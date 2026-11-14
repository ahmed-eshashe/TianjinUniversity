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
rk=np.array(c['knife_rotation_world']);minimum=1e9;worst=None
for phase in ['entry','cut','withdraw']:
 for row in c[phase][::10]:
  for path,pts in meshdata:
   points=pts@rk.T+np.array(row['origin']);lo=points.min(0);hi=points.max(0)
   for f,fl,fh in fixture:
    gap=float(np.maximum(lo-fh,fl-hi).max())
    if gap<minimum:minimum=gap;worst=[phase,row['time'],path,f,gap]
result=dict(hand_collision_mesh_count=len(meshdata),minimum_AABB_clearance_m=minimum,worst=worst,scope='Conservative hand collision-mesh boxes at sampled poses, actual closed-finger pose from dry run. Native continuous route still required.')
(W/'reports/cradle_clearance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
