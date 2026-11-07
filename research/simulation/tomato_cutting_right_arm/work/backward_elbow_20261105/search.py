from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path[:0]=[str(r/'scripts'),str(r/'rl')]
from reach_kinematics import ArmKinematics,PALM_OFFSET
from tomato_fixed_mount_scene import matrix
p=json.loads((r/'work/kitchen_stance_20261104/plan.json').read_text());s0=Usd.Stage.Open(p['scene']);k=ArmKinematics(s0);l=ArmKinematics(s0,'left');q0=np.array([p['home_rad'][n]for n in k.names]);tf=k.transforms(q0);ep=next(x for x in tf if x.endswith('_link4'));sp=next(x for x in tf if x.endswith('_link2'));shoulder=tf[sp][:3,3];lt=l.transforms([p['home_rad'][n]for n in l.names]);ls=next(t[:3,3]for x,t in lt.items()if x.endswith('_link2'));out=shoulder-ls;out[2]=0;out/=np.linalg.norm(out);print('out',out,'old elbow',np.dot(tf[ep][:3,3]-shoulder,out),flush=True)
k.lower[5]=-.90;k.upper[5]=.90
# Seven-axis posture selection: retain hand pose and request outward elbow offset.
def solve(oldq,seed,offset):
 target=k.transforms(oldq)[k.hand_path]
 def residual(q):
  t=k.transforms(q);h=t[k.hand_path]
  return np.r_[h[:3,3]-target[:3,3],.2*Rotation.from_matrix(target[:3,:3]@h[:3,:3].T).as_rotvec(),.5*(t[ep][2,3]-offset)]
 sol=least_squares(residual,np.clip(seed,k.lower,k.upper),bounds=(k.lower,k.upper),max_nfev=250,gtol=1e-10,ftol=1e-10,xtol=1e-10)
 return sol.x,np.linalg.norm(sol.fun)

rng=np.random.default_rng(51);res=[];oldend=p['approach_routes'][-1][-1];target=k.transforms(oldend)[k.hand_path]
for guess in [oldend]+[rng.uniform(k.lower,k.upper)for _ in range(140)]:
 q,e,a=k.solve(target[:3,3]+target[:3,:3]@PALM_OFFSET,target[:3,:3],guess)
 if e<2e-5 and a<2e-4:
  el=k.transforms(q)[ep][:3,3];res.append(dict(q=q.tolist(),el=el.tolist(),back=float((el-shoulder)@k.root[:3,0])))
res.sort(key=lambda x:-x['back']);(w/'endpoints.json').write_text(json.dumps(res,indent=2));print('shoulder',shoulder,'best',res[:3],flush=True)
