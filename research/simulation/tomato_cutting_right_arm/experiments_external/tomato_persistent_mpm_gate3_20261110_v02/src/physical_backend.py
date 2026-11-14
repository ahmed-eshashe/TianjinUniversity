from pathlib import Path
import numpy as np
from backend import Backend,wp,k
from physical_kernels import contact_advance
class PhysicalBackend(Backend):
 def __init__(self,X,spacing=.0015,h=.003,fixed=None):
  super().__init__(X,spacing,h);self.external=wp.zeros(self.n,dtype=wp.vec3,device=self.device);self.fixed=wp.array(np.zeros(self.n,np.int32) if fixed is None else np.asarray(fixed,np.int32),dtype=int,device=self.device);self.support=wp.zeros(self.n,dtype=wp.vec3,device=self.device)
 def physical_step(self,dt,force):
  self.external.assign(np.asarray(force));self.launch(k.clear_grid,(self.count,self.ng),[self.m,self.p,self.q,self.r]);self.launch(k.p2g,self.n,[self.v,self.F,self.codes,self.lookup,self.ids,self.w,self.g,self.mass,self.vol,self.mu,self.lam,dt,self.m,self.p,self.q,self.bad]);self.launch(k.grid_update,(self.count,self.ng),[self.m,self.p,self.q,self.active,self.count,self.v0,self.v1]);self.launch(contact_advance,self.n,[self.x,self.v,self.codes,self.lookup,self.ids,self.w,self.v0,self.v1,self.external,self.mass,self.fixed,self.support,dt]);self.launch(k.remap,self.n,[self.v,self.codes,self.lookup,self.ids,self.w,self.mass,self.r]);self.launch(k.remap_couple,(self.count,self.ng),[self.m,self.r,self.active,self.count,self.vr]);self.launch(k.deform,self.n,[self.F,self.codes,self.lookup,self.ids,self.g,self.vr,dt]);self.sim_time+=dt;self.steps+=1
 def predict(self,dt):
  from physical_kernels import predict_velocity
  if not hasattr(self,'pred'):self.pred=wp.zeros(self.n,dtype=wp.vec3,device=self.device)
  self.launch(k.clear_grid,(self.count,self.ng),[self.m,self.p,self.q,self.r]);self.launch(k.p2g,self.n,[self.v,self.F,self.codes,self.lookup,self.ids,self.w,self.g,self.mass,self.vol,self.mu,self.lam,dt,self.m,self.p,self.q,self.bad]);self.launch(k.grid_update,(self.count,self.ng),[self.m,self.p,self.q,self.active,self.count,self.v0,self.v1]);self.launch(predict_velocity,self.n,[self.v,self.codes,self.lookup,self.ids,self.w,self.v0,self.v1,self.pred]);return self.pred.numpy().astype(float)
 def finish(self,dt,velocity):
  from physical_kernels import finish_velocity
  self.pred.assign(np.asarray(velocity));self.launch(finish_velocity,self.n,[self.x,self.v,self.pred,dt]);self.launch(k.remap,self.n,[self.v,self.codes,self.lookup,self.ids,self.w,self.mass,self.r]);self.launch(k.remap_couple,(self.count,self.ng),[self.m,self.r,self.active,self.count,self.vr]);self.launch(k.deform,self.n,[self.F,self.codes,self.lookup,self.ids,self.g,self.vr,dt]);self.sim_time+=dt;self.steps+=1
