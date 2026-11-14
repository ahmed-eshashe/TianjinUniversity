"""Current-state adaptive contact integration; original CAD and physical law.

Convex hull is ONLY a conservative zero-force domain exclusion. Signed distance,
normal and friction always use the original nonconvex triangle mesh.
"""
import numpy as np,warp as wp
from scipy.sparse import coo_matrix
from pathlib import Path
from adaptive_reference import facets
from contact_surface import Surface
from contact_gpu_precise import ContactGPU as Base,closest
from contact_reductions import pullback_parallel,force_parts,force_guard
from persistent_gpu import gather

class TriangleSurface(Surface):
 def __init__(self,a):
  ids,X,area=facets(a);self.face_ids=ids;self.X=X.reshape(-1,3);self.tri_area=area;self.area=np.repeat(area/3,3);self.a=a
  self.Q0=coo_matrix((np.ones(ids.size),(np.arange(ids.size),ids.ravel())),shape=(ids.size,len(a.body.u))).tocsr();self.Q=(self.Q0@a.E).tocsr()

@wp.struct
class Signed:
 phi:wp.float64
 normal:wp.vec3d

@wp.func
def signed(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),p:wp.vec3d):
 r=Signed();r.phi=wp.float64(100.);r.normal=wp.vec3d(wp.float64(0.));q=wp.mesh_query_point_sign_winding_number(mesh,wp.vec3(p),10.)
 if q.result:
  c=closest(p,tri[q.face,0],tri[q.face,1],tri[q.face,2]);best=wp.length_sq(p-c);bestface=q.face
  # The float nearest-face routine is unreliable for thin CAD triangles.
  # Its candidate still supplies an upper bound. Expand for float BVH rounding,
  # then evaluate every intersecting original triangle in double precision.
  radius=wp.sqrt(best)+wp.float64(2e-7)
  candidates=wp.mesh_query_aabb(mesh,wp.vec3(p-wp.vec3d(radius)),wp.vec3(p+wp.vec3d(radius)))
  for face in candidates:
   candidate=closest(p,tri[face,0],tri[face,1],tri[face,2]);dist=wp.length_sq(p-candidate)
   if dist<best or (dist==best and face<bestface):best=dist;c=candidate;bestface=face
  d=p-c;l=wp.sqrt(best);r.phi=wp.float64(q.sign)*l
  if l>wp.float64(1e-15):r.normal=wp.float64(q.sign)*d/l
  else:r.normal=wp.normalize(wp.cross(tri[bestface,1]-tri[bestface,0],tri[bestface,2]-tri[bestface,0]))
 return r

@wp.struct
class Value:
 f:wp.mat33d
 U:wp.float64
 D:wp.float64
 W:wp.float64
 moment:wp.vec3d
 error:wp.float64
 queries:int

@wp.func
def bisect(B:wp.mat33d,X:wp.mat33d):
 p=B*X;i=int(0);j=int(1);best=wp.length_sq(p[0]-p[1])
 for u in range(3):
  for v in range(u+1,3):
   d=wp.length_sq(p[u]-p[v])
   if d>best:best=d;i=u;j=v
 mid=(B[i]+B[j])*wp.float64(.5);L=B;H=B
 for k in range(3):L[i,k]=mid[k];H[j,k]=mid[k]
 return L,H

@wp.func
def evaluate_leaf(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),B:wp.mat33d,X:wp.mat33d,V:wp.mat33d,A:wp.float64,R:wp.mat33d,T:wp.vec3d,tv:wp.vec3d):
 r=Value();r.f=wp.mat33d(wp.float64(0.));r.U=wp.float64(0.);r.D=wp.float64(0.);r.W=wp.float64(0.);r.moment=wp.vec3d(wp.float64(0.));r.error=wp.float64(0.);r.queries=1
 p=B*X;c=(p[0]+p[1]+p[2])/wp.float64(3.);radius=wp.max(wp.length(p[0]-c),wp.max(wp.length(p[1]-c),wp.length(p[2]-c)));sd=signed(mesh,tri,wp.transpose(R)*(c-T));Ar=A*wp.abs(wp.determinant(B))
 if sd.phi<=radius+wp.float64(2e-9):
  L,H=bisect(B,X);low=wp.mat33d(wp.float64(0.));active=False
  for k in range(9):
   block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)
   if block==1:C=L;weight=Ar/wp.float64(6.)
   elif block==2:C=H;weight=Ar/wp.float64(6.)
   bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1
   if s.phi<wp.float64(0.):
    active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))
    if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed
    f=fn*normal+fr
    for u in range(3):
     for v0 in range(3):
      if block==0:low[u,v0]+=bary[u]*f[v0]
      else:r.f[u,v0]+=bary[u]*f[v0]
    if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)
  for u in range(3):r.error+=wp.length(r.f[u]-low[u])
  # Exact CAD-interior partition; no unresolved outside-contact region.
 return r

