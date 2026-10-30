"""A bounded positions-only continuation guess, never physical history.

Predict the bulk field from two accepted states instead of projecting only the
surface of the previous state onto the next blade. Damage and the physical work
ledger still start at the actual previous checkpoint in the evolving worker.
"""
import argparse,fcntl,hashlib,json,resource,signal,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--previous',type=Path,required=True);p.add_argument('--depth-mm',type=float,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
        def read(folder):
            s=json.loads((folder/'summary.json').read_text());assert s['passed'] and s['backend'] in ('triangle_evolving_v1','triangle_search_evolving_v1')
            for n,h in s['source_hashes'].items():assert digest(ROOT/n)==h
            for n,h in s['state_hashes'].items():assert digest(folder/n)==h
            return s,np.load(folder/'positions.npy')
        previous=a.previous.resolve();s,x=read(previous)
        if not s['previous_checkpoint']:raise ValueError('Two verified states are required')
        older=ROOT/s['previous_checkpoint'];old,y=read(older)
        while old['depth_mm']==s['depth_mm']:
            older=ROOT/old['previous_checkpoint'];old,y=read(older)
        increment=s['depth_mm']-old['depth_mm'];step=a.depth_mm-s['depth_mm']
        if not 0<increment<=.25000001 or not 0<step<=.25000001:raise ValueError('Only nearby forward insertion guesses are supported')
        # A bounded numerical guess only. This displacement cap is not a
        # material property, physical action clamp or acceptance tolerance.
        ratio=min(step/increment,2.);prediction=ratio*(x-y);maximum=float(np.max(np.linalg.norm(prediction,axis=1)))
        if maximum>.001:prediction*=.001/maximum
        guess=x+prediction
        assert np.isfinite(guess).all() and guess.shape==x.shape
        a.output.mkdir(parents=True,exist_ok=False);np.save(a.output/'guess.npy',guess)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        report={'passed':False,'optimization_only':True,'reason':'positions_only_secant_predictor','depth_mm':a.depth_mm,
            'previous_summary_sha256':digest(previous/'summary.json'),'guess_sha256':digest(a.output/'guess.npy'),
            'trial_damage_states':s['damage_states'],'optimizer_active_rows':None,'source_hashes':s['source_hashes'],
            'prediction_source_hashes':{str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},
            'previous_checkpoint':str(previous.relative_to(ROOT)),'older_checkpoint':str(older.relative_to(ROOT)),
            'older_summary_sha256':digest(older/'summary.json'),'requested_step_ratio':step/increment,'used_step_ratio':ratio,
            'maximum_predicted_displacement_m':float(np.max(np.linalg.norm(prediction,axis=1))),
            'damage_predicted':False,'work_predicted':False,'physical_trajectory_advanced':False,'forbidden_imports':forbidden,
            'runtime_s':time.monotonic()-start,'simulator':False,'training':False}
        (a.output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['trial_damage_states','source_hashes','prediction_source_hashes']},flush=True)
if __name__=='__main__':main()
