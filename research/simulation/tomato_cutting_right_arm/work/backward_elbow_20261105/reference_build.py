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
rng=np.random.default_rng(22);candidates=[]
for seed in [q0]+[rng.uniform(k.lower,k.upper)for _ in range(36)]:
 q,e=solve(q0,seed,.30)
 if e<1e-5:candidates.append(q)
assert candidates,'No outward solution'
seed=min(candidates,key=lambda q:np.linalg.norm(q-q0)+(10 if q[3]<0 else 0));home=seed.copy();print('new initial',home,flush=True)
for key in ['home_rad','closed_home_rad']:p[key].update(dict(zip(k.names,home)))
new=[]
for oldq in p['lift_route']:
 seed,e=solve(oldq,seed,.30);assert e<1e-5,e;new.append(seed.tolist())
p['lift_route']=new;lift=seed.copy();oldend=p['approach_routes'][-1][-1];target=k.transforms(oldend)[k.hand_path];ends=[]
for guess in [seed]+[rng.uniform(k.lower,k.upper)for _ in range(65)]:
 q,e,a=k.solve(target[:3,3]+target[:3,:3]@PALM_OFFSET,target[:3,:3],guess)
 if e<2e-5 and a<2e-4 and q[3]>0:ends.append(q)
assert ends,'No alternate endpoint'
end=min(ends,key=lambda q:np.linalg.norm(q-lift));print('end',end,'elbow',k.transforms(end)[ep][:3,3],flush=True)
p['approach_routes']=[[(lift+(end-lift)*(u*u*u*(10+u*(-15+6*u)))).tolist()for u in np.linspace(0,1,601)]]
scene=w/'outward_elbow.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
tf={'/dual_ar5_o6':k.root}
def tr(path):
 if path in tf:return tf[path]
 parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
 if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*p['home_rad'].get(name,0)).as_matrix()
 tf[path]=tr(parent)@a@rot@b;return tf[path]
for path in sorted(k.by_child,key=lambda x:x.count('/')):
 prim=s.GetPrimAtPath(path);parent=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(prim.GetParent())).T;matrix(UsdGeom.Xformable(prim),np.linalg.inv(parent)@tr(path))
for name,v in p['home_rad'].items():
 prim=s.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
 if prim:UsdPhysics.DriveAPI.Apply(prim,'angular').CreateTargetPositionAttr(float(np.rad2deg(v)))
s.GetRootLayer().Save();p.update(scene=str(scene),elbow_height_m=.30,outward_axis=out.tolist());(w/'plan.json').write_text(json.dumps(p,indent=2));print('done',flush=True)
