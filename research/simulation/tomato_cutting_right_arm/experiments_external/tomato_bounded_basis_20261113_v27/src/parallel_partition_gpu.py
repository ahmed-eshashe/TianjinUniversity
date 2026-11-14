"""Parallel quadrature on exact current CAD-intersection polygons.

Reference law/geometry preserved. Quadrature resolution must pass independent
refinement; this implementation does not claim an adaptive error certificate.
"""
from pathlib import Path
import numpy as np,warp as wp
from adaptive_gpu import TriangleSurface
from contact_gpu_precise import ContactGPU as Base
from exact_cad_gpu import signed
from contact_reductions import pullback_parallel,force_parts,force_guard
from persistent_gpu import gather

@wp.kernel
def frame(R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),local:wp.array(dtype=wp.mat33d),pose:wp.array(dtype=wp.vec3d)):
 face=wp.tid();t=clock[0];shape=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)
 if t<load:shape=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)
 elif t<load+hold:shape=wp.float64(1.)
 elif t<wp.float64(2.)*load+hold:
  z=(t-load-hold)/load;shape=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*z));speed=-wp.float64(.5)*pi/load*wp.sin(pi*z)
 T=T0+travel*shape;tv=travel*speed
 if face==0:pose[0]=T;pose[1]=tv
 xx=wp.mat33d(wp.float64(0.));vv=wp.mat33d(wp.float64(0.));ll=wp.mat33d(wp.float64(0.))
 for u in range(3):
  i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))
  for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])
  p=wp.transpose(R)*(x-T)
  for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]
 X[face]=xx;V[face]=vv;local[face]=ll

@wp.kernel
def domains(local:wp.array(dtype=wp.mat33d),planes:wp.array2d(dtype=wp.vec4d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,polygon:wp.array3d(dtype=wp.vec3d),polycounts:wp.array(dtype=int),sources:wp.array(dtype=int),active:wp.array(dtype=int),active_ids:wp.array(dtype=int),capacity:int,bad:wp.array(dtype=int)):
 pair=wp.tid();face=pair//ncells;cell=pair%ncells;x=local[face];inside=True;polycounts[pair]=0
 for axis in range(3):
  lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))
  if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:inside=False
 if inside and bad[0]==0:
  for k in range(3):unit=wp.vec3d(wp.float64(0.));unit[k]=wp.float64(1.);polygon[pair,0,k]=unit
  n=int(3);src=int(0);dst=int(1)
  for h in range(4):
   plane=planes[cell,h];normal=wp.vec3d(plane[0],plane[1],plane[2]);distance=x*normal+wp.vec3d(plane[3]);new=int(0)
   for k in range(n):
    p0=polygon[pair,src,k];p1=polygon[pair,src,(k+1)%n];d0=wp.dot(p0,distance);d1=wp.dot(p1,distance)
    if d0<=wp.float64(0.):
     if new>=10:wp.atomic_max(bad,0,6)
     else:polygon[pair,dst,new]=p0;new+=1
    if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):
     if new>=10:wp.atomic_max(bad,0,6)
     else:polygon[pair,dst,new]=p0+d0/(d0-d1)*(p1-p0);new+=1
   n=new;tmp=src;src=dst;dst=tmp
   if n<3:break
  if n>=3 and bad[0]==0:
   area=wp.float64(0.)
   for k in range(1,n-1):area+=wp.abs(wp.determinant(wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,k],polygon[pair,src,k+1])))
   if area>wp.float64(1e-30):
    index=wp.atomic_add(active,0,1)
    if index>=capacity:wp.atomic_max(bad,0,5)
    else:active_ids[index]=pair;polycounts[pair]=n;sources[pair]=src

@wp.kernel
def quadrature(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),areas:wp.array(dtype=wp.float64),ncells:int,masters:wp.array(dtype=wp.mat33d),polygon:wp.array3d(dtype=wp.vec3d),polycounts:wp.array(dtype=int),sources:wp.array(dtype=int),active:wp.array(dtype=int),active_ids:wp.array(dtype=int),bad:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d)):
 thread=wp.tid();nmaster=masters.shape[0];slot=thread//(8*nmaster);root=(thread//nmaster)%8;leaf=thread%nmaster
 if slot<active[0] and bad[0]==0:
  pair=active_ids[slot];face=pair//ncells;n=polycounts[pair];src=sources[pair]
  if root<n-2:
   B=wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,root+1],polygon[pair,src,root+2]);area=areas[face]*wp.abs(wp.determinant(B))/wp.float64(nmaster);B=masters[leaf]*B;x=X[face];v=V[face];T=pose[0];tv=pose[1];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))
   for k in range(3):
    rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))
    if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed
    f=fn*normal+fr
    for u in range(3):
     for a in range(3):forces[u,a]+=bary[u]*f[a]
    U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)
   for u in range(3):wp.atomic_add(ff,face,u,forces[u])
   wp.atomic_add(uu,face,U);wp.atomic_add(dd,face,D);wp.atomic_add(ww,face,W);wp.atomic_add(mm,face,M)

