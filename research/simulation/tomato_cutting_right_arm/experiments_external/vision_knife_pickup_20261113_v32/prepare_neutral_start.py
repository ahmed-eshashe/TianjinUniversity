from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'scripts'));from reach_kinematics import ArmKinematics,PALM_OFFSET
c=json.load(open(W/'scene_config.json'));g=json.load(open(W/'reports/pinch_geometry02.json'));kin=ArmKinematics(Usd.Stage.Open(c['scene']));p=np.array(json.load(open(W/'runs/camera01/result.json'))['knife_pose']);K=np.eye(4);K[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();K[:3,3]=p[:3];H=K@np.array(g['hand_from_knife']);H[2,3]+=.045;N=H.copy();N[:3,3]=[.05,-.4,.24];q,pe,re=kin.solve(N[:3,3]+N[:3,:3]@PALM_OFFSET,N[:3,:3],g['q']);rows=[];seed=q.copy()
for u in np.linspace(0,1,61):
 target=N[:3,3]*(1-u)+H[:3,3]*u;seed,e,a=kin.solve(target+H[:3,:3]@PALM_OFFSET,H[:3,:3],seed);rows.append([float(u),e,a])
out=dict(scope='Fixed task start beside the board, independent of sampled knife pose. Not the original remote home pose.',arm_joint_names=kin.names,arm_joint_rad=q.tolist(),hand_root_world=N.tolist(),position_error_m=pe,orientation_error_rad=re,maximum_route_position_error_m=max(x[1] for x in rows),maximum_route_orientation_error_rad=max(x[2] for x in rows),route_samples=rows)
(W/'reports/neutral_start.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['route_samples','hand_root_world','arm_joint_names','arm_joint_rad']})
