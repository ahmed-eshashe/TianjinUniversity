"""Same geometric split as v19, reusing untouched material moments.

Only potentially intersected polyhedra need convex clipping. History labels and
node sharing are identical to the reference. This is not a fracture law.
"""
import time,functools,copy
from surface_geometry import Surface
from packed_polys import PackedPolys
from update_kernels import labels,fields as fast_fields,metrics as fast_metrics
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from reference_v17 import Body as ReferenceBody,clip,moments,compatible

@functools.lru_cache(maxsize=4096)
def groups_for(codes):
 adj=np.array([[compatible(i,j) for j in codes] for i in codes])
 return connected_components(csr_matrix(adj),directed=False)

def labels_to_nodes(oldids,codes,nold):
 flat=oldids.ravel();pairs=np.c_[flat,np.repeat(codes,4)]
 unique,inverse=np.unique(pairs,axis=0,return_inverse=True)
 counts=np.bincount(unique[:,0],minlength=nold);bounds=np.r_[0,np.cumsum(counts)]
 mapping=np.zeros(len(unique),int);nc=np.ones(nold,int)
 for a in np.flatnonzero(counts>1):
  lo,hi=bounds[a:a+2];nc[a],mapping[lo:hi]=groups_for(tuple(unique[lo:hi,1]))
 if np.any(counts==0):raise ValueError('orphaned reference node')
 base=np.r_[0,np.cumsum(nc[:-1])];mapping+=base[unique[:,0]]
 return mapping[inverse].reshape(oldids.shape),np.repeat(np.arange(nold),nc)

class Body(ReferenceBody):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.freeze_geometry()
 def freeze_geometry(self):
  if not isinstance(self.polys,PackedPolys):
   self.polys=PackedPolys(np.r_[0,np.cumsum([len(p) for p in self.polys])],np.concatenate(self.polys))
  self.poly_ptr=self.polys.ptr;self.poly_vertices=self.polys.vertices
  for key in ['grid','ids','inv','G','V','X','N','codes','mass','ptr','edge_p','edge_g']:
   getattr(self,key).flags.writeable=False
  return self
 def clone(self):
  # Geometry is immutable. Independent state and history remain owned by clone.
  out=copy.copy(self);out.u=self.u.copy();out.v=self.v.copy();out.history=copy.deepcopy(self.history);return out
 @classmethod
 def restore(cls,path):
  return super().restore(path).freeze_geometry()
 def fields(self,u=None,v=None):
  return fast_fields(self.ids,self.G,self.N,self.X,self.u if u is None else u,self.v if v is None else v)
 def metrics(self):
  U,T,p,L=fast_metrics(self.ids,self.G,self.V,self.grid,self.mass,self.u,self.v,self.mu,self.lam)
  return dict(mass=float(self.mass.sum()),volume=float(self.V.sum()),U=float(U),T=float(T),momentum=p,angular=L)

 def prepare_geometry_cache(self):
  if not hasattr(self,'_surface'):self._surface=Surface(self.polys)
  if hasattr(self,'_moment_V'):return
  mv=[moments(p) for p in self.polys]
  self._moment_V=np.array([m[0] for m in mv]);self._moment_X=np.array([m[1] for m in mv])
 def split(self,normal,offset,cut_id=0,front=None,world=False):
  if cut_id not in range(4):raise ValueError('four-cut capacity exceeded')
  start=time.perf_counter();self.prepare_geometry_cache();oldfields=self.fields();before=self.metrics()
  def mapped(n,d):
   n=np.asarray(n,dtype=float)
   if world:
    ns=np.einsum('pji,j->pi',oldfields[2],n);trans=oldfields[0]-np.einsum('pij,pj->pi',oldfields[2],self.X);ds=float(d)-trans@n
   else:ns=np.broadcast_to(n,(len(self.polys),3));ds=np.full(len(self.polys),float(d))
   return ns,ds
  cn,cd=mapped(normal,offset)
  if front is not None:fn,fd=mapped(*front)
  result=self._surface.event(self.codes,self._moment_V,self._moment_X,cn,cd,fn if front is not None else None,fd if front is not None else None,cut_id)
  newpolys=result['polys'];origin=result['origin'];codes=result['codes'];vol=result['V'];cent=result['X'];changed=result['changed'];clipped_parents=set()
  origin=np.asarray(origin);out=self.clone();out.polys=newpolys;out.codes=np.asarray(codes);out.inv=self.inv[origin].copy();out.G=self.G[origin].copy();out.V=np.asarray(vol);out.X=np.asarray(cent);out.N=np.einsum('pi,pij->pj',np.c_[np.ones(len(vol)),out.X],out.inv)
  if np.min(out.N)<-1e-11:raise ValueError('clipped centroid outside parent; no renormalization')
  oldids=self.ids[origin];out.ids,parents=labels(oldids,out.codes,len(self.u));out.grid=self.grid[parents].copy();out.u=self.u[parents].copy();out.v=self.v[parents].copy();out.rebuild()
  after=out.metrics();nf=out.fields();expected_x=out.X+np.einsum('pi,pij->pj',out.N,self.u[oldids]);expected_v=np.einsum('pi,pij->pj',out.N,self.v[oldids]);err={'x':float(np.max(abs(nf[0]-expected_x))),'v':float(np.max(abs(nf[1]-expected_v))),'F':float(np.max(abs(nf[2]-oldfields[2][origin])))}
  for k in ['mass','volume','U','T','momentum','angular']:err[k]=float(np.linalg.norm(np.asarray(after[k])-before[k]))
  if max(err[k] for k in ['x','v','F'])>1e-10 or err['mass']>before['mass']*1e-6 or any(err[k]>max(1e-12,abs(before[k])*1e-6) for k in ['U','T']):raise ValueError(('cut transfer failed',err))
  out.history.append({'cut_id':cut_id,'normal':list(normal),'offset':offset,'front':None if front is None else [list(front[0]),front[1]],'world':world,'geometry_only':True,'regions_before':len(self.X),'regions_after':len(out.X),'groups_before':len(self.u),'groups_after':len(out.u),'transfer':err})
  out._moment_V=out.V.copy();out._moment_X=out.X.copy();out._surface=result['surface']
  out.last_update={'wall_s':time.perf_counter()-start,'recomputed_regions':changed,'native_geometry':True,'reused_regions':len(vol)-changed,'total_regions':len(vol)}
  out.freeze_geometry();self.__dict__.update(out.__dict__);return err