@wp.kernel
def integrate(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),bbmin:wp.vec3d,bbmax:wp.vec3d,planes:wp.array2d(dtype=wp.vec4d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),areas:wp.array(dtype=wp.float64),area_total:wp.float64,q:wp.array(dtype=wp.vec3),vel:wp.array(dtype=wp.vec3),polygon:wp.array3d(dtype=wp.vec3d),Bs:wp.array2d(dtype=wp.mat33d),vals:wp.array2d(dtype=Value),depths:wp.array2d(dtype=int),counts:wp.array(dtype=int),query_counts:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),cap:int,relative_tol:wp.float64,absolute_tol:wp.float64,maxdepth:int):
 pair=wp.tid();face=pair//ncells;cell=pair%ncells;X=wp.mat33d(wp.float64(0.));V=wp.mat33d(wp.float64(0.));local=wp.mat33d(wp.float64(0.));t=clock[0];shape=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)
 if t<load:shape=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)
 elif t<load+hold:shape=wp.float64(1.)
 elif t<wp.float64(2.)*load+hold:
  z=(t-load-hold)/load;shape=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*z));speed=-wp.float64(.5)*pi/load*wp.sin(pi*z)
 T=T0+travel*shape;tv=travel*speed
 for vertex in range(3):
  k=3*face+vertex;x=ref[k];v=wp.vec3d(wp.float64(0.))
  for j in range(ptr[k],ptr[k+1]):x+=w[j]*wp.vec3d(q[ids[j]]);v+=w[j]*wp.vec3d(vel[ids[j]])
  xp=wp.transpose(R)*(x-T)
  for j in range(3):X[vertex,j]=x[j];V[vertex,j]=v[j];local[vertex,j]=xp[j]
  out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)
 counts[pair]=0;query_counts[pair]=0
 intersects=True
 for axis in range(3):
  lo=wp.min(local[0,axis],wp.min(local[1,axis],local[2,axis]));hi=wp.max(local[0,axis],wp.max(local[1,axis],local[2,axis]))
  if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False
 if intersects and bad[0]==0:
  for k in range(3):unit=wp.vec3d(wp.float64(0.));unit[k]=wp.float64(1.);polygon[pair,0,k]=unit
  n=int(3);src=int(0);dst=int(1)
  for h in range(4):
   plane=planes[cell,h];normal=wp.vec3d(plane[0],plane[1],plane[2]);distance=local*normal+wp.vec3d(plane[3]);nnew=int(0)
   for k in range(n):
    p0=polygon[pair,src,k];p1=polygon[pair,src,(k+1)%n];d0=wp.dot(p0,distance);d1=wp.dot(p1,distance)
    if d0<=wp.float64(0.):
     if nnew>=10:wp.atomic_max(bad,0,6)
     else:polygon[pair,dst,nnew]=p0;nnew+=1
    if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):
     if nnew>=10:wp.atomic_max(bad,0,6)
     else:polygon[pair,dst,nnew]=p0+d0/(d0-d1)*(p1-p0);nnew+=1
   n=nnew;tmp=src;src=dst;dst=tmp
   if n<3:break
  if n>=3 and bad[0]==0:
   total=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.));err=wp.float64(0.);count=int(0);queries=int(0)
   for k in range(1,n-1):
    B=wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,k],polygon[pair,src,k+1]);r=evaluate_leaf(mesh,tri,B,X,V,areas[face],R,T,tv);Bs[pair,count]=B;vals[pair,count]=r;depths[pair,count]=0;count+=1;total+=r.f;U+=r.U;D+=r.D;W+=r.W;M+=r.moment;err+=r.error;queries+=r.queries
   atol=absolute_tol*areas[face]/(area_total*wp.float64(ncells));fscale=wp.float64(0.)
   for k in range(3):fscale+=wp.length(total[k])
   while err>atol+relative_tol*fscale and bad[0]==0:
    if count>=cap:wp.atomic_max(bad,0,5);break
    worst=int(0);worsterr=wp.float64(-1.)
    for k in range(count):
     if vals[pair,k].error>worsterr:worst=k;worsterr=vals[pair,k].error
    depth=depths[pair,worst]
    if depth>=maxdepth:wp.atomic_max(bad,0,7);break
    B=Bs[pair,worst];old=vals[pair,worst];L,H=bisect(B,X);a=evaluate_leaf(mesh,tri,L,X,V,areas[face],R,T,tv);b=evaluate_leaf(mesh,tri,H,X,V,areas[face],R,T,tv)
    total+=a.f+b.f-old.f;U+=a.U+b.U-old.U;D+=a.D+b.D-old.D;W+=a.W+b.W-old.W;M+=a.moment+b.moment-old.moment;err+=a.error+b.error-old.error;queries+=a.queries+b.queries
    Bs[pair,worst]=L;vals[pair,worst]=a;depths[pair,worst]=depth+1;Bs[pair,count]=H;vals[pair,count]=b;depths[pair,count]=depth+1;count+=1;fscale=wp.float64(0.)
    for k in range(3):fscale+=wp.length(total[k])
   counts[pair]=count;query_counts[pair]=queries
   if bad[0]==0:
    for vertex in range(3):
     k=3*pair+vertex;cf[k]=wp.vec3(total[vertex]);cu[k]=float(U/wp.float64(3.));cp[k]=float(D/wp.float64(3.));power[k]=float(W/wp.float64(3.));moment[k]=wp.vec3(M/wp.float64(3.))


