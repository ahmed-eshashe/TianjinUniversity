"""Same conservative CAD proof, evaluated on device between substep blocks.

Unresolved cases stop explicitly. No CPU fallback is silently omitted: it can
be invoked by the caller after rollback, with the failing state retained.
"""
import numpy as np,warp as wp
from convex_guard_gpu import M43,M56,inside,plane_value,select_volume
from contact_gpu_precise import closest

@wp.kernel
def map_volume(ref:wp.array(dtype=M43),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),weights:wp.array(dtype=wp.float64),q:wp.array(dtype=wp.vec3),pose:wp.array(dtype=wp.vec3d),R:wp.mat33d,local:wp.array(dtype=M43)):
 i=wp.tid();out=M43(wp.float64(0.))
 for u in range(4):
  row=4*i+u;x=ref[i][u]
  for j in range(ptr[row],ptr[row+1]):x+=weights[j]*wp.vec3d(q[ids[j]])
  out[u]=wp.transpose(R)*(x-pose[0])
 local[i]=out

@wp.kernel
def map_near_volume(ref:wp.array(dtype=M43),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),weights:wp.array(dtype=wp.float64),q:wp.array(dtype=wp.vec3),pose:wp.array(dtype=wp.vec3d),R:wp.mat33d,parent:wp.array2d(dtype=int),owner:wp.array(dtype=int),corners:wp.array(dtype=wp.vec3d),roundoff:wp.array(dtype=wp.vec3d),lo:wp.vec3d,hi:wp.vec3d,local:wp.array(dtype=M43),count:wp.array(dtype=int),active:wp.array(dtype=int)):
 i=wp.tid();r=owner[i];overlap=True
 for k in range(3):
  low=wp.float64(1e30);high=wp.float64(-1e30)
  for j in range(4):low=wp.min(low,corners[parent[r,j]][k]);high=wp.max(high,corners[parent[r,j]][k])
  mag=wp.max(wp.abs(low),wp.abs(high));err=roundoff[i][0]*(high-low)+roundoff[i][1]*mag+roundoff[i][2]+wp.float64(1e-10)*(wp.float64(1.)+mag)
  if high+err<lo[k] or low-err>hi[k]:overlap=False
 if not overlap:return
 out=M43(wp.float64(0.))
 for u in range(4):
  row=4*i+u;x=ref[i][u]
  for j in range(ptr[row],ptr[row+1]):x+=weights[j]*wp.vec3d(q[ids[j]])
  out[u]=wp.transpose(R)*(x-pose[0])
 local[i]=out;overlap=True
 for k in range(3):
  low=wp.min(wp.min(out[0,k],out[1,k]),wp.min(out[2,k],out[3,k]));high=wp.max(wp.max(out[0,k],out[1,k]),wp.max(out[2,k],out[3,k]))
  if high+wp.float64(1e-12)<lo[k] or low-wp.float64(1e-12)>hi[k]:overlap=False
 if overlap:slot=wp.atomic_add(count,0,1);active[slot]=i

@wp.kernel
def set_target(speed:wp.array(dtype=float),vmax:wp.float64,interval:wp.float64,target:wp.array(dtype=wp.float64),bad:wp.array(dtype=int)):
 target[0]=wp.float64(.0001)-wp.float64(.000002)-(wp.float64(speed[0])+vmax)*interval
 if target[0]<=wp.float64(0.):wp.atomic_max(bad,0,4)

@wp.kernel
def reject_unresolved(flags:wp.array(dtype=int),bad:wp.array(dtype=int)):
 i=wp.tid()
 if flags[i]!=0:wp.atomic_max(bad,0,4)

@wp.kernel
def record_force(face_count:wp.array(dtype=int),face_ids:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),trace:wp.array(dtype=wp.float64),cursor:wp.array(dtype=int),bad:wp.array(dtype=int)):
 k=cursor[0]
 if bad[0]!=0:return
 if k>=trace.shape[0]:wp.atomic_max(bad,0,5);return
 value=wp.float64(0.)
 for i in range(face_count[0]):
  face=face_ids[i]
  for u in range(3):value+=wp.float64(wp.length(cf[3*face+u]))
 trace[k]=value;cursor[0]=k+1

@wp.kernel
def prove_at_target(tets:wp.array(dtype=M43),active_count:wp.array(dtype=int),active_ids:wp.array(dtype=int),cells:wp.array(dtype=M43),planes:wp.array(dtype=wp.mat44d),valid:wp.array(dtype=int),lo:wp.array(dtype=wp.vec3d),hi:wp.array(dtype=wp.vec3d),tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),target:wp.array(dtype=wp.float64),unresolved:wp.array(dtype=int),upper:wp.array(dtype=wp.float64)):
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
  if bound>target[0]:
   for k in range(ptr[c],ptr[c+1]):
    j=ids[k];candidate=wp.float64(0.)
    for u in range(count):candidate=wp.max(candidate,wp.length(points[u]-closest(points[u],tri[j,0],tri[j,1],tri[j,2])))
    bound=wp.min(bound,candidate)
    if bound<=target[0]:break
  wp.atomic_max(upper,0,bound)
  if bound>target[0]:wp.atomic_max(unresolved,i,1)

