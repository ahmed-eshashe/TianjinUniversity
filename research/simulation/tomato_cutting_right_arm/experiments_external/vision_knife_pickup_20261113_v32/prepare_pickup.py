from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,Gf
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from reach_kinematics import ArmKinematics,PALM_OFFSET
c=json.loads((W/'scene_config.json').read_text());old=Usd.Stage.Open(str(R/'rl/scene/phase3_grasp.usda'));ok=ArmKinematics(old);sample=json.loads((R/'runs/rl/phase3/central_grasp_13/before_lift.json').read_text());h=ok.transforms(sample['q_rad'][:7])[ok.hand_path];p=np.array(sample['knife_pose_xyzw']);K=np.eye(4);K[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();K[:3,3]=p[:3];relative=np.linalg.inv(K)@h
s=Usd.Stage.Open(c['scene']);kin=ArmKinematics(s);settled=json.loads((W/'runs/camera01/result.json').read_text());p=np.array(settled['knife_pose']);K=np.eye(4);K[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();K[:3,3]=p[:3]
rows=[];seed=np.array([c['home_rad'][n] for n in kin.names])
for offset in [0.,-.025,-.045]:
 rel=relative.copy();rel[0,3]+=offset;T=K@rel
 q,pe,re=kin.solve(T[:3,3]+T[:3,:3]@PALM_OFFSET,T[:3,:3],seed)
 rows.append(dict(handle_axis_shift_m=offset,hand_from_knife=rel.tolist(),q=q.tolist(),position_error_m=pe,angle_error_rad=re,hand_position_world=T[:3,3].tolist()))
(W/'reports/initial_grasp_reach.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
