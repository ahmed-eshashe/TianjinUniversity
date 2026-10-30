"""Search exact convex projected handle/hand outlines; requires runtime validation."""
import json,itertools
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom
# Share the hand's USD joint and mesh geometry with the earlier exploratory search.
source=(Path(__file__).with_name('search_grasp_geometry.py')).read_text()
exec(source.split('from scipy.spatial import ConvexHull')[0])
knife=s.GetPrimAtPath('/Indoor/RZ/SM_kitchen_knife_02');meshknife=UsdGeom.Mesh(knife)
counts=np.array(meshknife.GetFaceVertexCountsAttr().Get());indices=np.array(meshknife.GetFaceVertexIndicesAttr().Get());offsets=np.r_[0,np.cumsum(counts)]
faces=np.array(UsdGeom.Subset(s.GetPrimAtPath(str(knife.GetPath())+'/Section2')).GetIndicesAttr().Get());used=np.unique(np.concatenate([indices[offsets[f]:offsets[f+1]] for f in faces]))
localpoints=np.array(meshknife.GetPointsAttr().Get())[used];meta=json.load(open('work/kitchen_reach_metadata.json'));km=np.array(xc.GetLocalToWorldTransform(knife)).T
world_vectors=(localpoints-np.array(meta['knife_handle_local']))@km[:3,:3].T
old=np.array(json.load(open('work/reach_seed.json'))['orientation'])
centers=np.array(list(itertools.product(np.linspace(.025,.10,91),np.linspace(.06,.16,101))))
results=[]
for tilt in [45,55,65,75,90]:
 rot=old@Rotation.from_euler('y',tilt,degrees=True).as_matrix();kv=(world_vectors@rot)[:,[0,2]];kv=kv[ConvexHull(kv).vertices]
 print('HANDLE',tilt,kv.min(0),kv.max(0),flush=True)
 for finger,pitch,yaw in itertools.product([50,60,70,80,90],[5,10,15,20,25,30],[20,40,60]):
  vs=geometry(finger,yaw,pitch);dists=[];normals=[]
  for name,v in vs:
   v2=v[:,[0,2]];v2=v2[ConvexHull(v2).vertices]
   obstacle=(v2[:,None,:]-kv[None,:,:]).reshape(-1,2);eq=ConvexHull(obstacle).equations
   ds=centers@eq[:,:2].T+eq[:,2];ii=ds.argmax(1);d=ds[np.arange(len(centers)),ii];dists.append(d);normals.append(eq[ii,:2])
  di=next(i for i,(n,v) in enumerate(vs) if 'index_distal' in n);dt=next(i for i,(n,v) in enumerate(vs) if 'thumb_distal' in n)
  dists=np.array(dists);opp=np.sum(normals[di]*normals[dt],axis=1)
  contact_cost=(dists[di]**2+dists[dt]**2)*1e4+np.maximum(-.0003-dists,0).sum(0)*100+np.maximum(opp+.5,0)*2
  allv=np.concatenate([v for _,v in vs]);minimum=(allv@rot[2]).min()-centers@rot[2,[0,2]]
  cost=contact_cost+np.maximum(-.0095-minimum,0)*100;j=cost.argmin()
  results.append({'cost':float(cost[j]),'finger':finger,'pitch':pitch,'yaw':yaw,'tilt':tilt,'center_xz':centers[j].tolist(),'minimum_height_relative_handle':float(minimum[j]),'index_gap':float(dists[di,j]),'thumb_gap':float(dists[dt,j]),'opposition':float(opp[j])})
results.sort(key=lambda x:x['cost']);json.dump(results[:60],open('work/handle_fit_candidates.json','w'),indent=2)
for row in results[:12]:print(row)