class ResidentProof:
 def __init__(self,g,proof,trace_capacity=4096):
  self.g=g;self.guard=proof.guard;
  b=g.aggregates[0].body;X=proof.tets0.reshape(-1,3);owner=np.repeat(proof.owners,4);N=np.einsum('pi,pij->pj',np.c_[np.ones(len(X)),X],b.inv[owner]);res=X-np.einsum('pi,pij->pj',N,b.grid[b.ids[owner]]);negative=np.maximum(-N,0).sum(1).reshape(-1,4).max(1);unit=np.abs(N.sum(1)-1).reshape(-1,4).max(1);offset=np.linalg.norm(res,axis=1).reshape(-1,4).max(1);self.owners=wp.array(proof.owners,dtype=int,device='cuda:0');self.roundoff=wp.array(np.c_[negative,unit,offset],dtype=wp.vec3d,device='cuda:0');self.n=len(proof.tets0);self.graphs={}
  self.ref=wp.array(proof.tets0,dtype=M43,device='cuda:0');self.local=wp.empty(self.n,dtype=M43,device='cuda:0')
  for key,value,dtype in [('ptr',proof.Q.indptr,int),('ids',proof.Q.indices,int),('weights',proof.Q.data,wp.float64)]:setattr(self,key,wp.array(value,dtype=dtype,device='cuda:0'))
  self.active_count=wp.zeros(1,dtype=int,device='cuda:0');self.active_ids=wp.empty(self.n,dtype=int,device='cuda:0');self.failed=wp.zeros(self.n,dtype=int,device='cuda:0');self.upper=wp.zeros(1,dtype=wp.float64,device='cuda:0');self.target=wp.zeros(1,dtype=wp.float64,device='cuda:0');self.trace=wp.zeros(trace_capacity,dtype=wp.float64,device='cuda:0');self.cursor=wp.zeros(1,dtype=int,device='cuda:0')
 def certify(self,n):
  g=self.g;c=self.guard;self.active_count.zero_();self.failed.zero_();self.upper.zero_()
  wp.launch(map_near_volume,self.n,[self.ref,self.ptr,self.ids,self.weights,g.q,g.toolpose,wp.mat33d(g.R),g.hparent,self.owners,g.hcorners,self.roundoff,wp.vec3d(c.lo.min(0)),wp.vec3d(c.hi.max(0)),self.local,self.active_count,self.active_ids])
  wp.launch(set_target,1,[g.maxspeed,wp.float64(np.linalg.norm(g.travel)*.5*np.pi/g.load),wp.float64(n*g.dt),self.target,g.bad])
  wp.launch(prove_at_target,(64,len(c.cells)),[self.local,self.active_count,self.active_ids,c.dcells,c.dp,c.dv,c.dlo,c.dhi,c.dtri,c.dptr,c.dids,self.target,self.failed,self.upper]);wp.launch(reject_unresolved,self.n,[self.failed,g.bad]);wp.launch(record_force,1,[g.face_count,g.face_ids,g.cf,self.trace,self.cursor,g.bad])
 def graph(self,n):
  if n not in self.graphs:
   g=self.g;wp.load_module(device='cuda:0')
   with wp.ScopedStream(g.stream):
    wp.capture_begin(device='cuda:0')
    try:
     g.maxspeed.zero_()
     for _ in range(n):g.one()
     g.contact_force();self.certify(n)
    finally:self.graphs[n]=wp.capture_end(device='cuda:0')
  return self.graphs[n]
 def step_async(self,n,block=10):
  g=self.g
  if g.pending is not None:raise ValueError('unfinished step')
  full,rem=divmod(n,block);graphs=[self.graph(block)]*full
  if rem:graphs.append(self.graph(rem))
  with wp.ScopedStream(g.stream):
   wp.copy(g.backup[0],g.q);wp.copy(g.backup[1],g.vh)
   for k,v in g.tx.items():wp.copy(v,g.ca[k])
   g.bad.zero_();self.cursor.zero_()
   for graph in graphs:wp.capture_launch(graph)
   wp.copy(g.host_q,g.q,count=g.n);wp.copy(g.host_v,g.vh,count=g.n);wp.copy(g.host_bad,g.bad)
  g.pending=n
