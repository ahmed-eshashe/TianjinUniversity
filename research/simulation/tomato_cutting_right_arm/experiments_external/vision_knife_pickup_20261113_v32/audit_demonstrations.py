"""Independent checks on stored observations/actions and physical result provenance."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np

a = argparse.ArgumentParser()
a.add_argument('dataset', type=Path)
args = a.parse_args()
rows = []
for folder in sorted(p for p in args.dataset.iterdir() if p.is_dir()):
    if not (folder / 'demonstration.npz').exists() or not (folder / 'demonstration_metadata.json').exists():
        continue
    raw = dict(np.load(folder / 'demonstration.npz'))
    keep = raw['sim_s'] >= .5 - 1e-8
    d = {k:v[keep] for k,v in raw.items()}
    result = json.loads((folder / 'result.json').read_text()) if (folder / 'result.json').exists() else {}
    reset = json.loads((folder / 'reset_audit.json').read_text()) if (folder / 'reset_audit.json').exists() else {}
    action = d['target'] - d['previous_target']
    state_ok = all(np.isfinite(d[k]).all() for k in ['q', 'qd', 'target', 'previous_target'])
    continuity = float(np.abs(d['previous_target'][1:] - d['target'][:-1]).max())
    bounds = np.array([.04] * 7 + [.02] * 6)
    action_ok = bool((np.abs(action) <= bounds + 1e-6).all())
    depth_valid = float(np.isfinite(d['depth']).mean())
    temporal_ok = bool(np.allclose(np.diff(d['sim_s']), .05, atol=1e-7))
    allowed = set(d) == {'sim_s', 'rgb', 'depth', 'q', 'qd', 'target', 'previous_target'}
    reset_ok = bool(reset and np.linalg.norm(np.array(reset['actual'][:3])-reset['requested'][:3]) < 1e-6)
    passed = bool(result.get('success')) and state_ok and temporal_ok and action_ok and continuity < 1e-6 and allowed and reset_ok
    rows.append(dict(episode=folder.name, physical_success=bool(result.get('success')), eligible_for_imitation=passed,
                     frames=len(action), startup_frames_discarded=int((~keep).sum()), state_finite=state_ok, temporal_ok=temporal_ok, action_bounds_ok=action_ok,
                     target_continuity_error=continuity, allowed_observation_fields=allowed, reset_pose_checked=reset_ok,
                     max_arm_action_rad=float(np.abs(action[:, :7]).max()), max_hand_action_rad=float(np.abs(action[:, 7:]).max()),
                     depth_finite_fraction=depth_valid, source_sha256=hashlib.sha256((folder/'source.py').read_bytes()).hexdigest()))
report = dict(episodes=rows, eligible=sum(x['eligible_for_imitation'] for x in rows), total=len(rows),
              preprocessing='Discard frames before 0.5 simulated second to avoid stale initial post-reset rendering. Raw recordings preserved.',
              limitation='Eligibility is not proof of learned policy success, force calibration, or held-out robustness.')
(args.dataset/'audit.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