@wp.kernel
def collect(ncells:int,ff:wp.array(dtype=wp.vec3),uu:wp.array(dtype=float),dd:wp.array(dtype=float),ww:wp.array(dtype=float),mm:wp.array(dtype=wp.vec3),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3)):
 k=wp.tid();face=k//3;vertex=k%3;f=wp.vec3d(wp.float64(0.));u=wp.float64(0.);d=wp.float64(0.);w=wp.float64(0.);m=wp.vec3d(wp.float64(0.))
 for c in range(ncells):
  j=(face*ncells+c)*3+vertex;f+=wp.vec3d(ff[j]);u+=wp.float64(uu[j]);d+=wp.float64(dd[j]);w+=wp.float64(ww[j]);m+=wp.vec3d(mm[j])
 cf[k]=wp.vec3(f);cu[k]=float(u);cp[k]=float(d);power[k]=float(w);moment[k]=wp.vec3(m)

class ContactGPU(Base):
 def __init__(self,*args,relative_tol=.002,absolute_tol=1e-6,capacity=256,maxdepth=32,**kwargs):
  self.adaptive=False;super().__init__(*args,**kwargs);self.nfaces=len(self._surface.tri_area);self.capacity=capacity;self.relative_tol=relative_tol;self.absolute_tol=absolute_tol;self.maxdepth=maxdepth
  z=np.load(Path(__file__).resolve().parents[1]/'assets/blade_partition.npz');cells=z['x'][z['tets']];self.ncells=len(cells);self.npairs=self.nfaces*self.ncells
  self.planes=wp.array(z['planes'],dtype=wp.vec4d,device='cuda:0');self.cellbounds=wp.array(np.stack([cells.min(1),cells.max(1)],axis=1),dtype=wp.vec3d,device='cuda:0');self.areas=wp.array(self._surface.tri_area,dtype=wp.float64,device='cuda:0');self.area_total=float(sum(self._surface.tri_area))
  self.polygon=wp.empty((self.npairs,2,10),dtype=wp.vec3d,device='cuda:0');self.Bs=wp.empty((self.npairs,capacity),dtype=wp.mat33d,device='cuda:0');self.vals=wp.empty((self.npairs,capacity),dtype=Value,device='cuda:0');self.depths=wp.empty((self.npairs,capacity),dtype=int,device='cuda:0');self.leaves=wp.zeros(self.npairs,dtype=int,device='cuda:0');self.queries=wp.zeros(self.npairs,dtype=int,device='cuda:0')
  self.pf=wp.zeros(3*self.npairs,dtype=wp.vec3,device='cuda:0');self.pu=wp.zeros(3*self.npairs,dtype=float,device='cuda:0');self.pd=wp.zeros(3*self.npairs,dtype=float,device='cuda:0');self.pw=wp.zeros(3*self.npairs,dtype=float,device='cuda:0');self.pm=wp.zeros(3*self.npairs,dtype=wp.vec3,device='cuda:0');self.adaptive=True
 def contact_force(self):
  if not self.adaptive:return super().contact_force()
  wp.launch(integrate,self.npairs,[self.cad.mesh.id,self.tri,wp.vec3d(self.cad.vertices.min(0)-2e-6),wp.vec3d(self.cad.vertices.max(0)+2e-6),self.planes,self.cellbounds,self.ncells,wp.mat33d(self.R),wp.vec3d(self.T0),wp.vec3d(self.travel),wp.float64(self.load),wp.float64(self.hold),self.clock,self.sptr,self.sids,self.sw,self.reference,self.areas,wp.float64(self.area_total),self.q,self.vh,self.polygon,self.Bs,self.vals,self.depths,self.leaves,self.queries,self.pf,self.pu,self.pd,self.pw,self.pm,self.bad,self.capacity,wp.float64(self.relative_tol),wp.float64(self.absolute_tol),self.maxdepth],block_dim=32)
  wp.launch(collect,self.ns,[self.ncells,self.pf,self.pu,self.pd,self.pw,self.pm,self.cf,self.cu,self.cp,self.power,self.moment])
  wp.launch(pullback_parallel,((self.n+3)//4)*128,[self.cptr,self.cids,self.cw,self.cf,self.external,self.n],block_dim=128);wp.launch(force_parts,self.nparts,[self.cf,self.part_sum,self.part_mag,self.ns]);wp.launch(force_guard,1,[self.part_sum,self.part_mag,self.bad,self.peak,self.nparts]);self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
