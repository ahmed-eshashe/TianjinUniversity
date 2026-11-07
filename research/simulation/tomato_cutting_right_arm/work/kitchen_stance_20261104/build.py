from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,UsdLux,Gf
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path[:0]=[str(r/'scripts'),str(r/'rl')]
from reach_kinematics import ArmKinematics,PALM_OFFSET
from tomato_fixed_mount_scene import matrix
p=json.loads((r/'work/handle_approach_20261104/plan.json').read_text());old=Usd.Stage.Open(p['scene']);ko=ArmKinematics(old);m=np.array(p['mount_hand_from_knife']);scene=w/'kitchen_stance.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
root=np.array(p['robot_root_world_matrix']);root[0,3]-=.14;matrix(UsdGeom.Xformable(s.GetPrimAtPath('/dual_ar5_o6')),root);k=ArmKinematics(s)
seed=np.array([p['home_rad'][n]for n in k.names]);
def solve(q):
 global seed
 t=ko.transforms(q)[ko.hand_path];seed,e,a=k.solve(t[:3,3]+t[:3,:3]@PALM_OFFSET,t[:3,:3],seed)
 assert e<2e-5 and a<2e-4,(e,a)
 return seed.tolist()
originalseed=seed.copy();target=ko.transforms(originalseed)[ko.hand_path];candidates=[];k.lower[5]=-.90;k.upper[5]=.90;rng=np.random.default_rng(42)
for guess in [np.clip(seed,k.lower,k.upper)]+[rng.uniform(k.lower,k.upper)for _ in range(80)]:
 q,e,a=k.solve(target[:3,3]+target[:3,:3]@PALM_OFFSET,target[:3,:3],guess)
 if e<2e-5 and a<2e-4:candidates.append(q)
assert candidates,'No initial pose'
seed=min(candidates,key=lambda q:np.linalg.norm(q-originalseed));home=seed.tolist()
for key in ['home_rad','closed_home_rad']:p[key].update(dict(zip(k.names,home)))
p['lift_route']=[solve(q)for q in p['lift_route']]
liftseed=seed.copy();endold=p['approach_routes'][-1][-1];t=ko.transforms(endold)[ko.hand_path];rng=np.random.default_rng(13);candidates=[]
for guess in [seed]+[rng.uniform(k.lower,k.upper)for _ in range(50)]:
 q,e,a=k.solve(t[:3,3]+t[:3,:3]@PALM_OFFSET,t[:3,:3],guess)
 if e<2e-5 and a<2e-4 and abs(q[5])<.82:candidates.append(q)
assert candidates,'No endpoint'
end=min(candidates,key=lambda q:np.linalg.norm(q-liftseed));p['approach_routes']=[[(liftseed+(end-liftseed)*(u*u*u*(10+u*(-15+6*u)))).tolist()for u in np.linspace(0,1,601)]]
# Bake initial articulation pose, preserving stationary world knife and fixture.
tf={'/dual_ar5_o6':root}
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
# Restore the original room at the benchmark's original world-to-local offset.
env=UsdGeom.Xform.Define(s,'/KitchenEnvironment');env.GetPrim().GetReferences().AddReference('/home/omen/Aperdata-SimReady-Kitchen-01/0_Kitchen_Indoor/Indoor.usd','/Root');t=np.eye(4);t[:3,3]=[2.2843094031304836,1.625671974500418,-.8616160089768693];matrix(env,t)
for name in ['SM_YZ_CF_10','SM_kitchen_Board','SM_kitchen_knife_02']:s.OverridePrim('/KitchenEnvironment/RZ/'+name).SetActive(False)
# Background is presentation geometry; working counter/board retain their physics.
for prim in Usd.PrimRange(env.GetPrim()):
 if prim.HasAPI(UsdPhysics.RigidBodyAPI):UsdPhysics.RigidBodyAPI(prim).CreateRigidBodyEnabledAttr(False)
 if prim.HasAPI(UsdPhysics.CollisionAPI):UsdPhysics.CollisionAPI(prim).CreateCollisionEnabledAttr(False)
 if prim.IsA(UsdLux.DomeLight):pass
UsdLux.DomeLight(s.GetPrimAtPath('/PresentationLight')).CreateColorAttr(Gf.Vec3f(1,1,1));UsdLux.DomeLight(s.GetPrimAtPath('/PresentationLight')).CreateIntensityAttr(350.)
s.GetRootLayer().Save();p.update(scene=str(scene),robot_root_world_matrix=root.tolist(),base_shift_m=[-.14,0,0],background_physics=False);(w/'plan.json').write_text(json.dumps(p,indent=2));print('Built closer stance and kitchen',home)
