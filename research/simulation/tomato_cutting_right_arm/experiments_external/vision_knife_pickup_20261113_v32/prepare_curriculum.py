"""Freeze small first-curriculum splits before collecting training trajectories.

Geometry/reach screening is not a physical pickup pass. Expansion to other
resting poses and original long knives remains explicitly unqualified.
"""
from pathlib import Path
import json
import sys
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd, UsdGeom

W = Path(__file__).resolve().parent
R = Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
sys.path.insert(0, str(R / 'scripts'))
from reach_kinematics import ArmKinematics, PALM_OFFSET

c = json.loads((W / 'scene_config.json').read_text())
g = json.loads((W / 'reports/pinch_geometry02.json').read_text())
stage = Usd.Stage.Open(str(W / 'knife_short_blade_v02.usda'))
kin = ArmKinematics(stage)
vertices = np.array(UsdGeom.Mesh(stage.GetPrimAtPath(c['knife_path'])).GetPointsAttr().Get())
pose = np.array(json.loads((W / 'runs/camera01/result.json').read_text())['knife_pose'])
R0 = Rotation.from_quat(pose[3:]).as_matrix()
handle = np.array([-.0860033812, .0076461609, .001586524])
centre = pose[:3] + R0 @ handle
board_lo, board_hi = np.array(c['board_world_bounds'])
rng = np.random.default_rng(20261113)
rows = []
for split, number in [('train', 24), ('validation', 6), ('test', 8)]:
    attempts = 0
    while sum(x['split'] == split for x in rows) < number:
        attempts += 1
        if attempts > 1000:
            raise RuntimeError('Insufficient feasible candidates')
        dx = float(rng.uniform(-.045, .045))
        dy = float(rng.uniform(-.065, -.008))
        yaw = float(rng.uniform(-14., 14.))
        rot = Rotation.from_euler('z', yaw, degrees=True).as_matrix() @ R0
        K = np.eye(4)
        K[:3, :3] = rot
        K[:3, 3] = centre - rot @ handle + [dx, dy, 0.]
        points = vertices @ rot.T + K[:3, 3]
        margins = np.minimum(points[:, :2].min(0) - board_lo[:2], board_hi[:2] - points[:, :2].max(0))
        if margins.min() < .005:
            continue
        target = K @ np.array(g['hand_from_knife'])
        seed = g['q']
        errors = []
        for dz in [0., .045, .12]:
            p = target[:3, 3] + [0., 0., dz]
            seed, pe, re = kin.solve(p + target[:3, :3] @ PALM_OFFSET, target[:3, :3], seed)
            errors.append([pe, re])
        if max(x[0] for x in errors) > .0003 or max(x[1] for x in errors) > .003:
            continue
        rows.append(dict(id=f'{split}_{sum(x["split"] == split for x in rows):03}', split=split,
                         scene='knife_short_blade_v02.usda', dx=dx, dy=dy, yaw_deg=yaw,
                         board_aabb_margin_m=float(margins.min()), ik_errors=errors))

destination = W / 'curriculum_split_v01.json'
assert not destination.exists(), 'Preserve the frozen evaluation split'
destination.write_text(json.dumps(dict(seed=20261113, scope='Initial short-knife flat-rest curriculum only; no broad geometry/rest-pose generalization claim.',
                                      test_rule='Do not train or select controller settings using test episodes; validation may inform development.',
                                      screening='Board AABB and endpoint IK only; continuous physical contact/collision verification still required.',
                                      episodes=rows), indent=2) + '\n')
print('Frozen', len(rows), 'episode placements:', destination)
