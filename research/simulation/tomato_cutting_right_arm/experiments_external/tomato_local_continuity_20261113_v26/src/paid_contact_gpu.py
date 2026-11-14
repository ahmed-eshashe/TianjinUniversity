"""Trial coupling of the existing ideal resistance to the qualified mechanics.

Work is accumulated separately from geometric authorization. A caller must
prove sharp-edge overlap, novel patch area and transactional topology transfer.
This integrator alone never creates a cut or claims a complete physical gate.
"""
import numpy as np,warp as wp
from supported_contact_gpu import ContactGPU as Base
from constrained_resistance import inverse_free

@wp.kernel
def resistance(v:wp.array(dtype=wp.vec3),B:wp.array(dtype=wp.vec3d),c:wp.array(dtype=wp.vec3d),params:wp.array(dtype=wp.float64),pose:wp.array(dtype=wp.vec3d),dt:wp.float64,Jout:wp.array(dtype=wp.float64),force:wp.array(dtype=wp.vec3d),account:wp.array(dtype=wp.float64),impulse:wp.array(dtype=wp.vec3d),bad:wp.array(dtype=int),n:int):
 if bad[0]==0:
  material=wp.float64(0.)
  for i in range(n):material+=wp.dot(B[i],wp.vec3d(v[i]))
  tv=wp.dot(pose[1],c[0]);relative=tv-material;Y=params[0]*wp.float64(80.);J=wp.float64(0.);slip=wp.float64(0.)
  if params[2]>wp.float64(.5) and params[1]>wp.float64(0.):
   J=wp.min(Y*dt,wp.max(relative,wp.float64(0.))/params[1])
   if J>=Y*dt*wp.float64(1.-1e-10):slip=wp.max(relative-J*params[1],wp.float64(0.))*dt
  Jout[0]=J;force[0]=J/dt*c[0];area=params[0]*slip;account[0]+=J*tv;account[1]+=wp.float64(.5)*J*J*params[1];account[2]+=wp.float64(80.)*area;account[3]+=area;impulse[0]+=J*c[0]

@wp.kernel
def apply_impulse(v:wp.array(dtype=wp.vec3),mobility:wp.array(dtype=wp.vec3d),reaction:wp.array(dtype=wp.vec3d),J:wp.array(dtype=wp.float64),support:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int)):
 i=wp.tid()
 if bad[0]==0:v[i]+=wp.vec3(J[0]*mobility[i]);support[i]+=wp.vec3(J[0]*reaction[i])

@wp.kernel
def combined_guard(cf:wp.array(dtype=wp.vec3),cut:wp.array(dtype=wp.vec3d),peak:wp.array(dtype=float),bad:wp.array(dtype=int),n:int):
 value=wp.length(cut[0])
 for i in range(n):value+=wp.float64(wp.length(cf[i]))
 wp.atomic_max(peak,0,float(value))
 if value>wp.float64(2.) or not wp.isfinite(value):wp.atomic_max(bad,0,3)

class ContactGPU(Base):
 def __init__(self,*args,**kwargs):
  self.paid=False;super().__init__(*args,**kwargs)
  for name,n,dtype in [('cutB',self.n,wp.vec3d),('cut_mobility',self.n,wp.vec3d),('cut_reaction',self.n,wp.vec3d),('cut_c',1,wp.vec3d),('cut_force',1,wp.vec3d),('cut_impulse',1,wp.vec3d),('cut_J',1,wp.float64),('cut_params',3,wp.float64),('cut_account',4,wp.float64)]:
   arr=wp.zeros(n,dtype=dtype,device='cuda:0');setattr(self,name,arr)
   if name in ['cut_force','cut_impulse','cut_J','cut_account']:self.ca[name]=arr;self.tx[name]=wp.clone(arr)
  self.paid=True
 def configure_resistance(self,marker,covector,width,eligible):
  c=np.asarray(covector,float);self.configure_vectors(np.asarray(marker)[:,None]*c,c,width,eligible)
 def configure_vectors(self,B,c,width,eligible):
  a=self.aggregates[0];mobility=inverse_free(a,B,self.fixed.numpy()[:self.n].astype(bool));invm=float(np.sum(B*mobility));reaction=a.M@mobility-B
  with wp.ScopedStream(self.stream):
   self.cutB.assign(B);self.cut_mobility.assign(mobility);self.cut_reaction.assign(reaction);self.cut_c.assign(c[None]);self.cut_params.assign(np.array([width,invm,float(eligible)]))
 def contact_force(self):
  super().contact_force()
  if self.paid:wp.launch(combined_guard,1,[self.cf,self.cut_force,self.peak,self.bad,self.ns])
 def one(self):
  if not self.paid:return super().one()
  self.contact_force();wp.launch(resistance,1,[self.vh,self.cutB,self.cut_c,self.cut_params,self.toolpose,wp.float64(self.dt),self.cut_J,self.cut_force,self.cut_account,self.cut_impulse,self.bad,self.n]);wp.launch(combined_guard,1,[self.cf,self.cut_force,self.peak,self.bad,self.ns]);wp.launch(apply_impulse,self.n,[self.vh,self.cut_mobility,self.cut_reaction,self.cut_J,self.support,self.bad]);super().one()
 def observe(self):
  o=super().observe();account=self.cut_account.numpy();o.update(cutting_tool_work_J=float(account[0]),cutting_numerical_loss_J=float(account[1]),earned_fracture_J=float(account[2]),earned_area_m2=float(account[3]),cutting_impulse=self.cut_impulse.numpy()[0],cutting_force=self.cut_force.numpy()[0]);return o
