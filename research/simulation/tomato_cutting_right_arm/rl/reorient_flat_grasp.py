"""Reuse mesh screens at other central knife yaws; solve bounded offline IK alternatives."""
import json
from pathlib import Path
import sys
import numpy as np
from pxr import Usd,UsdGeom
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
from reset_sampler import FlatResetSampler

base=json.loads((ROOT/'docs/rl/flat_grasp_geometry.json').read_text())
stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3.usda'))
meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
physics=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text())
mesh=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path'])).GetPointsAttr().Get())
handle=np.array(physics['handle_centre_local_m'])
sampler=FlatResetSampler(mesh,meta['board_world_bounds']);centre=np.mean(meta['board_world_bounds'],axis=0)[:2]
kin=ArmKinematics(stage);seed=np.array([physics['home_rad'][n] for n in kin.names])
old=Rotation.from_quat(base['reset']['pose_xyzw'][3:]).as_matrix()
results=[];attempts=[]
for yaw in [-67.5,67.5,-112.5]:
    reset=sampler.at(centre,np.deg2rad(yaw));assert reset['valid']
    kr=Rotation.from_quat(reset['pose_xyzw'][3:]).as_matrix();h=kr@handle+np.array(reset['pose_xyzw'][:3]);h[2]-=.003
    for c in base['candidates'][:12]:
        rotation=kr@old.T@np.array(c['hand_rotation_world']);target=h-rotation@(np.array(c['handle_in_hand_m'])-PALM_OFFSET)
        q,error,angle=kin.solve(target,rotation,seed)
        if error>.005 or angle>.04:
            q2,e2,a2=kin.solve(target,rotation,np.array(base['candidates'][6]['q_rad']))
            if e2+0.15*a2<error+0.15*angle:q,error,angle=q2,e2,a2
        case={**c,'reset':reset,'hand_rotation_world':rotation.tolist(),'palm_world_m':target.tolist(),
              'q_rad':q.tolist(),'ik_position_error_m':error,'ik_angle_error_rad':angle}
        attempts.append({'yaw_deg':yaw,'roll_deg':c['roll_deg'],'position_error_m':error,'rotation_error_rad':angle})
        if error<.005 and angle<.04:results.append(case)
    print('YAW',yaw,'reachable so far',len(results),flush=True)
results.sort(key=lambda c:c['cost'])
out={'reset':base['reset'],'candidates':results[:12],'ik_attempts':attempts,'scope':'Central flat mesh/IK alternatives; no physical validation'}
(ROOT/'docs/rl/flat_grasp_alternatives.json').write_text(json.dumps(out,indent=2))
print([(i,c['reset']['yaw_rad'],c['roll_deg'],c['finger_deg'],c['cost']) for i,c in enumerate(out['candidates'])])
