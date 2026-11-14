from pathlib import Path
import json,numpy as np
from pxr import Usd,UsdGeom,UsdPhysics
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent;c=json.loads((W/'scene_plan.json').read_text());p=json.loads(Path(c['source_plan']).read_text());s=Usd.Stage.Open(c['scene']);cache=UsdGeom.XformCache();bounds=UsdGeom.BBoxCache(0,['default','render']);state=json.loads((W/'runs/dry02/collision_state.json').read_text());actual=dict(zip(state['body_names'],state['body_poses']))
def T(pose):
 t=np.eye(4);t[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();t[:3,3]=pose[:3];return t
oldtool=T(state['tool_pose']);meshdata=[]
for prim in s.Traverse():
 if 'right_rh_'not in str(prim.GetPath()) or not prim.IsA(UsdGeom.Mesh) or not prim.HasAPI(UsdPhysics.CollisionAPI) or UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get()==False:continue
 parent=prim
 while parent and not parent.HasAPI(UsdPhysics.RigidBodyAPI):parent=parent.GetParent()
 if not parent or parent.GetName()not in actual:continue
 geom=np.array(cache.GetLocalToWorldTransform(prim)).T;body=np.array(cache.GetLocalToWorldTransform(parent)).T;relative=np.linalg.inv(oldtool)@T(actual[parent.GetName()])@np.linalg.inv(body)@geom;pts=np.array(UsdGeom.Mesh(prim).GetPointsAttr().Get());pts=pts@relative[:3,:3].T+relative[:3,3];meshdata.append((str(prim.GetPath()),pts))
fixture=[]
for path in p['fixture_paths']:
 b=bounds.ComputeWorldBound(s.GetPrimAtPath(path)).ComputeAlignedRange();fixture.append((path,np.array(b.GetMin()),np.array(b.GetMax())))

rk=np.array(c['knife_rotation_world']);offset=np.array(c['material_origin_world_m']);samples=c['cut'][::80]+c['cut'][-1:]+c['withdraw'][::10]+c['withdraw'][-1:];boxes=[]
for row in samples:
 for path,pts in meshdata:
  points=pts@rk.T+np.array(row['origin']);boxes.append([points.min(0),points.max(0)])
boxes=np.array(boxes);candidates=[]
for x in np.linspace(-.04,.065,8):
 for y in np.linspace(-.12,.18,21):
  anchor=np.array([x,y,0]);delta=anchor-offset;minimum=1e9
  for f,fl,fh in fixture:
   gap=np.maximum(boxes[:,0]+delta-fh,fl-boxes[:,1]-delta).max(1).min();minimum=min(minimum,float(gap))
  if minimum>.006:candidates.append((float(np.linalg.norm(anchor-np.array([.04,-.02,0]))),anchor,minimum))
candidates.sort(key=lambda x:x[0]);print('Clearance candidates',len(candidates),flush=True)
import sys
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
kin=ArmKinematics(s);Q=np.array(c['material_to_world_rotation']);C=np.array(c['proxy_origin_in_knife_m']);mount=np.array(p['mount_hand_from_knife']);result=[]
for distance,anchor,clearance in candidates[:30]:
 q=np.array(p['approach_routes'][-1][-1]);worst=0;failed=None
 for i,row in enumerate(samples):
  origin=anchor+Q@np.array(row['proxy'])-rk@C;T=np.eye(4);T[:3,:3]=rk;T[:3,3]=origin;hand=T@np.linalg.inv(mount);q,pe,re=kin.solve(hand[:3,3]+hand[:3,:3]@PALM_OFFSET,hand[:3,:3],q);worst=max(worst,pe)
  if pe>1e-4 or re>1e-3:failed=[i,pe,re];break
 result.append(dict(anchor=anchor.tolist(),clearance_m=clearance,pass_ik=failed is None,failure=failed,max_error_m=worst));print(result[-1],flush=True)
 if failed is None:break
(W/'reports/placement_screen.json').write_text(json.dumps(result,indent=2))
