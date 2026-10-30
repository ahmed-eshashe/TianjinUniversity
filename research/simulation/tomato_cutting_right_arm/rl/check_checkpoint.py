"""Independently load a trusted resource-probe checkpoint on CPU, without Kit."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from probe_policy import ProbePolicy, VisionProxy


def main():
    p=argparse.ArgumentParser();p.add_argument('checkpoint',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    torch.set_num_threads(1)
    payload=torch.load(a.checkpoint,map_location='cpu',weights_only=False)
    c=payload['config'];policy=ProbePolicy(c['observation_size'],c['action_size'])
    policy.load_state_dict(payload['policy'])
    optimizer=torch.optim.Adam(policy.parameters(),lr=3e-4);optimizer.load_state_dict(payload['optimizer'])
    with torch.no_grad():
        action,logp,value,entropy=policy.evaluate(torch.zeros(c['observation_size']))
    checks={'actor_finite':bool(torch.isfinite(action).all() and torch.isfinite(logp) and torch.isfinite(value) and torch.isfinite(entropy)),
            'optimizer_state_present':bool(optimizer.state),
            'optimizer_state_finite':all(bool(torch.isfinite(v).all()) for s in optimizer.state.values() for v in s.values() if isinstance(v,torch.Tensor)),
            'normalization_present':payload['normalization']['count']>0 and np.isfinite(payload['normalization']['mean']).all() and np.isfinite(payload['normalization']['m2']).all(),
            'rng_complete':set(payload['rng'])=={'python','numpy','torch','cuda','reset_generator'},
            'resource_probe_only':payload['curriculum']['stage']=='resource_probe_only' and not payload['curriculum']['grasp_training']}
    if c['camera']:
        vision=VisionProxy();vision.load_state_dict(payload['vision_proxy'])
        with torch.no_grad():features=vision(torch.zeros(1,4,c['width'],c['width']))
        checks['encoder_loads_and_is_finite']=bool(features.shape==(1,16) and torch.isfinite(features).all())
    checks={k:bool(v) for k,v in checks.items()}
    report={'passed':all(checks.values()),'checkpoint':str(a.checkpoint.resolve()),'device':'cpu','checks':checks,
            'counters':payload['counters'],'normalization_count':payload['normalization']['count'],
            'scope':'Independent deserialisation/inference check. No simulator, GPU allocation, hardware action or training.'}
    a.output.write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
