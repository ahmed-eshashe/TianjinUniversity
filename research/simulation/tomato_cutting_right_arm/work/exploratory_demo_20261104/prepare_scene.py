from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,Gf
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'scripts'));sys.path.insert(0,str(r/'rl'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
from tomato_fixed_mount_scene import matrix
old=json.loads((r/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json').read_text());grip=json.loads((w/'grip_candidate.json').read_text());source=Usd.Stage.Open(old['scene']);kin=ArmKinematics(source);mount=np.array(grip['mount_hand_from_knife']);rk=np.array(old['knife_rotation']);rh=rk@mount[:3,:3].T
origins=np.array(old['knife_origin_route_m']);q=np.array([old['home_rad'][n] for n in kin.names]);route=[];errs=[]
# Search only the initial IK seed; all subsequent motion is continuous.
rng=np.random.default_rng(204)
oldrk=rk.copy();oldorigins=origins.copy();found=False
blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());bc=np.mean(blade['vertices'],axis=0)
for yaw in [180,90,-90,45,-45,135,-135]:
 rk=Rotation.from_euler('z',yaw,degrees=True).as_matrix()@oldrk;rh=rk@mount[:3,:3].T;origins=oldorigins+oldrk@bc-rk@bc
 initial_target=origins[0]-rh@mount[:3,3]+rh@PALM_OFFSET
 for seed in [q]+[rng.uniform(kin.lower,kin.upper) for _ in range(5)]:
  trial,err,angle=kin.solve(initial_target,rh,seed)
  if err<2e-5 and angle<2e-4:q=trial;found=True;break
 if found:break
if not found:raise ValueError('No reachable initial grasp pose')
# Retain existing offset blade route; a new hand/tool transform requires fresh IK and validation.
for origin in origins:
 hand_origin=origin-rh@mount[:3,3];q,err,angle=kin.solve(hand_origin+rh@PALM_OFFSET,rh,q);route.append(q);errs.append([err,angle])
 if err>2e-5 or angle>2e-4:raise ValueError(('New grasp IK failed',len(route),err,angle))
scene=w/'demo_grip_scene.usda';stage=Usd.Stage.CreateNew(str(scene));stage.GetRootLayer().subLayerPaths=[old['scene']];joint=UsdPhysics.FixedJoint(stage.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount'));joint.CreateLocalPos0Attr(Gf.Vec3f(*mount[:3,3]));quat=Rotation.from_matrix(mount[:3,:3]).as_quat();joint.CreateLocalRot0Attr(Gf.Quatf(float(quat[3]),Gf.Vec3f(*quat[:3])))
knife=np.eye(4);knife[:3,:3]=rk;knife[:3,3]=origins[0];matrix(UsdGeom.Xformable(stage.GetPrimAtPath(old['tool_path'])),np.linalg.inv(np.array(old['robot_root_world_matrix']))@knife)
home=dict(old['home_rad']);home.update(dict(zip(kin.names,route[0])));home.update(grip['hand_joint_rad'])
for name,value in home.items():
 prim=stage.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
 if prim:UsdPhysics.DriveAPI.Apply(prim,'angular').CreateTargetPositionAttr(float(np.rad2deg(value)))
# Knife and its holding hand form an ideal attached assembly, not contact-based retention.
filtered=[];tool=stage.GetPrimAtPath(old['tool_path']);rel=UsdPhysics.FilteredPairsAPI.Apply(tool).CreateFilteredPairsRel()
for prim in stage.Traverse():
 if prim.GetName().startswith('right_rh_') and prim.HasAPI(UsdPhysics.RigidBodyAPI):rel.AddTarget(prim.GetPath());filtered.append(str(prim.GetPath()))
stage.GetRootLayer().Save();plan=dict(old,scene=str(scene),home_rad={k:float(v) for k,v in home.items()},mount_hand_from_knife=mount.tolist(),right_joint_route_rad=np.array(route).tolist(),knife_origin_route_m=origins.tolist(),knife_rotation=rk.tolist(),source_sha256={},finger_grasp=False,visible_finger_wrap=True,ideal_mount=True,exploratory_demo=True,knife_hand_collision_filters=filtered,limitations=['Exploratory scripted demo; force/work not validated','Ideal fixed knife attachment; posed fingers do not prove friction retention','New route requires fresh native tracking/mount/clearance validation'])
(w/'demo_plan.json').write_text(json.dumps(plan,indent=2)+'\n');print('Prepared',len(route),'poses; max IK error',np.max(errs,axis=0))
