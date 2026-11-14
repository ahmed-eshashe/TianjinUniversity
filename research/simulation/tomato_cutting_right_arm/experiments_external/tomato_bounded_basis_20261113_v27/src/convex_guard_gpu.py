"""GPU implementation of the conservative, original-CAD clearance bound.

No contact law or material force is evaluated here. Unproved cases use the
independent CPU whole-material certificate, and never silently pass.
"""
from pathlib import Path
import numpy as np,warp as wp,time
from contact_gpu_precise import closest
from convex_guard import ConvexGuard
M43=wp.types.matrix(shape=(4,3),dtype=wp.float64)
M56=wp.types.matrix(shape=(56,3),dtype=wp.float64)

@wp.func
def plane_value(p:wp.vec3d,plane:wp.vec4d):
 return p[0]*plane[0]+p[1]*plane[1]+p[2]*plane[2]+plane[3]

@wp.func
def inside(p:wp.vec3d,planes:wp.mat44d):
 good=True
 for i in range(4):
  if plane_value(p,planes[i])>wp.float64(1e-12):good=False
 return good

@wp.kernel
def select_volume(tets:wp.array(dtype=M43),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),ids:wp.array(dtype=int)):
 i=wp.tid();a=tets[i];overlap=True
 for k in range(3):
  amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))
  if amax+wp.float64(1e-12)<lo[k] or hi[k]+wp.float64(1e-12)<amin:overlap=False
 if overlap:slot=wp.atomic_add(count,0,1);ids[slot]=i

@wp.kernel
def prove(tets:wp.array(dtype=M43),active_count:wp.array(dtype=int),active_ids:wp.array(dtype=int),cells:wp.array(dtype=M43),planes:wp.array(dtype=wp.mat44d),valid:wp.array(dtype=int),lo:wp.array(dtype=wp.vec3d),hi:wp.array(dtype=wp.vec3d),tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),target:wp.float64,unresolved:wp.array(dtype=int),upper:wp.array(dtype=wp.float64)):
 lane,c=wp.tid()
 for slot in range(lane,active_count[0],64):
  i=active_ids[slot];a=tets[i];b=cells[c];overlap=True
  for k in range(3):
   amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))
   if amax+wp.float64(1e-12)<lo[c][k] or hi[c][k]+wp.float64(1e-12)<amin:overlap=False
  if not overlap:continue
  pa=wp.mat44d(wp.float64(0.));ok=valid[c]!=0;h=wp.float64(0.)
  for u in range(4):
   for v in range(u):h=wp.max(h,wp.length(a[u]-a[v]))
  for u in range(4):
   p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)
   if size==wp.float64(0.):ok=False
   else:
    n=n/size
    if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n
    d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)
    if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False
  if not ok:wp.atomic_max(unresolved,i,1);continue
  pb=planes[c];points=M56(wp.float64(0.));count=int(0)
  for u in range(4):
   if inside(a[u],pb):points[count]=a[u];count+=1
   if inside(b[u],pa):points[count]=b[u];count+=1
  for side in range(2):
   vertices=a;other=pb;own=pa
   if side==1:vertices=b;other=pa;own=pb
   for u in range(4):
    for v in range(u):
     for k in range(4):
      d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])
      if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):
       point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])
       if inside(point,other) and inside(point,own):points[count]=point;count+=1
  if count==0:continue
  center=wp.vec3d(wp.float64(0.))
  for k in range(count):center+=points[k]
  center/=wp.float64(count);face=int(-1);best=wp.float64(1e30)
  for k in range(ptr[c],ptr[c+1]):
   j=ids[k];d=wp.length(center-closest(center,tri[j,0],tri[j,1],tri[j,2]))
   if d<best:best=d;face=j
  bound=wp.float64(0.)
  for k in range(count):bound=wp.max(bound,wp.length(points[k]-closest(points[k],tri[face,0],tri[face,1],tri[face,2])))
  if bound>target:
   for k in range(ptr[c],ptr[c+1]):
    j=ids[k];candidate=wp.float64(0.)
    for u in range(count):candidate=wp.max(candidate,wp.length(points[u]-closest(points[u],tri[j,0],tri[j,1],tri[j,2])))
    bound=wp.min(bound,candidate)
    if bound<=target:break
  wp.atomic_max(upper,0,bound)
  if bound>target:wp.atomic_max(unresolved,i,1)

class GPUConvexGuard(ConvexGuard):
 def __init__(self,cad):
  super().__init__(cad);self.dcells=wp.array(self.cells,dtype=M43,device='cuda:0');self.dp=wp.array(self.planes,dtype=wp.mat44d,device='cuda:0');self.dv=wp.array(self.valid.astype(np.int32),dtype=int,device='cuda:0');self.dlo=wp.array(self.lo,dtype=wp.vec3d,device='cuda:0');self.dhi=wp.array(self.hi,dtype=wp.vec3d,device='cuda:0');self.dtri=wp.array(self.tri,dtype=wp.vec3d,device='cuda:0');self.dptr=wp.array(self.ptr,dtype=int,device='cuda:0');self.dids=wp.array(self.ids,dtype=int,device='cuda:0');self.cached={}
 def certify(self,tets,T,R=None,limit=.0001,motion=0.,maxdepth=24,allowance=2e-6):
  from blade_geometry import certify
  start=time.perf_counter();R=self.cad.R if R is None else R;local=(np.asarray(tets)-T)@R;n=len(local);threshold=limit-motion-allowance
  if threshold<=0:return dict(passed=False,reason='motion_exceeds_certificate_budget',motion_bound_m=motion)
  if n not in self.cached:self.cached[n]=(wp.empty(n,dtype=M43,device='cuda:0'),wp.zeros(n,dtype=int,device='cuda:0'),wp.zeros(1,dtype=wp.float64,device='cuda:0'),wp.zeros(1,dtype=int,device='cuda:0'),wp.empty(n,dtype=int,device='cuda:0'))
  dtets,failed,upper,active_count,active_ids=self.cached[n];dtets.assign(local);failed.zero_();upper.zero_();active_count.zero_();wp.launch(select_volume,n,[dtets,wp.vec3d(self.lo.min(0)),wp.vec3d(self.hi.max(0)),active_count,active_ids]);wp.launch(prove,(64,len(self.cells)),[dtets,active_count,active_ids,self.dcells,self.dp,self.dv,self.dlo,self.dhi,self.dtri,self.dptr,self.dids,threshold,failed,upper]);unresolved=failed.numpy().astype(bool);raw=float(upper.numpy()[0]);fallback=None
  if unresolved.any():fallback=certify(np.asarray(tets)[unresolved],self.cad,T,R,limit=limit,motion=motion,maxdepth=maxdepth,allowance=allowance)
  passed=fallback is None or fallback['passed'];return dict(passed=bool(passed),reason='GPU_original_CAD_convex_distance_bound' if passed else fallback['reason'],bound_m=raw+motion+allowance if fallback is None else None,raw_bound_m=raw+motion+allowance,total_tets=n,candidate_tets=int(active_count.numpy()[0]),fallback_tets=int(unresolved.sum()),fallback=fallback,wall_s=time.perf_counter()-start,motion_bound_m=motion)
