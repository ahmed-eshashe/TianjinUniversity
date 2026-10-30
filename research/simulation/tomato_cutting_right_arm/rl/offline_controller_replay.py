"""Recompute rolling-command diagnostics from stored states, without simulation.

The replay checks intermediate versus commanded contact motion; it does not
integrate dynamics, reconstruct a contact manifold, or infer physical causality.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from pxr import Usd
from scipy.spatial.transform import Rotation

from offline_grasp_audit import ROOT, hashes
from plan_contact_seating import HandGeometry
from rolling_contact_control import project_contact_motion
from contact_path_control import balanced_contact_goals, synchronized_increment
from in_place_motion import relative_command_pose
from reach_kinematics import PALM_OFFSET


def point_motion(model, start, end, anchors, knife_rotation):
    """Full nonlinear FK motion at the SAME body material points, world-to-knife."""
    def points(q):
        root = model.kin.transforms(q[:7])[model.root]
        links = model.transforms(q[7:])
        return np.array([root[:3, 3] + root[:3, :3] @
                         (links[a['body']][:3, 3] + links[a['body']][:3, :3] @ a['local'])
                         for a in anchors])
    return (points(end) - points(start)) @ knife_rotation


def replay(stage, model, records, plan, control):
    i = next(i for i, x in enumerate(records) if x['control_step'] == control)
    sample, following = records[i:i+2]
    first = next(i for i, x in enumerate(records) if x['phase'] == 'contact_preserving_seating')
    refpose = np.array(records[first - 1]['knife_pose_xyzw'])
    refr = Rotation.from_quat(refpose[3:]).as_matrix()
    pose = np.array(sample['knife_pose_xyzw']); kr = Rotation.from_quat(pose[3:]).as_matrix()
    actual = np.array(sample['q_rad']); command = np.array(sample['command_q_rad'])
    root = model.kin.transforms(actual[:7])[model.root]
    r = kr.T @ root[:3, :3]; t = kr.T @ (root[:3, 3] - pose[:3])
    handq = actual[7:]; links = model.transforms(handq); anchors = []
    for part in ['thumb', 'index', 'middle', 'ring', 'pinky']:
        contacts = [c for c in sample['contacts'] if c['part'] == part and c['on_handle'] and c['force_n'] > .3]
        if not contacts:
            continue
        c = max(contacts, key=lambda c: c['force_n']); link = links[c['body']]
        br = root[:3, :3] @ link[:3, :3]; bp = root[:3, 3] + root[:3, :3] @ link[:3, 3]
        local = br.T @ (np.array(c['point_world_m']) - bp)
        anchors.append({'body': c['body'], 'local': local, 'point_world': np.array(c['point_world_m'])})
    def points(z):
        rr = Rotation.from_rotvec(z[3:6]).as_matrix() @ r
        tr = model.transforms(handq + z[6:])
        return np.concatenate([t + z[:3] + rr @ (tr[a['body']][:3, 3] + tr[a['body']][:3, :3] @ a['local'])
                               for a in anchors])
    zero = np.zeros(12); base = points(zero); jac = []
    for j in range(12):
        z = zero.copy(); eps = 1e-5 if j < 3 else 1e-4; z[j] = eps
        jac.append((points(z) - base) / eps)
    jac = np.array(jac).T
    goal = plan['target']
    goalr = Rotation.from_quat(plan['reference_sample']['knife_pose_xyzw'][3:]).as_matrix().T @ np.array(goal['hand_rotation_world'])
    # Native evaluator uses raw knife-local handle points; no stage mutation.
    from pxr import UsdGeom
    meta = json.loads((ROOT / 'rl/scene/manifest.json').read_text())
    v = np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path'] + '/CollisionHandle')).GetPointsAttr().Get())
    centre = (v.min(0) + v.max(0)) / 2
    goalt = centre - goalr @ np.array(goal['handle_in_hand_m'])
    initial = records[first - 1]
    ir = model.kin.transforms(initial['q_rad'][:7])[model.root]
    ip = np.array(initial['knife_pose_xyzw']); ikr = Rotation.from_quat(ip[3:]).as_matrix()
    it = ikr.T @ (ir[:3, 3] - ip[:3])
    distance = np.linalg.norm(goalt - t)
    fraction = float(np.clip(1 - distance / max(np.linalg.norm(goalt - it), .001), 0, 1))
    qgoal = np.deg2rad([goal['thumb_yaw_deg'], goal['thumb_pitch_deg'], 70,
                       52.5 + 17.5 * np.clip((fraction - .3) / .7, 0, 1), 70, 85])
    delta = project_contact_motion(jac, np.r_[goalt - t, Rotation.from_matrix(goalr @ r.T).as_rotvec(), qgoal - handq],
                                   [.00015] * 3 + [.001] * 9)
    nextq = handq + delta[6:]; nr = Rotation.from_rotvec(delta[3:6]).as_matrix() @ r; nt = t + delta[:3]
    target = refr @ (nt + nr @ PALM_OFFSET) + refpose[:3]; orientation = refr @ nr
    actualp, actualr = model.kin.pose(actual[:7]); commandp, commandr = model.kin.pose(command[:7])
    solvep, solver = relative_command_pose(actualp, actualr, commandp, commandr, target, orientation)
    arm, pe, re = model.kin.solve(solvep, solver, command[:7])
    held = command[7:] - handq
    adjusted = np.clip(balanced_contact_goals(sample, nextq + held, nextq + held, 3.),
                       0, [.90, .38, *[np.deg2rad(85)] * 4])
    desired = np.r_[arm, adjusted]
    increment = synchronized_increment(desired - command, [.001] * 7 + [.003] * 6)
    # Measure both exact saved targets and offline reproduction: recorded targets
    # are authoritative and do not depend on tiny FK/solver reconstruction errors.
    saved_next_command = np.array(following['command_q_rad'])
    saved_desired = np.array(following['desired_q_rad'])
    raw_hand_delta = delta.copy()
    raw_hand_delta[6:] = adjusted - command[7:]
    actual_motion = point_motion(model, actual, following['q_rad'], anchors, kr)
    target_motion = point_motion(model, command, saved_next_command, anchors, kr)
    ideal_motion = (points(delta) - base).reshape(-1, 3)
    adjusted_motion = (points(raw_hand_delta) - base).reshape(-1, 3)
    # Frame error is the exact transform discrepancy from interpreting a newly
    # current-object point using the fixed reference-object transform.
    frame_errors = []
    for a in anchors:
        current_local = kr.T @ (a['point_world'] - pose[:3])
        frame_errors.append(float(np.linalg.norm(refr @ current_local + refpose[:3] - a['point_world'])))
    def norms(m): return [float(x) for x in np.linalg.norm(m, axis=1)]
    return {'control': control, 'anchor_bodies': [a['body'] for a in anchors],
            'projected_linear_residual_m': float(np.linalg.norm(jac @ delta)),
            'projected_nonlinear_point_motion_m': norms(ideal_motion),
            'after_pressure_correction_point_motion_m': norms(adjusted_motion),
            'saved_command_point_motion_m': norms(target_motion),
            'measured_joint_fk_material_point_motion_m': norms(actual_motion),
            'frame_reinterpretation_error_m': frame_errors,
            'offline_desired_vs_saved_max_joint_error_rad': float(np.max(abs(desired - saved_desired))),
            'offline_next_target_vs_saved_max_joint_error_rad': float(np.max(abs(command + increment - saved_next_command))),
            'ik_position_error_m': pe, 'ik_rotation_error_rad': re,
            'middle_goal_deg': float(np.rad2deg(qgoal[3])),
            'caveat': 'Point norms are per control interval, not velocities or contact slip. Material points need not remain active contacts. Target FK is commanded geometry, not physical pose.'}


if __name__ == '__main__':
    before = hashes()
    model_stage = Usd.Stage.Open(str(ROOT / 'rl/scene/phase3_grasp.usda'))
    model = HandGeometry(model_stage)
    folder = ROOT / 'runs/rl/phase3/contact_transfer_05'
    records = json.loads((folder / 'trajectory.json').read_text())
    plan = json.loads((folder / 'source_snapshot/docs/rl/contact_seating_plan.json').read_text())
    results = [replay(model_stage, model, records, plan, n) for n in [661, 701, 751, 761]]
    if hashes() != before:
        raise RuntimeError('Protected files changed')
    path = ROOT / 'docs/rl/offline_controller_replay.json'
    out = {'scope': 'Offline forward-kinematic replay of existing run 05; no simulator or dynamics',
           'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'protected_hashes': before, 'cases': results}
    path.write_text(json.dumps(out, indent=2, allow_nan=False))
    print(json.dumps(out['cases'], indent=2))
