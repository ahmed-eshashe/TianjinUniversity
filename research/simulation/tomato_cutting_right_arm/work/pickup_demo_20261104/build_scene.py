from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pxr import Usd,UsdGeom,UsdPhysics,Gf
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path[:0]=[str(r/'scripts'),str(r/'rl'),str(w)]
from reach_kinematics import ArmKinematics,PALM_OFFSET
from tomato_fixed_mount_scene import matrix
from materials import apply
p=json.loads((r/'work/overhand_grip_20261104/overhand_ready_plan.json').read_text());c=json.loads((w/'postures_free.json').read_text())[0];p['robot_root_world_matrix']=c['root'];p['knife_rotation']=c['rotation'];p['knife_origin_route_m']=[c['origin']];p['right_joint_route_rad']=[c['q']];p['home_rad'].update(dict(zip(p['right_joint_names'],c['q'])));root=np.array(c['root']);base=Usd.Stage.Open(p['scene']);left=ArmKinematics(base,side='left');left.root=root;left.lower[5]=-.75;left.upper[5]=.75
left.lower[0]=-.8;left.upper[0]=.8
leftbase=next(t[:3,3]for n,t in left.transforms(np.zeros(7)).items()if n.endswith('_link2'))
# Tuck unused arm beside torso instead of the previous horizontal zero-joint pose.
def residual(q):
 tf=left.transforms(q);hand=tf[left.hand_path];elbow=next(t[:3,3]for n,t in tf.items() if n.endswith('_link4'))
 return np.r_[hand[:3,3]-(leftbase+[.20,-.05,-.37]),.4*(elbow-(leftbase+[.06,-.06,-.2])),.01*q]
rng=np.random.default_rng(35);best=None
for seed in [np.zeros(7)]+[rng.uniform(left.lower,left.upper)for _ in range(8)]:
 sol=least_squares(residual,seed,bounds=(left.lower,left.upper),max_nfev=200)
 if best is None or np.linalg.norm(sol.fun)<np.linalg.norm(best.fun):best=sol
p['home_rad'].update(dict(zip(left.names,best.x)));print('left',best.x,flush=True)
scene=w/'posture_materials_v03.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.);matrix(UsdGeom.Xformable(s.GetPrimAtPath('/dual_ar5_o6')),root)
# Bake all joint-driven transforms for a correct stopped-stage view.
k=ArmKinematics(s);tf={'/dual_ar5_o6':root};home=p['home_rad']
def tr(path):
 if path in tf:return tf[path]
 parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
 if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*home.get(name,0)).as_matrix()
 tf[path]=tr(parent)@a@rot@b;return tf[path]
for path in sorted(k.by_child,key=lambda x:x.count('/')):
 prim=s.GetPrimAtPath(path);parent=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(prim.GetParent())).T;matrix(UsdGeom.Xformable(prim),np.linalg.inv(parent)@tr(path))
for name,value in home.items():
 prim=s.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
 if prim:UsdPhysics.DriveAPI.Apply(prim,'angular').CreateTargetPositionAttr(float(np.rad2deg(value)))
report=apply(s,p['tool_path']);s.GetRootLayer().Save();p['scene']=str(scene);(w/'posture_plan_v03.json').write_text(json.dumps(p,indent=2));(w/'materials_report.json').write_text(json.dumps(report,indent=2))
