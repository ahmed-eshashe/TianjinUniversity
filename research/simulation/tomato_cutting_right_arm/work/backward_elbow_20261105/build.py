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
end=np.array(json.loads((w/'endpoints.json').read_text())[0]['q']);rng=np.random.default_rng(55);candidates=[];target=k.transforms(q0)[k.hand_path]
for guess in [end]+[rng.uniform(k.lower,k.upper)for _ in range(90)]:
 q,e,a=k.solve(target[:3,3]+target[:3,:3]@PALM_OFFSET,target[:3,:3],guess)
 if e<2e-5 and a<2e-4 and q[0]>1.5:candidates.append(q)
assert candidates
seed=min(candidates,key=lambda q:np.linalg.norm(q-end));home=seed.copy();print('home',home,flush=True)
for key in ['home_rad','closed_home_rad']:p[key].update(dict(zip(k.names,home)))
new=[]
for oldq in p['lift_route']:
 target=k.transforms(oldq)[k.hand_path];seed,e,a=k.solve(target[:3,3]+target[:3,:3]@PALM_OFFSET,target[:3,:3],seed);assert e<2e-5 and a<2e-4,(e,a);new.append(seed.tolist())
p['lift_route']=new;lift=seed.copy();route=[]
for u in np.linspace(0,1,601):
 blend=u*u*u*(10+u*(-15+6*u));direct=lift+(end-lift)*blend;target=k.transforms(direct)[k.hand_path];pos=target[:3,3]+target[:3,:3]@PALM_OFFSET;pos[2]+=.08*np.sin(np.pi*blend)**2
 seed,e,a=k.solve(pos,target[:3,:3],seed);assert e<2e-4 and a<2e-3,(u,e,a);route.append(seed.tolist())
p['approach_routes']=[route];print('final elbow',k.transforms(seed)[ep][:3,3],flush=True)
scene=w/'backward_elbow.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
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
s.GetRootLayer().Save();p.update(scene=str(scene),elbow_selection="backward maximum with fixed hand pose",outward_axis=out.tolist());(w/'plan.json').write_text(json.dumps(p,indent=2));print('done',flush=True)
