"""Validated on-disk cache of immutable surface maps; independent live state."""
import hashlib,numpy as np
from scipy.sparse import csr_matrix
from poly_surface import Surface
FIELDS=['triangles','tri_owner','ref_normals','X','owner','tri_area','area','volume_tets','volume_owner']
MATS=['Q0','Q','volume_Q']
def signature(a):
 h=hashlib.sha256()
 for x in [a.body.grid,a.body.ids,a.body.inv,a.body.codes,a.body.poly_ptr,a.body.poly_vertices,a.E.indptr,a.E.indices,a.E.data]:
  z=np.ascontiguousarray(x);h.update(str(z.dtype).encode());h.update(str(z.shape).encode());h.update(z.tobytes())
 return h.hexdigest()
def cached_surface(a,path):
 import json,time
 start=time.perf_counter();key=signature(a)
 if path.exists():
  z=np.load(path,allow_pickle=False)
  if str(z['signature'])!=key:raise ValueError('surface cache geometry/operator mismatch')
  s=Surface.__new__(Surface);s.a=a
  for k in FIELDS:setattr(s,k,z[k])
  for k in MATS:setattr(s,k,csr_matrix((z[k+'_data'],z[k+'_indices'],z[k+'_indptr']),shape=tuple(z[k+'_shape'])))
  s.metadata=json.loads(str(z['metadata']));s.cache_hit=True
 else:
  s=Surface(a);data={k:getattr(s,k) for k in FIELDS}
  for k in MATS:
   m=getattr(s,k);data.update({k+'_data':m.data,k+'_indices':m.indices,k+'_indptr':m.indptr,k+'_shape':m.shape})
  np.savez_compressed(path,signature=key,metadata=json.dumps(s.metadata),**data);s.cache_hit=False
 s.cache_seconds=time.perf_counter()-start;return s
