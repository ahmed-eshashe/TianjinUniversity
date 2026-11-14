from pathlib import Path
import sys,json,numpy as np
from pxr import Usd
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
c=json.loads((W/'scene_plan.json').read_text());p=json.loads(Path(c['source_plan']).read_text());kin=ArmKinematics(Usd.Stage.Open(c['scene']));Q=np.array(c['material_to_world_rotation']);anchor=np.array(c['material_origin_world_m']);rk=np.array(c['knife_rotation_world']);C=np.array(c['proxy_origin_in_knife_m']);mount=np.array(p['mount_hand_from_knife']);q=np.array(c['cut'][-1]['q']);start=np.array(c['cut'][-1]['proxy']);withdraw=[]
def solve(proxy,q):
 origin=anchor+Q@proxy-rk@C;T=np.eye(4);T[:3,:3]=rk;T[:3,3]=origin;hand=T@np.linalg.inv(mount);q,pe,re=kin.solve(hand[:3,3]+hand[:3,:3]@PALM_OFFSET,hand[:3,:3],q)
 if pe>1e-4 or re>1e-3:raise ValueError((proxy.tolist(),pe,re))
 return q,origin,pe,re
for u in np.linspace(0,1,161):
 f=u*u*u*(10-15*u+6*u*u);position=start+[0,0,.105*f];q,origin,pe,re=solve(position,q);withdraw.append(dict(time=u*4,q=q.tolist(),proxy=position.tolist(),origin=origin.tolist(),error_m=pe,error_rad=re))
start=position.copy();bodyward=np.array(p['robot_root_world_matrix'])[:3,3]-anchor;bodyward[2]=0;bodyward/=np.linalg.norm(bodyward);direction=Q.T@bodyward
for u in np.linspace(0,1,121)[1:]:
 f=u*u*u*(10-15*u+6*u*u);position=start+.06*f*direction;q,origin,pe,re=solve(position,q);withdraw.append(dict(time=4+u*3,q=q.tolist(),proxy=position.tolist(),origin=origin.tolist(),error_m=pe,error_rad=re))
(W/'reports/withdraw_positive_candidate.json').write_text(json.dumps(withdraw,indent=2));print('IK passed',max(x['error_m']for x in withdraw))
