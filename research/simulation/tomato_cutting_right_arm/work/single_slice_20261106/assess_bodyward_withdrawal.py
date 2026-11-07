"""Read-only constant-height bodyward IK screen; no material state changes."""
from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
candidates=sorted((w/'robot_cut16/checkpoints').glob('step_*.json'))
cp=candidates[-1] if candidates else w/'robot_cut15/checkpoints/step_005425.json'
m=json.loads(cp.read_text());p=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());names=json.loads((w/'robot_cut16/runtime_joint_limits.json').read_text())['names'];k=ArmKinematics(Usd.Stage.Open(p['scene']));k.upper[5]=.85;k.lower[6]=-.85;mount=np.array(p['mount_hand_from_knife']);q=np.array([m['robot_state']['q'][names.index(n)] for n in k.names]);P=np.array(m['robot_state']['tool_pose'][:3]);R=Rotation.from_quat(m['robot_state']['tool_pose'][3:]).as_matrix();root=np.array(p['robot_root_world_matrix']);direction=root[:3,3]-P;direction[2]=0;direction/=np.linalg.norm(direction);H=R@mount[:3,:3].T;rows=[];failure=None
for distance in np.linspace(0,.12,241):
 target=P+direction*distance;new,pe,re=k.solve(target-H@mount[:3,3]+H@PALM_OFFSET,H,q)
 if pe>2e-5 or re>2e-4 or np.max(abs(new-q))>.05:
  failure={'distance_m':float(distance),'position_error_m':float(pe),'rotation_error_rad':float(re),'maximum_joint_change_rad':float(np.max(abs(new-q)))};break
 rows.append({'distance_m':float(distance),'q':new.tolist(),'tool_origin':target.tolist(),'tool_rotation':R.tolist()});q=new
report={'checkpoint':str(cp),'direction_world':direction.tolist(),'height_change_m':0,'scope':'Kinematics only; no collision, material or native dynamic pass','requested_distance_m':.12,'reachable_distance_m':rows[-1]['distance_m'] if rows else 0,'failure':failure,'rows':rows}
(w/'bodyward_withdrawal_screen.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='rows'})