@wp.kernel
def collect(ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3)):
 k=wp.tid();face=k//3;vertex=k%3;cf[k]=wp.vec3(ff[face,vertex]);cu[k]=float(uu[face]/wp.float64(3.));cp[k]=float(dd[face]/wp.float64(3.));power[k]=float(ww[face]/wp.float64(3.));moment[k]=wp.vec3(mm[face]/wp.float64(3.))

def master_triangles(n):
 def b(i,j):return np.array([1-(i+j)/n,i/n,j/n])
 out=[]
 for i in range(n):
  for j in range(n-i):
   out.append([b(i,j),b(i+1,j),b(i,j+1)])
   if i+j<n-1:out.append([b(i+1,j),b(i+1,j+1),b(i,j+1)])
 assert len(out)==n*n
 return np.array(out)

class ContactGPU(Base):
 def __init__(self,*args,resolution=4,capacity=256,compact_storage=False,**kwargs):
  self.parallel=False;super().__init__(*args,**kwargs);self.nfaces=len(self._surface.tri_area);self.capacity=capacity;self.resolution=resolution;z=np.load(Path(__file__).resolve().parents[1]/'assets/blade_partition.npz');cells=z['x'][z['tets']];self.ncells=len(cells);self.npairs=self.nfaces*self.ncells
  def arr(name,data,dtype):setattr(self,name,wp.array(data,dtype=dtype,device='cuda:0'))
  arr('planes',z['planes'],wp.vec4d);arr('cellbounds',np.stack([cells.min(1),cells.max(1)],axis=1),wp.vec3d);arr('areas',self._surface.tri_area,wp.float64);arr('masters',master_triangles(resolution),wp.mat33d)
  if not compact_storage:
   self.polygon=wp.empty((self.npairs,2,10),dtype=wp.vec3d,device='cuda:0');self.leaves=wp.zeros(self.npairs,dtype=int,device='cuda:0');self.sources=wp.zeros(self.npairs,dtype=int,device='cuda:0');self.active_ids=wp.empty(capacity,dtype=int,device='cuda:0')
  self.active=wp.zeros(1,dtype=int,device='cuda:0');self.queries=wp.zeros(1,dtype=int,device='cuda:0')
  self.xx=wp.empty(self.nfaces,dtype=wp.mat33d,device='cuda:0');self.vv=wp.empty(self.nfaces,dtype=wp.mat33d,device='cuda:0');self.local=wp.empty(self.nfaces,dtype=wp.mat33d,device='cuda:0');self.toolpose=wp.empty(2,dtype=wp.vec3d,device='cuda:0');self.ff=wp.zeros((self.nfaces,3),dtype=wp.vec3d,device='cuda:0');self.mm=wp.zeros(self.nfaces,dtype=wp.vec3d,device='cuda:0')
  for name in ['uu','dd','ww']:setattr(self,name,wp.zeros(self.nfaces,dtype=wp.float64,device='cuda:0'))
  self.parallel=True
 def contact_force(self):
  if not self.parallel:return super().contact_force()
  for a in [self.active,self.ff,self.uu,self.dd,self.ww,self.mm]:a.zero_()
  wp.launch(frame,self.nfaces,[wp.mat33d(self.R),wp.vec3d(self.T0),wp.vec3d(self.travel),wp.float64(self.load),wp.float64(self.hold),self.clock,self.sptr,self.sids,self.sw,self.reference,self.q,self.vh,self.xx,self.vv,self.local,self.toolpose])
  wp.launch(domains,self.npairs,[self.local,self.planes,self.cellbounds,self.ncells,self.polygon,self.leaves,self.sources,self.active,self.active_ids,self.capacity,self.bad])
  wp.launch(quadrature,self.capacity*8*self.resolution*self.resolution,[self.cad.mesh.id,self.tri,wp.mat33d(self.R),self.toolpose,self.xx,self.vv,self.areas,self.ncells,self.masters,self.polygon,self.leaves,self.sources,self.active,self.active_ids,self.bad,self.ff,self.uu,self.dd,self.ww,self.mm])
  wp.launch(collect,self.ns,[self.ff,self.uu,self.dd,self.ww,self.mm,self.cf,self.cu,self.cp,self.power,self.moment])
  wp.launch(pullback_parallel,((self.n+3)//4)*128,[self.cptr,self.cids,self.cw,self.cf,self.external,self.n],block_dim=128);wp.launch(force_parts,self.nparts,[self.cf,self.part_sum,self.part_mag,self.ns]);wp.launch(force_guard,1,[self.part_sum,self.part_mag,self.bad,self.peak,self.nparts]);self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
