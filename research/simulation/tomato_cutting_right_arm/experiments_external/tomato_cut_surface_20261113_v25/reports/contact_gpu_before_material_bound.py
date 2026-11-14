"""State-driven CAD contact on the frozen v22 bulk operator.

Velocity Verlet bulk; contact/friction evaluated at both kicks, with the second
friction evaluation using the drift velocity. Physics parameters are v02's.
Qualification is restricted to intact-tet coupons; no paid splitting is enabled.
"""
import numpy as np,warp as wp
from pipeline_gpu import GPU as Runtime
from persistent_gpu import gather

@wp.kernel
def samples(mesh:wp.uint64,R:wp.mat33,T0:wp.vec3,travel:wp.vec3,load:float,hold:float,clock:wp.array(dtype=float),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=float),X:wp.array(dtype=wp.vec3),A:wp.array(dtype=float),u:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),phiout:wp.array(dtype=float),mode:int):
 i=wp.tid();t=clock[0];s=float(0.);speed=float(0.)
 if t<load:s=.5*(1.-wp.cos(wp.pi*t/load));speed=.5*wp.pi/load*wp.sin(wp.pi*t/load)
 elif t<load+hold:s=1.
 elif t<2.*load+hold:
  a=(t-load-hold)/load;s=.5*(1.+wp.cos(wp.pi*a));speed=-.5*wp.pi/load*wp.sin(wp.pi*a)
 T=T0+travel*s;tv=travel*speed;x=X[i];vel=wp.vec3(0.)
 for k in range(ptr[i],ptr[i+1]):x+=w[k]*u[ids[k]];vel+=w[k]*v[ids[k]]
 p=wp.transpose(R)*(x-T);r=wp.mesh_query_point_sign_winding_number(mesh,p,10.);phi=float(100.);normal=wp.vec3(0.)
 if r.result:
  c=wp.mesh_eval_position(mesh,r.face,r.u,r.v);d=p-c;l=wp.length(d);phi=r.sign*l
  if l>1.e-12:normal=R*(r.sign*d/l)
  else:normal=R*wp.mesh_eval_face_normal(mesh,r.face)
 if mode==1:phi=T[1]-x[1];normal=wp.vec3(0.,-1.,0.) # analytical plane only
 depth=wp.max(-phi,0.);fn=1.e9*A[i]*depth;rel=vel-tv;tangent=rel-wp.dot(rel,normal)*normal;vs=wp.length(tangent);fr=wp.vec3(0.)
 if vs>1.e-30:fr=-.2*fn*wp.tanh(vs/.001)*tangent/vs
 f=fn*normal+fr;cf[i]=f;cu[i]=.5*1.e9*A[i]*depth*depth;cp[i]=-wp.dot(fr,rel);power[i]=wp.dot(f,tv);moment[i]=wp.cross(x-T,f);phiout[i]=phi

@wp.kernel
def pullback(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=float),cf:wp.array(dtype=wp.vec3),external:wp.array(dtype=wp.vec3),n:int):
 i=wp.tid()
 if i<n:
  f=wp.vec3(0.)
  for k in range(ptr[i],ptr[i+1]):f+=w[k]*cf[ids[k]]
  external[i]=f

@wp.kernel
def guard(cf:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),peak:wp.array(dtype=float),n:int):
 if wp.tid()==0:
  total=wp.vec3(0.);mag=float(0.)
  for i in range(n):total+=cf[i];mag+=wp.length(cf[i])
  value=wp.max(mag,wp.length(total));peak[0]=wp.max(peak[0],value)
  if value>2. or not wp.isfinite(value):wp.atomic_max(bad,0,3)

@wp.kernel
def kick(mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float,n:int,bad:wp.array(dtype=int)):
 i=wp.tid()
 if i<n and bad[0]==0:
  if fixed[i]!=0:support[i]-=dt*force[i];v[i]=wp.vec3(0.)
  else:
   acc=wp.vec3(0.)
   for k in range(mptr[i],mptr[i+1]):acc+=mi[k]*force[midx[k]]
   v[i]+=dt*acc

