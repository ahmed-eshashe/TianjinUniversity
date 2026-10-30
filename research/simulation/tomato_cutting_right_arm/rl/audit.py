"""Offline Phase 1 inventory; does not connect to or command hardware."""
import hashlib
import importlib.metadata as metadata
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/rl'
SOURCE = ROOT / 'assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stage = Usd.Stage.Open(str(ROOT / 'work/kitchen_reach.usda'))
    robot = stage.GetPrimAtPath('/dual_ar5_o6')
    joints = []
    for prim in Usd.PrimRange(robot):
        if not prim.IsA(UsdPhysics.RevoluteJoint):
            continue
        joint = UsdPhysics.RevoluteJoint(prim)
        drive = UsdPhysics.DriveAPI(prim, 'angular')
        joints.append({
            'name': prim.GetName(), 'path': str(prim.GetPath()),
            'limits_rad': np.deg2rad([joint.GetLowerLimitAttr().Get(), joint.GetUpperLimitAttr().Get()]).tolist(),
            'axis': joint.GetAxisAttr().Get(),
            'body0': [str(x) for x in joint.GetBody0Rel().GetTargets()],
            'body1': [str(x) for x in joint.GetBody1Rel().GetTargets()],
            'simulation_drive': {'type': drive.GetTypeAttr().Get(), 'stiffness': drive.GetStiffnessAttr().Get(),
                                 'damping': drive.GetDampingAttr().Get(), 'max_force': drive.GetMaxForceAttr().Get()},
            'mimic_relationships': {r.GetName(): [str(x) for x in r.GetTargets()] for r in prim.GetRelationships() if 'mimic' in r.GetName().lower()},
            'mimic_attributes': {a.GetName(): str(a.Get()) for a in prim.GetAttributes() if 'mimic' in a.GetName().lower()},
            'physical_limits_verified': False,
        })
    urdf_path = ROOT / 'ros2_ws/src/ar5_o6_right_description/urdf/dual_ar5_o6.urdf'
    urdf = []
    for j in ET.parse(urdf_path).getroot().findall('joint'):
        limit = j.find('limit')
        if limit is not None:
            urdf.append({'name': j.attrib['name'], 'limits': limit.attrib,
                         'mimic': j.find('mimic').attrib if j.find('mimic') is not None else None})
    versions = {}
    for name in ['isaacsim', 'isaacsim-core', 'isaaclab', 'isaaclab-rl', 'torch', 'torchvision', 'numpy', 'gymnasium', 'rsl-rl-lib', 'rl-games', 'skrl', 'stable-baselines3']:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    import torch
    versions.update(python=sys.version, cuda_build=torch.version.cuda,
                    cuda_available=torch.cuda.is_available(), gpu=torch.cuda.get_device_name(0),
                    torch_architectures=torch.cuda.get_arch_list(),
                    isaaclab_source_VERSION=Path('/home/omen/IsaacLab/VERSION').read_text().strip(),
                    isaaclab_source_commit=subprocess.check_output(['git', '-C', '/home/omen/IsaacLab', 'rev-parse', 'HEAD'], text=True).strip())
    baseline_paths = ['run_kitchen_grasp.sh', 'scripts/guarded_grasp.py', 'work/validated_grasp_configuration.json',
                      'logs/kitchen_grasp_validation_report.json', 'logs/kitchen_grasp_gui_validation_report.json']
    bbox = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'render']).ComputeWorldBound(robot).ComputeAlignedRange()
    audit = {
        'scope': 'Offline model/software audit, no physical connection or hardware commands',
        'versions': versions, 'platform': platform.platform(),
        'gpu_driver': subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'], text=True).strip(),
        'source': str(SOURCE), 'source_sha256': digest(SOURCE),
        'baseline_sha256': {p: digest(ROOT / p) for p in baseline_paths if (ROOT / p).exists()},
        'joints': joints, 'urdf_inventory': urdf,
        'robot_world_visual_bounds_m': [list(bbox.GetMin()), list(bbox.GetMax())],
        'rigid_body_count': sum(p.HasAPI(UsdPhysics.RigidBodyAPI) for p in Usd.PrimRange(robot)),
        'sensor_prims': [str(p.GetPath()) for p in Usd.PrimRange(robot) if 'sensor' in p.GetTypeName().lower()],
        'right_arm_independent': [x['name'] for x in joints if x['name'].startswith('right_AR5')],
        'right_hand_independent': [x['name'] for x in joints if x['name'].startswith('right_rh_') and not x['mimic_relationships']],
        'right_hand_followers': [x for x in joints if x['name'].startswith('right_rh_') and x['mimic_relationships']],
        'hardware_status': 'NOT VERIFIED: same models confirmed by user; live encoders, calibration, firmware, tactile, force/current interfaces and certified limits remain unverified',
        'compatibility': 'CUDA tensor operation and Phase 2 runtime probes required; distribution isaaclab 19.0.0 and source VERSION 3.0.0 recorded separately; no upgrade performed',
        'references': ['https://github.com/linker-bot/linkerhand-python-sdk', 'https://github.com/linker-bot/linkerhand-ros2-sdk'],
    }
    (OUT / 'phase1_inventory.json').write_text(json.dumps(audit, indent=2))
    contract = {
        'status': 'Simulation interface specified; physical deployment blocked pending verification',
        'frames': {'world': 'metres, Z up', 'robot': 'authored robot root', 'camera': 'USD optical -Z forward, +Y up; convert explicitly to ROS optical +Z forward, +Y down'},
        'joint_units': 'radians and radians/second; USD drive positions are authored in degrees',
        'actor_inputs': {'q_independent': {'size': 13, 'source': 'simulator joint state; physical encoder mapping unverified'},
                         'qd_independent': {'size': 13, 'source': 'simulator joint state; physical velocity feedback unverified'},
                         'previous_action': {'size': 12, 'source': 'controller history'},
                         'handle_pose_confidence': {'size': 8, 'source': 'future RGB-D perception: xyz + quaternion wxyz + confidence'},
                         'image_age_seconds': {'size': 1, 'source': 'camera timestamp'}},
        'actor_exclusions': ['ground-truth knife pose', 'simulated contact identities/forces', 'tactile', 'wrist wrench', 'motor current or torque'],
        'teacher_critic_only': ['ground-truth object pose/velocity', 'simulator contacts'],
        'proposed_task_action': {'size': 12, 'order': ['palm dx', 'palm dy', 'palm dz', 'palm dRx', 'palm dRy', 'palm dRz',
                                                               'thumb flexion', 'thumb opposition', 'index', 'middle', 'ring', 'pinky'],
                                 'initial_rate_hz': 20, 'translation_limit_m_per_step': .002,
                                 'rotation_limit_rad_per_step': .02, 'finger_limit_rad_per_step': .01,
                                 'status': 'provisional simulation limits, not hardware calibration'},
        'benchmark_action': {'size': 13, 'type': 'bounded independent-joint offsets around fixed ready posture; resource probe only',
                             'joint_offset_limit_rad': .015, 'target_slew_rad_per_step': .002,
                             'action_hz': 20, 'physics_hz': 240},
        'independent_joint_order': audit['right_arm_independent'] + audit['right_hand_independent'],
        'hardware_hand_order': ['thumb flexion', 'thumb opposition', 'index', 'middle', 'ring', 'pinky'],
        'hardware_mapping_notes': 'Vendor O6 six-channel order differs from authored yaw/pitch traversal. Named mapping and sign/range calibration required before hardware use; URDF effort declarations are not proof of available torque control.',
        'fallbacks': {'stale_image': 'hold bounded targets, stop if age exceeds future validated threshold',
                      'missing_joint_feedback': 'stop; do not substitute zeros', 'missing_tactile': 'excluded by design'},
        'physical_deployment_inputs_confirmed': [],
    }
    (OUT / 'interface_contract.json').write_text(json.dumps(contract, indent=2))
    # A real CUDA operation tests the installed wheel on this GPU without starting Kit.
    z = torch.randn(32, 32, device='cuda'); value = (z @ z.T).sum(); torch.cuda.synchronize()
    assert torch.isfinite(value)
    (OUT / 'cuda_smoke.json').write_text(json.dumps({'passed': True, 'value_finite': True, 'device': torch.cuda.get_device_name(0)}, indent=2))
    assert len(joints) == 36 and len(audit['right_arm_independent']) == 7 and len(audit['right_hand_independent']) == 6
    print(json.dumps({'joint_count': len(joints), 'independent_right': 13, 'followers_right': 5, 'cuda_smoke': True, 'output': str(OUT)}))


if __name__ == '__main__':
    main()
