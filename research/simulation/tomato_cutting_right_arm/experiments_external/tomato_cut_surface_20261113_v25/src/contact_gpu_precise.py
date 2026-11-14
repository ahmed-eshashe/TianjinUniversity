"""Double precision closest-triangle evaluation after CAD BVH candidate lookup.

Same saved triangles and same law. Bulk arrays/time step remain unchanged.
The mesh BVH's float query selects a face; distance/normal are recomputed from
original float64 vertices. Independent CPU checks guard this candidate lookup.
"""
import numpy as np,warp as wp
from contact_gpu import ContactGPU as Base,pullback,guard,drift
from persistent_gpu import gather
from contact_reductions import pullback_parallel,force_parts,force_guard

@wp.func
def closest(p:wp.vec3d,a:wp.vec3d,b:wp.vec3d,c:wp.vec3d):
 e=b-a;f=c-a;r=p-a;aa=wp.dot(e,e);ab=wp.dot(e,f);bb=wp.dot(f,f);den=aa*bb-ab*ab;u=(wp.dot(r,e)*bb-wp.dot(r,f)*ab)/den;v=(wp.dot(r,f)*aa-wp.dot(r,e)*ab)/den
 q=a+u*e+v*f;best=wp.dot(p-q,p-q)
 if u<wp.float64(0.) or v<wp.float64(0.) or u+v>wp.float64(1.):best=wp.float64(1.e20)
 for k in range(3):
  x=a;y=b
  if k==1:x=b;y=c
  elif k==2:x=c;y=a
  edge=y-x;t=wp.clamp(wp.dot(p-x,edge)/wp.dot(edge,edge),wp.float64(0.),wp.float64(1.));z=x+t*edge;dd=wp.dot(p-z,p-z)
  if dd<best:best=dd;q=z
 return q

@wp.kernel
def samples_precise(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),bbmin:wp.vec3d,bbmax:wp.vec3d,R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),X:wp.array(dtype=wp.vec3d),A:wp.array(dtype=float),u:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),phiout:wp.array(dtype=float),mode:int):
 i=wp.tid();t=clock[0];s=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)
 if t<load:s=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)
 elif t<load+hold:s=wp.float64(1.)
 elif t<wp.float64(2.)*load+hold:
  a=(t-load-hold)/load;s=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*a));speed=-wp.float64(.5)*pi/load*wp.sin(pi*a)
 T=T0+travel*s;tv=travel*speed;x=X[i];vel=wp.vec3d(wp.float64(0.))
 for k in range(ptr[i],ptr[i+1]):x+=w[k]*wp.vec3d(u[ids[k]]);vel+=w[k]*wp.vec3d(v[ids[k]])
 p=wp.transpose(R)*(x-T);phi=wp.float64(100.);normal=wp.vec3d(wp.float64(0.))
 inside=True
 for axis in range(3):
  if p[axis]<bbmin[axis] or p[axis]>bbmax[axis]:inside=False
 if inside:
  r=wp.mesh_query_point_sign_winding_number(mesh,wp.vec3(p),10.)
  if r.result:
   c=closest(p,tri[r.face,0],tri[r.face,1],tri[r.face,2]);d=p-c;l=wp.length(d);phi=wp.float64(r.sign)*l
   if l>wp.float64(1.e-15):normal=R*(wp.float64(r.sign)*d/l)
   else:normal=R*wp.normalize(wp.cross(tri[r.face,1]-tri[r.face,0],tri[r.face,2]-tri[r.face,0]))
 if mode==1:phi=T[1]-x[1];normal=wp.vec3d(wp.float64(0.),wp.float64(-1.),wp.float64(0.))
 depth=wp.max(-phi,wp.float64(0.));fn=wp.float64(1.e9)*wp.float64(A[i])*depth;rel=vel-tv;tangent=rel-wp.dot(rel,normal)*normal;vs=wp.length(tangent);fr=wp.vec3d(wp.float64(0.))
 if vs>wp.float64(1.e-30):fr=-wp.float64(.2)*fn*wp.tanh(vs/wp.float64(.001))*tangent/vs
 f=fn*normal+fr;cf[i]=wp.vec3(f);cu[i]=float(wp.float64(.5)*wp.float64(1.e9)*wp.float64(A[i])*depth*depth);cp[i]=float(-wp.dot(fr,rel));power[i]=float(wp.dot(f,tv));moment[i]=wp.vec3(wp.cross(x-T,f));phiout[i]=float(phi)

@wp.kernel
def tick_precise(clock:wp.array(dtype=wp.float64),dt:wp.float64,bad:wp.array(dtype=int)):
 if bad[0]==0:clock[0]+=dt

class ContactGPU(Base):
 def __init__(self,*args,**kwargs):
  self.precise=False;super().__init__(*args,**kwargs)
  with wp.ScopedStream(self.stream):
   for name,value,dtype in [('reference',self._surface.X,wp.vec3d),('sw',self._surface.Q.data,wp.float64),('clock',[0.],wp.float64)]:
    a=wp.array(value,dtype=dtype,device='cuda:0');setattr(self,name,a);self.ca[name]=a
   self.tri=wp.array(self.cad.vertices[self.cad.faces],dtype=wp.vec3d,device='cuda:0');self.tx['clock']=wp.clone(self.clock)
  self.nparts=(self.ns+127)//128;self.part_sum=wp.zeros(self.nparts,dtype=wp.vec3,device='cuda:0');self.part_mag=wp.zeros(self.nparts,dtype=float,device='cuda:0')
  self.precise=True
 def contact_force(self):
  if not self.precise:return super().contact_force()
  wp.launch(samples_precise,self.ns,[self.cad.mesh.id,self.tri,wp.vec3d(self.cad.vertices.min(0)-2e-6),wp.vec3d(self.cad.vertices.max(0)+2e-6),wp.mat33d(self.R),wp.vec3d(self.T0),wp.vec3d(self.travel),wp.float64(self.load),wp.float64(self.hold),self.clock,self.sptr,self.sids,self.sw,self.reference,self.area,self.q,self.vh,self.cf,self.cu,self.cp,self.power,self.moment,self.phiout,self.mode])
  wp.launch(pullback_parallel,((self.n+3)//4)*128,[self.cptr,self.cids,self.cw,self.cf,self.external,self.n],block_dim=128);wp.launch(force_parts,self.nparts,[self.cf,self.part_sum,self.part_mag,self.ns]);wp.launch(force_guard,1,[self.part_sum,self.part_mag,self.bad,self.peak,self.nparts]);self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
 def one(self):
  if not self.precise:return super().one()
  self.contact_force();self.half_kick();wp.launch(drift,self.n,[self.q,self.vh,self.dt,self.n,self.bad,self.maxspeed]);wp.launch(tick_precise,1,[self.clock,wp.float64(self.dt),self.bad]);self.contact_force();self.half_kick()