@wp.kernel
def drift(q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dt:float,n:int,bad:wp.array(dtype=int),maxspeed:wp.array(dtype=float)):
 i=wp.tid()
 if i<n and bad[0]==0:
  wp.atomic_max(maxspeed,0,wp.length(v[i]));q[i]+=dt*v[i]

@wp.kernel
def tick(clock:wp.array(dtype=float),dt:float,bad:wp.array(dtype=int)):
 if bad[0]==0:clock[0]+=dt

@wp.kernel
def ledger(cf:wp.array(dtype=wp.vec3),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),impulse:wp.array(dtype=wp.vec3),angular:wp.array(dtype=wp.vec3),work:wp.array(dtype=float),diss:wp.array(dtype=float),dt:float,bad:wp.array(dtype=int)):
 i=wp.tid()
 if bad[0]==0:impulse[i]+=dt*cf[i];angular[i]+=dt*moment[i];work[i]+=dt*power[i];diss[i]+=dt*cp[i]

class ContactGPU(Runtime):
 def __init__(self,a,surface,cad,T0,travel,load=.005,hold=.003,dt=12.5e-6,fixed=None,R=None,mode=0):
  self.physical=False;super().__init__([a],dt=dt)
  q,v=super().state();self._surface=surface;self.cad=cad;self.R=cad.R if R is None else np.asarray(R);self.T0=np.asarray(T0);self.travel=np.asarray(travel);self.load=load;self.hold=hold;self.mode=int(mode)
  if a.coupled:raise ValueError('Supported contact integration currently requires uncoupled mass; never relump')
  self.graphs.clear();self.dispatch.clear();self.ca={}
  def arr(name,value,dtype):
   z=wp.array(value,dtype=dtype,device='cuda:0');setattr(self,name,z);self.ca[name]=z
  with wp.ScopedStream(self.stream):
   padded=np.zeros((self.ncap,3),np.float32);padded[:self.n]=v;self.vh.assign(padded)
   Q=surface.Q;C=Q.tocsc();self.ns=Q.shape[0]
   for name,value in [('sptr',Q.indptr),('sids',Q.indices),('cptr',C.indptr),('cids',C.indices)]:arr(name,value,int)
   for name,value in [('sw',Q.data),('cw',C.data),('area',surface.area),('clock',[0.]),('peak',[0.]),('maxspeed',[0.])]:arr(name,value,float)
   arr('reference',surface.X,wp.vec3);arr('fixed',np.zeros(self.ncap,np.int32) if fixed is None else np.pad(np.asarray(fixed,np.int32),(0,self.ncap-len(fixed))),int)
   for name in ['cf','moment','impulse','angular']:arr(name,np.zeros((self.ns,3)),wp.vec3)
   for name in ['cu','cp','power','phiout','work','diss']:arr(name,np.zeros(self.ns),float)
   arr('support',np.zeros((self.ncap,3)),wp.vec3)
  self.physical=True;self.steps=0
  self.tx={k:wp.clone(v) for k,v in self.ca.items() if k in ['clock','peak','maxspeed','support','impulse','angular','work','diss']}
 def graph(self,n):
  if not self.physical:return super().graph(n)
  # Contact topology is fixed in this first integration; retain capacity grids.
  from persistent_gpu import GPU
  return GPU.graph(self,n)
 def contact_force(self):
  wp.launch(samples,self.ns,[self.cad.mesh.id,wp.mat33(self.R),wp.vec3(self.T0),wp.vec3(self.travel),self.load,self.hold,self.clock,self.sptr,self.sids,self.sw,self.reference,self.area,self.q,self.vh,self.cf,self.cu,self.cp,self.power,self.moment,self.phiout,self.mode])
  wp.launch(pullback,self.n,[self.cptr,self.cids,self.cw,self.cf,self.external,self.n])
  wp.launch(guard,1,[self.cf,self.bad,self.peak,self.ns])
  self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
 def half_kick(self):
  wp.launch(kick,self.n,[self.mptr,self.midx,self.mi,self.force,self.vh,self.fixed,self.support,.5*self.dt,self.n,self.bad])
  wp.launch(ledger,self.ns,[self.cf,self.cp,self.power,self.moment,self.impulse,self.angular,self.work,self.diss,.5*self.dt,self.bad])
 def one(self):
  if not self.physical:return super().one()
  self.contact_force();self.half_kick();wp.launch(drift,self.n,[self.q,self.vh,self.dt,self.n,self.bad,self.maxspeed]);wp.launch(tick,1,[self.clock,self.dt,self.bad]);self.contact_force();self.half_kick()
 def step_async(self,n,block=32):
  if self.pending is not None:raise ValueError('unfinished contact step')
  if n<=0:raise ValueError('positive steps required')
  with wp.ScopedStream(self.stream):
   full,rem=divmod(n,block);graphs=[self.graph(block)]*full
   if rem:graphs.append(self.graph(rem))
   wp.copy(self.backup[0],self.q);wp.copy(self.backup[1],self.vh)
   for k,v in self.tx.items():wp.copy(v,self.ca[k])
   self.bad.zero_()
   for g in graphs:wp.capture_launch(g)
   self.contact_force()
   wp.copy(self.host_q,self.q,count=self.n);wp.copy(self.host_v,self.vh,count=self.n);wp.copy(self.host_bad,self.bad)
  self.pending=n
 def finish(self):
  wp.synchronize_stream(self.stream)
  failed=bool(self.bad_view[0])
  try:return super().finish()
  finally:
   if failed:
    with wp.ScopedStream(self.stream):
     for k,v in self.tx.items():wp.copy(self.ca[k],v)
    wp.synchronize_stream(self.stream)
 def state(self):
  if not self.physical:return super().state()
  if self.pending is not None:raise ValueError('unfinished contact step')
  with wp.ScopedStream(self.stream):
   wp.copy(self.host_q,self.q,count=self.n);wp.copy(self.host_v,self.vh,count=self.n);self.check()
  return self.q_view[:self.n].astype(float),self.v_view[:self.n].astype(float)
 def observe(self):
  if self.pending is not None:raise ValueError('unfinished contact step')
  with wp.ScopedStream(self.stream):self.contact_force();self.check()
  f=self.cf.numpy().astype(float)
  return dict(reaction=-f.sum(0),moment=-self.moment.numpy().astype(float).sum(0),contact_energy=float(self.cu.numpy().astype(float).sum()),friction_J=float(self.diss.numpy().astype(float).sum()),tool_work_J=float(self.work.numpy().astype(float).sum()),material_impulse=self.impulse.numpy().astype(float).sum(0),support_impulse=self.support.numpy().astype(float).sum(0),sum_force_N=float(np.linalg.norm(f,axis=1).sum()),peak_N=float(self.peak.numpy()[0]),time=float(self.clock.numpy()[0]))
 def replace(self,*args,**kwargs):
  if self.physical:raise ValueError('Contact topology replacement/reset requires a new validated surface; use a fresh instance')
  return super().replace(*args,**kwargs)
 def pose(self,t):
  if t<self.load:s=.5*(1-np.cos(np.pi*t/self.load));v=.5*np.pi/self.load*np.sin(np.pi*t/self.load)
  elif t<self.load+self.hold:s=1.;v=0.
  elif t<2*self.load+self.hold:z=(t-self.load-self.hold)/self.load;s=.5*(1+np.cos(np.pi*z));v=-.5*np.pi/self.load*np.sin(np.pi*z)
  else:s=v=0.
  return self.T0+self.travel*s,self.travel*v

 def checked_step(self,n,block=32):
  from blade_geometry import certify
  import time
  t0=time.perf_counter();self.step_async(n,block);wp.synchronize_stream(self.stream);t1=time.perf_counter()
  if self.bad_view[0]:return self.finish()
  q=self.q_view[:self.n].astype(float);end=(self.steps+n)*self.dt;T,_=self.pose(end)
  maxv=float(self.maxspeed.numpy()[0]);motion=(maxv+np.linalg.norm(self.travel)*.5*np.pi/self.load)*n*self.dt
  cert=certify(self._surface.tets(q),self.cad,T,self.R,motion=motion)
  t2=time.perf_counter();self.last_certificate=cert
  if not cert['passed']:self.bad_view[0]=4
  result=self.finish();self.last_cost={'GPU_step_host_read_s':t1-t0,'whole_volume_certificate_s':t2-t1,'accepted_state_transfer_s':time.perf_counter()-t2};return result
