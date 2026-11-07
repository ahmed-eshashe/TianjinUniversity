from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,Gf
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent
sys.path[:0]=[str(r/'scripts'),str(r/'rl')]
from check_reach_clearance import check
from reach_kinematics import ArmKinematics,PALM_OFFSET
from tomato_fixed_mount_scene import matrix
old=json.loads((r/'work/exploratory_demo_20261104/demo_plan_v02.json').read_text())
g=json.loads((r/'work/exploratory_demo_20261104/grip_candidate.json').read_text())
m=np.array(old['mount_hand_from_knife']);c=np.array(g['handle_in_hand_m']);hc=m[:3,:3].T@(c-m[:3,3]);m[:3,:3]=m[:3,:3]@Rotation.from_euler('x',90,degrees=True).as_matrix()@Rotation.from_euler('y',180,degrees=True).as_matrix();m[:3,3]=c-m[:3,:3]@hc
k=ArmKinematics(Usd.Stage.Open(old['scene']));rk=np.array(old['knife_rotation']);rh=rk@m[:3,:3].T;o=np.array(old['knife_origin_route_m'][0]);q=np.array([old['home_rad'][n] for n in k.names]);rng=np.random.default_rng(53)
k.lower[5]=max(k.lower[5],-.80);k.upper[5]=min(k.upper[5],.80)
k.upper[1]=min(k.upper[1],-.3);k.lower[3]=max(k.lower[3],.3)
oldrk=rk.copy();oldo=o.copy();found=False
for yaw in [0,45,-45,90,-90,135,-135,180]:
 rk=Rotation.from_euler('z',yaw,degrees=True).as_matrix()@oldrk;rh=rk@m[:3,:3].T;o=oldo+oldrk@hc-rk@hc
 for seed in [q]+[rng.uniform(k.lower,k.upper) for _ in range(15)]:
  trial,err,angle=k.solve(o-rh@m[:3,3]+rh@PALM_OFFSET,rh,seed)
  if err<2e-5 and angle<2e-4:
   overlap=check(trial,left_zero=True,root_matrix=old['robot_root_world_matrix'],hand_values={n:v for n,v in old['home_rad'].items() if 'right_rh_' in n})
   if not overlap:q=trial;found=True;break
   print('Rejected overlap',overlap,flush=True)
 if found:break
if not found:raise ValueError('IK unreachable')
print('heading adjustment',yaw)
scene=w/'overhand_scene_v05.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[old['scene']]
j=UsdPhysics.FixedJoint(s.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount'));j.CreateLocalPos0Attr(Gf.Vec3f(*m[:3,3]));quat=Rotation.from_matrix(m[:3,:3]).as_quat();j.CreateLocalRot0Attr(Gf.Quatf(float(quat[3]),Gf.Vec3f(*quat[:3])))
knife=np.eye(4);knife[:3,:3]=rk;knife[:3,3]=o;matrix(UsdGeom.Xformable(s.GetPrimAtPath(old['tool_path'])),np.linalg.inv(np.array(old['robot_root_world_matrix']))@knife)
home=dict(old['home_rad']);home.update({'right_rh_thumb_cmc_pitch':.49,'right_rh_thumb_ip':1.86*.49});home.update(dict(zip(k.names,q)))
for name,value in home.items():
 prim=s.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
 if prim:UsdPhysics.DriveAPI.Apply(prim,'angular').CreateTargetPositionAttr(float(np.rad2deg(value)))
s.GetRootLayer().Save()
p=dict(old,scene=str(scene),knife_rotation=rk.tolist(),home_rad=home,mount_hand_from_knife=m.tolist(),right_joint_route_rad=[q.tolist()],knife_origin_route_m=[o.tolist()],limitations=['Stationary overhand pose; movement route must be recomputed before use','Disclosed fixed attachment, no friction-retention claim','Research validation remains pending'])
(w/'overhand_plan_v05.json').write_text(json.dumps(p,indent=2)+'\n');print('IK errors',err,angle,'palm above handle',float((rh@(PALM_OFFSET-c))[2]))
