from pathlib import Path
from pxr import Usd,UsdGeom
import json,numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;p=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());route=json.loads((w/'clear_entry_robot_plan_v2.json').read_text());stage=Usd.Stage.Open(p['scene']);cache=UsdGeom.XformCache();tool=stage.GetPrimAtPath(p['tool_path']);geometry=[]
for child in ['CollisionHandle','CollisionBlade']:
 prim=stage.GetPrimAtPath(p['tool_path']+'/'+child);mesh=UsdGeom.Mesh(prim);v=np.asarray(mesh.GetPointsAttr().Get(),float);T=np.array(cache.GetLocalToWorldTransform(prim)*cache.GetLocalToWorldTransform(tool).GetInverse());v=(np.c_[v,np.ones(len(v))]@T)[:,:3];counts=np.array(mesh.GetFaceVertexCountsAttr().Get());indices=np.array(mesh.GetFaceVertexIndicesAttr().Get());assert np.all(counts==3);geometry.append((child,v,indices.reshape(-1,3)))
posts=[]
for path in p['fixture_paths']:
 T=np.array(cache.GetLocalToWorldTransform(stage.GetPrimAtPath(path)));posts.append((path,np.linalg.inv(T),.5+.003/np.linalg.norm(T[:3,:3],axis=1)))
def intersects(tris,half):
 edges=np.roll(tris,-1,axis=1)-tris;axes=np.concatenate([np.broadcast_to(np.eye(3),(len(tris),3,3)),np.cross(edges[:,:,None,:],np.eye(3)[None,None,:,:]).reshape(-1,9,3),np.cross(edges[:,0],edges[:,1])[:,None,:]],axis=1);projections=np.einsum('nai,nvi->nav',axes,tris);radius=np.einsum('nai,i->na',abs(axes),half);return np.all((projections.min(2)<=radius+1e-12)&(projections.max(2)>=-radius-1e-12),axis=1)
bad=[]
for index,row in enumerate(route['rows']):
 R=np.array(row['tool_rotation']);t=np.array(row['tool_origin'])
 for child,v,faces in geometry:
  world=v@R.T+t
  for path,inverse,half in posts:
   local=(np.c_[world,np.ones(len(world))]@inverse)[:,:3]
   if intersects(local[faces],half).any():bad.append(dict(point=index,phase=row['phase'],shape=child,post=path))
result=dict(passed=not bad,minimum_tested_clearance_m=.003,poses=len(route['rows']),collisions=bad,robot_body_clearance_tested=False);(w/'cradle_route_check.json').write_text(json.dumps(result,indent=2));print(result);assert result['passed']
