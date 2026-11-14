"""Train only from successful physical demonstrations; keep evaluation split separate.

An offline loss is not a closed-loop pickup pass. Run physical evaluation with
the saved image actor before claiming learned pickup.
"""
from pathlib import Path
import argparse
import hashlib
import json
import random
import time
import numpy as np
import torch
from vision_policy import VisionPickupPolicy, image_tensor

W = Path(__file__).resolve().parent
a = argparse.ArgumentParser()
a.add_argument('--dataset', type=Path, required=True)
a.add_argument('--output', type=Path, required=True)
a.add_argument('--epochs', type=int, default=80)
a.add_argument('--device', default='cuda')
args = a.parse_args()
assert not args.output.exists(), 'Preserve previous checkpoints and reports'
args.output.mkdir(parents=True)
(args.output/'training_source.py').write_text(Path(__file__).read_text())
(args.output/'vision_policy.py').write_text((W/'vision_policy.py').read_text())
(args.output/'configuration.json').write_text(json.dumps({k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},indent=2))
torch.manual_seed(20261113)
np.random.seed(20261113)
random.seed(20261113)
torch.set_num_threads(4)
torch.set_float32_matmul_precision('high')
episodes = []
excluded = []
for p in sorted(args.dataset.glob('*/demonstration.npz')):
    if not (p.parent / 'demonstration_metadata.json').exists():
        continue
    meta = json.loads((p.parent / 'demonstration_metadata.json').read_text())
    result = json.loads((p.parent / 'result.json').read_text()) if (p.parent / 'result.json').exists() else {}
    if not meta['success'] or not result.get('success'):
        excluded.append(str(p))
        continue
    if p.parent.name.startswith('test_'):
        continue
    data = dict(np.load(p))
    assert set(data) == {'rgb', 'depth', 'q', 'qd', 'previous_target', 'target', 'sim_s'}
    # The renderer's first post-reset frame can retain the authored object pose.
    # Keep original recordings, but learn only from the settled, refreshed view.
    keep = data['sim_s'] >= .5 - 1e-8
    data = {k:v[keep] for k,v in data.items()}
    assert np.allclose(np.diff(data['sim_s']), .05, atol=1e-7)
    assert np.allclose(data['previous_target'][1:], data['target'][:-1])
    action = data['target'] - data['previous_target']
    bounds = np.array([.04] * 7 + [.02] * 6)
    if (np.abs(action) > bounds + 1e-6).any():
        excluded.append(str(p) + ': action outside student limits')
        continue
    data['action'] = action
    data['previous_action'] = np.concatenate([np.zeros_like(action[:1]), action[:-1]])
    data['split'] = 'validation' if p.parent.name.startswith('validation_') else 'train'
    data['path'] = str(p)
    episodes.append(data)
train = [x for x in episodes if x['split'] == 'train']
validation = [x for x in episodes if x['split'] == 'validation']
assert len(train) >= 6 and len(validation) >= 2, 'Require multiple successful training and validation placements'
q = np.concatenate([x['q'] for x in train])
mean = q.mean(0)
scale = np.maximum(q.std(0), .03)
model = VisionPickupPolicy(mean, scale).to(args.device)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
provenance = dict(training=[x['path'] for x in train], validation=[x['path'] for x in validation],
                  excluded=excluded, test_episodes_used=False, source_sha256=hashlib.sha256((W/'vision_policy.py').read_bytes()).hexdigest(),
                  actor_inputs=['current RGB-D', 'initial RGB-D memory', 'q', 'qd', 'joint command memory', 'previous action'],
                  preprocessing='Discard startup frames before 0.5 simulated second. Use settled head image as initial visual memory; initial renderer pose lag was independently observed.',
                  success_claim='None: offline training only. Fresh closed-loop physical evaluation required.')
(args.output / 'provenance.json').write_text(json.dumps(provenance, indent=2))
best = float('inf')
history = []
start = time.monotonic()
for epoch in range(args.epochs):
    model.train()
    random.shuffle(train)
    metrics = {}
    for split, items in [('train', train), ('validation', validation)]:
        losses = []
        model.train(split == 'train')
        for episode in items:
            # Full sequences preserve recurrent timing through handle occlusion.
            with torch.set_grad_enabled(split == 'train'):
                images = image_tensor(episode['rgb'], episode['depth'], args.device)[None]
                qv = torch.tensor(episode['q'], device=args.device)[None]
                qd = torch.tensor(episode['qd'], device=args.device)[None]
                targets = torch.tensor(episode['previous_target'], device=args.device)[None]
                prev = torch.tensor(episode['previous_action'], device=args.device)[None]
                truth = torch.tensor(episode['action'], device=args.device)[None] / model.action_scale
                if split == 'train':
                    # Sensor/command noise teaches small corrections, without object-state input.
                    noise = torch.randn_like(targets) * .0005
                    targets = targets + noise
                    truth = truth - noise / model.action_scale
                    qv = qv + torch.randn_like(qv) * .0005
                    gain = .9 + torch.rand((), device=args.device) * .2
                    images[:, :, :3] = (images[:, :, :3] * gain).clamp(0., 1.)
                with torch.autocast('cuda', dtype=torch.bfloat16, enabled=args.device.startswith('cuda')):
                    prediction, goal, _ = model(images, images[:, 0], qv, qd, targets, prev)
                contact_index = np.argmin(abs(episode['sim_s'] - 6.5))
                contact_q = torch.tensor(episode['q'][contact_index, :7], device=args.device)
                goal_truth = (contact_q - model.mean[:7]) / model.scale[:7]
                action_loss = (prediction - truth).square().mean()
                loss = action_loss + .05 * (goal - goal_truth).square().mean()
                if split == 'train':
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
                    optimizer.step()
                losses.append(float(action_loss.detach()))
        metrics[split] = float(np.mean(losses))
    row = dict(epoch=epoch, **metrics, wall_s=time.monotonic()-start)
    history.append(row)
    print(json.dumps(row), flush=True)
    (args.output/'progress.json').write_text(json.dumps(row))
    if metrics['validation'] < best:
        best = metrics['validation']
        torch.save(dict(state_dict=model.state_dict(), mean=mean.tolist(), scale=scale.tolist(),
                        epoch=epoch, metrics=metrics, provenance=provenance), args.output/'best.pt')
(args.output/'history.json').write_text(json.dumps(history, indent=2))
