from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,Gf,Sdf
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path[:0]=[str(r/'scripts'),str(r/'rl')]
from reach_kinematics import ArmKinematics,PALM_OFFSET
from tomato_fixed_mount_scene import matrix
p=json.loads((w/'posture_plan_v03.json').read_text());scene=w/'pickup_scene.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
j=UsdPhysics.FixedJoint(s.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount'));j.CreateExcludeFromArticulationAttr(True);j.CreateJointEnabledAttr(False)
k=ArmKinematics(s);closed=p['home_rad'].copy();initial=closed.copy()
for finger in ['index','middle','ring','pinky']:initial['right_rh_'+finger+'_mcp_pitch']=np.deg2rad(15);initial['right_rh_'+finger+'_dip']=np.deg2rad(15*.89)
initial['right_rh_thumb_cmc_pitch']=.14;initial['right_rh_thumb_ip']=.14*1.86
# Update stopped-view hand pose to the open pregrasp.
tf={'/dual_ar5_o6':k.root}
def tr(path):
 if path in tf:return tf[path]
 parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
 if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*initial.get(name,0)).as_matrix()
 tf[path]=tr(parent)@a@rot@b;return tf[path]
for path in sorted(k.by_child,key=lambda x:x.count('/')):
 prim=s.GetPrimAtPath(path);parent=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(prim.GetParent())).T;matrix(UsdGeom.Xformable(prim),np.linalg.inv(parent)@tr(path))
for name,v in initial.items():
 prim=s.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
 if prim:UsdPhysics.DriveAPI.Apply(prim,'angular').CreateTargetPositionAttr(float(np.rad2deg(v)))
rk=np.array(p['knife_rotation']);o=np.array(p['knife_origin_route_m'][0]);tool=np.eye(4);tool[:3,:3]=rk;tool[:3,3]=o
clamp=UsdPhysics.FixedJoint.Define(s,'/PickupFixture/Clamp');clamp.CreateExcludeFromArticulationAttr(True);clamp.CreateBody1Rel().SetTargets([p['tool_path']]);clamp.CreateLocalPos0Attr(Gf.Vec3f(*o));q=Rotation.from_matrix(rk).as_quat();clamp.CreateLocalRot0Attr(Gf.Quatf(float(q[3]),Gf.Vec3f(*q[:3])));clamp.CreateLocalPos1Attr(Gf.Vec3f(0));clamp.CreateLocalRot1Attr(Gf.Quatf(1));clamp.CreateJointEnabledAttr(True)
# Visible fixture: two posts below exposed blade and handle butt, outside the finger region.
mat=UsdShade.Material.Define(s,'/PresentationLooks/fixture');sh=UsdShade.Shader.Define(s,str(mat.GetPath())+'/Surface');sh.CreateIdAttr('UsdPreviewSurface');sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(.13,.16,.18));sh.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(.6);sh.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.35);mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface')
fixture=[]
for i,x in enumerate([-.025,-.25]):
 pos=o+rk@np.array([x,0,0]);top=o[2]-.026;bottom=-.035;path='/PickupFixture/Post'+str(i);cube=UsdGeom.Cube.Define(s,path);cube.CreateSizeAttr(1.);t=np.eye(4);t[:3,:3]=np.column_stack([rk[:,0]*.025,rk[:,2]*.045,np.array([0,0,top-bottom])]);t[:3,3]=[pos[0],pos[1],(top+bottom)/2];matrix(cube,t);UsdPhysics.CollisionAPI.Apply(cube.GetPrim());UsdShade.MaterialBindingAPI.Apply(cube.GetPrim()).Bind(mat);fixture.append(path)
# Smooth lift only after close and attachment; exact IK uses the selected relaxed branch.
m=np.array(p['mount_hand_from_knife']);rh=rk@m[:3,:3].T;seed=np.array([closed[n]for n in k.names]);route=[]
for i in range(241):
 u=i/240;b=u*u*u*(10+u*(-15+6*u));origin=o+[0,0,.065*b];seed,e,a=k.solve(origin-rh@m[:3,3]+rh@PALM_OFFSET,rh,seed)
 if e>2e-5 or a>2e-4:raise ValueError(('Lift unreachable',i,e,a))
 route.append(seed.tolist())
s.GetRootLayer().Save();p.update(scene=str(scene),home_rad=initial,closed_home_rad=closed,lift_route=route,fixture_paths=fixture,sequence=['fixture supported, fingers open','close fingers with arm stationary','engage disclosed hand fixed attachment and release fixture','lift 65 mm','hold'],fixture_ideal_clamp=True,tool_separate_rigid_body=True,video_recorded=False);(w/'pickup_plan.json').write_text(json.dumps(p,indent=2));print('Prepared pickup sequence')
