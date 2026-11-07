"""Prospective physical continuation; no material state or damage modifications."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
from pxr import Usd

w = Path(__file__).parent
r = w.parents[1]
sys.path.insert(0, str(r / 'scripts'))
from reach_kinematics import ArmKinematics, PALM_OFFSET

source = w / 'clear_entry_robot_plan_v8.json'
route = json.loads(source.read_text())
plan = json.loads((r / 'work/backward_elbow_20261105/plan.json').read_text())
k = ArmKinematics(Usd.Stage.Open(plan['scene']))
k.upper[5] = .85
k.lower[6] = -.85
mount = np.asarray(plan['mount_hand_from_knife'])
F = np.asarray(route['target_rotation'])
cut = [p for p in route['rows'] if p['phase'] == 'cut']
parent_duration = abs(cut[-1]['tool_origin'][2] - cut[0]['tool_origin'][2]) / .02
for i, p in enumerate(cut):
    p['time_s'] = parent_duration * i / (len(cut) - 1)
q = np.asarray(cut[-1]['q'])
position = np.asarray(cut[-1]['tool_origin'])
rotation = np.asarray(cut[-1]['tool_rotation'])
hand_rotation = rotation @ mount[:3, :3].T
distance = .014
speed = .02
extra = []
for t in np.linspace(0, distance / speed, 141)[1:]:
    desired = position + F @ np.array([speed * t, 0, 0])
    previous = q.copy()
    q, pe, re = k.solve(desired - hand_rotation @ mount[:3, 3] + hand_rotation @ PALM_OFFSET, hand_rotation, q)
    if pe > 2e-5 or re > 2e-4 or np.max(abs(q - previous)) > .05:
        raise ValueError(('Continuation IK failed', pe, re, np.max(abs(q - previous))))
    extra.append(dict(phase='cut', q=q.tolist(), tool_origin=desired.tolist(), tool_rotation=rotation.tolist(), time_s=parent_duration+t, position_error=pe, angle_error=re))
route.update(rows=[p for p in route['rows'] if p['phase'] == 'entry'] + cut + extra,
    parent_duration_s=parent_duration, duration_s=parent_duration+distance/speed,
    parent_route=str(source), parent_route_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    transition_checkpoint=str(w/'robot_cut13/checkpoints/step_005375.npz'),
    purpose='Physical lateral blade continuation toward the deformed lower interface; no prescribed failure',
    lateral_distance_m=distance, lateral_speed_m_s=speed, fixed_blade_rotation=True,
    material_law_unchanged=True, kinematic_only=True, robot_dynamics_checked=False, full_slice=False)
(w/'lateral_continuation_plan_v1.json').write_text(json.dumps(route, indent=2))
print({k: v for k, v in route.items() if k != 'rows'})
