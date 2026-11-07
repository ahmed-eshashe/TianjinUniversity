"""Cache only immutable local-CAD partition-plane coefficients.
Current tissue geometry, quadrature, CAD queries and all tolerances are unchanged.
The cache key includes every blade vertex, face and selected face identifier.
"""
import numpy as np
from functools import lru_cache
from tomato_compiled_plane_partition import compute

@lru_cache(maxsize=512)
def coefficients(vertex_bytes,face_bytes,selected):
 blade=dict(vertices=np.frombuffer(vertex_bytes,dtype=np.float64).reshape(-1,3),triangles=np.frombuffer(face_bytes,dtype=np.int64).reshape(-1,3));face_ids=selected
 vertices=np.asarray(blade['vertices']);faces=np.asarray(blade['triangles']);planes=[]
 for face in face_ids:
  a,b,c=vertices[faces[int(face)]];n=np.cross(b-a,c-a);n/=np.linalg.norm(n);d=float(n@a)
  if not any(np.linalg.norm(n-old_n)<1e-6 and abs(d-old_d)<1e-8 for old_n,old_d in planes):planes.append((n,d))
 original=list(planes)
 for i,(n,d) in enumerate(original):
  for m,e in original[i+1:]:
   normal=n-m;length=np.linalg.norm(normal)
   if length>1e-6:planes.append((normal/length,(d-e)/length))
 normals=np.asarray([p[0]for p in planes]).reshape(-1,3);offsets=np.asarray([p[1]for p in planes]);normals.setflags(write=False);offsets.setflags(write=False);return normals,offsets,len(original)

def partition(blade,ids,leaves,areas,x,rotation,translation,face_ids):
 normals,offsets,original_count=coefficients(np.asarray(blade['vertices'],dtype=np.float64).tobytes(),np.asarray(blade['triangles'],dtype=np.int64).tobytes(),tuple(int(i)for i in face_ids))
 ni,nc,na,fallbacks=compute(np.asarray(ids),np.asarray(leaves),np.asarray(areas),np.asarray(x),np.asarray(rotation),np.asarray(translation),normals,offsets)
 if abs(sum(na)-sum(areas))>1e-12*max(sum(areas),1e-12):raise ValueError('Partition lost material reference area')
 return np.asarray(ni),np.asarray(nc),np.asarray(na),dict(unpartitioned_roundoff_fallbacks=fallbacks,face_planes=original_count,partition_planes=len(normals),original_cells=len(leaves),partitioned_cells=len(nc))
