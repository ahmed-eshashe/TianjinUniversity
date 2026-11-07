from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pxr import Usd
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
from check_reach_clearance import check
p=json.loads((r/'work/overhand_grip_20261104/overhand_ready_plan.json').read_text());k=ArmKinematics(Usd.Stage.Open(p['scene']));m=np.array(p['mount_hand_from_knife']);rng=np.random.default_rng(510);hc=np.array([-.0860033812,.0076461609,.0015865240]);results=[]
# Search an elbow-down posture; the old solver selected only hand-pose accuracy.
for yaw in [0,45,90,135,180,-45,-90]:
 rk=Rotation.from_euler('z',yaw,degrees=True).as_matrix()@np.array([[1,0,0],[0,0,-1],[0,1,0]])
 for xy in [[.28,-.04],[.32,-.10],[.25,.04]]:
  handle=np.array([*xy,.085]);o=handle-rk@hc;rh=rk@m[:3,:3].T;hp=o-rh@m[:3,3];target=hp+rh@PALM_OFFSET
  def residual(q):
   tf=k.transforms(q);hand=tf[k.hand_path];elbow=next(t[:3,3]for n,t in tf.items() if n.endswith('_link4'));wrist=next(t[:3,3]for n,t in tf.items() if n.endswith('_link5'))
   return np.r_[10*(hand[:3,3]+hand[:3,:3]@PALM_OFFSET-target),2*Rotation.from_matrix(rh@hand[:3,:3].T).as_rotvec(),.8*(elbow[2]-.13),2*np.maximum(.065-elbow[2],0),.005*q]
  for _ in range(6):
   sol=least_squares(residual,rng.uniform(k.lower,k.upper),bounds=(k.lower,k.upper),max_nfev=160,ftol=1e-8)
   q,e,a=k.solve(target,rh,sol.x);tf=k.transforms(q);el=next(t[:3,3]for n,t in tf.items() if n.endswith('_link4'))
   if e>2e-5 or a>2e-4 or not .065<el[2]<.30 or abs(q[5])>.85:continue
   overlap=check(q,left_zero=True,root_matrix=p['robot_root_world_matrix'],hand_values={n:v for n,v in p['home_rad'].items() if 'right_rh_'in n})
   if overlap:continue
   score=abs(el[2]-.15)+.03*np.linalg.norm(q)+.03*abs(q[5]);results.append(dict(score=score,q=q.tolist(),rotation=rk.tolist(),origin=o.tolist(),handle=handle.tolist(),elbow=el.tolist(),yaw=yaw));print('candidate',yaw,xy,el,score,flush=True)
results.sort(key=lambda x:x['score']);(w/'postures.json').write_text(json.dumps(results,indent=2));print('COUNT',len(results))
