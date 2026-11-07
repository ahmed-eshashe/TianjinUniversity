from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdPhysics,Gf
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
p=json.loads((w/'overhand_plan_v05.json').read_text());f=json.loads((w/'final_fit.json').read_text());original=json.loads((r/'work/exploratory_demo_20261104/grip_candidate.json').read_text());om=np.array(original['mount_hand_from_knife']);hc=om[:3,:3].T@(np.array(original['handle_in_hand_m'])-om[:3,3]);m=np.eye(4);m[:3,:3]=f['A'];m[:3,3]=np.array(f['center'])-m[:3,:3]@hc
rk=np.array(p['knife_rotation']);rh=rk@m[:3,:3].T;o=np.array(p['knife_origin_route_m'][0]);k=ArmKinematics(Usd.Stage.Open(p['scene']));seed=np.array([p['home_rad'][n] for n in k.names]);q,e,a=k.solve(o-rh@m[:3,3]+rh@PALM_OFFSET,rh,seed);assert e<2e-5 and a<2e-4
scene=w/'overhand_scene_v06.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];j=UsdPhysics.FixedJoint(s.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount'));j.CreateLocalPos0Attr(Gf.Vec3f(*m[:3,3]));quat=Rotation.from_matrix(m[:3,:3]).as_quat();j.CreateLocalRot0Attr(Gf.Quatf(float(quat[3]),Gf.Vec3f(*quat[:3])))
home=p['home_rad'];home.update(dict(zip(k.names,q)))
for finger,flex in f['fingers'].items():home['right_rh_'+finger+'_mcp_pitch']=np.deg2rad(flex);home['right_rh_'+finger+'_dip']=np.deg2rad(flex*.89)
for name,value in home.items():
 prim=s.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
 if prim:UsdPhysics.DriveAPI.Apply(prim,'angular').CreateTargetPositionAttr(float(np.rad2deg(value)))
s.GetRootLayer().Save();p.update(scene=str(scene),mount_hand_from_knife=m.tolist(),right_joint_route_rad=[q.tolist()]);(w/'overhand_plan_v06.json').write_text(json.dumps(p,indent=2));print('Final IK',e,a)
