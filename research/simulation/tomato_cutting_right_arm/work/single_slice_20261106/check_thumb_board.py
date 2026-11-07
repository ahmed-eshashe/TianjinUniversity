from pathlib import Path
import json,numpy as np,fcl
from pxr import Usd,UsdGeom,UsdPhysics
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];p=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());s=Usd.Stage.Open(p['scene']);xc=UsdGeom.XformCache();a=json.loads((w/'refined_tracking01/collision_state.json').read_text());body='right_rh_thumb_distal';pose=np.array(a['body_poses'][a['body_names'].index(body)]);actual=np.eye(4);actual[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();actual[:3,3]=pose[:3];objects=[];rows=[]
for prim in s.Traverse():
 if not prim.HasAPI(UsdPhysics.CollisionAPI)or not prim.IsA(UsdGeom.Mesh):continue
 owner=prim
 while owner and not owner.HasAPI(UsdPhysics.RigidBodyAPI):owner=owner.GetParent()
 isthumb=owner and owner.GetName()==body
 isboard=str(prim.GetPath())==p['board_path']
 if not(isthumb or isboard):continue
 m=UsdGeom.Mesh(prim);counts=np.array(m.GetFaceVertexCountsAttr().Get());assert np.all(counts==3);v=np.array(m.GetPointsAttr().Get(),float);faces=np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);T=np.array(xc.GetLocalToWorldTransform(prim)).T
 if isthumb:T=actual@np.linalg.inv(np.array(xc.GetLocalToWorldTransform(owner)).T)@T
 v=v@T[:3,:3].T+T[:3,3];model=fcl.BVHModel();model.beginModel(len(v),len(faces));model.addSubModel(v,faces);model.endModel();objects.append(fcl.CollisionObject(model));rows.append(dict(path=str(prim.GetPath()),minimum=v.min(0).tolist(),maximum=v.max(0).tolist(),below_board_points=v[v[:,2]<0].tolist()if isthumb else []))
res=fcl.CollisionResult();cnt=fcl.collide(*objects,fcl.CollisionRequest(num_max_contacts=10,enable_contact=True),res);dist=fcl.distance(*objects,fcl.DistanceRequest(),fcl.DistanceResult());out=dict(phase=a['phase'],tool_pose=a['tool_pose'],meshes=rows,intersections=cnt,distance_m=dist);(w/'thumb_board_geometry_check.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items()if k!='meshes'});print([{k:v for k,v in row.items()if k!='below_board_points'}for row in rows])
