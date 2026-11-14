from pathlib import Path
import os,time,json,numpy as np
import warp as wp
W=Path(__file__).resolve().parents[1]
wp.config.kernel_cache_dir=str(W/'cache/warp')
wp.config.enable_backward=False
wp.init()
from reference import stencil
import kernels as k

class Backend:
 def __init__(self,X,spacing=.003,h=.006,E=1e5,nu=.4,capacity=81):
  self.X=np.asarray(X).copy();self.n=len(X);self.h=h;self.mass=1000*spacing**3;self.vol=spacing**3;self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu));self.device='cuda:0';self.capacity=capacity
  ids,w,g,grid=stencil(self.X,h);self.grid=grid;self.ng=len(grid)
  def arr(a,t):return wp.array(a,dtype=t,device=self.device)
  self.ids=arr(ids.astype(np.int32),wp.int32);self.w=arr(w,wp.float32);self.g=arr(g,wp.vec3)
  self.x=arr(X,wp.vec3);self.v=arr(np.zeros_like(X),wp.vec3);self.F=arr(np.tile(np.eye(3),(len(X),1,1)),wp.mat33)
  self.codes=arr(np.zeros(len(X),np.int32),wp.int32);self.lookup=arr(np.zeros(81,np.int32),wp.int32);self.active=arr(np.zeros(81,np.int32),wp.int32);self.count=1
  self.m=wp.zeros((capacity,self.ng),dtype=wp.float32,device=self.device)
  for name in ['p','q','r','v0','v1','vr']:setattr(self,name,wp.zeros((capacity,self.ng),dtype=wp.vec3,device=self.device))
  self.bad=wp.zeros(1,dtype=wp.int32,device=self.device);self.allocated_cuts=0;self.steps=0;self.sim_time=0.;self.graphs={}
 def launch(self,fn,dim,args):wp.launch(fn,dim=dim,inputs=args,device=self.device)
 def _step(self,dt):
  self.launch(k.clear_grid,(self.count,self.ng),[self.m,self.p,self.q,self.r])
  self.launch(k.p2g,self.n,[self.v,self.F,self.codes,self.lookup,self.ids,self.w,self.g,self.mass,self.vol,self.mu,self.lam,dt,self.m,self.p,self.q,self.bad])
  self.launch(k.grid_update,(self.count,self.ng),[self.m,self.p,self.q,self.active,self.count,self.v0,self.v1])
  self.launch(k.g2p,self.n,[self.x,self.v,self.codes,self.lookup,self.ids,self.w,self.v0,self.v1,dt])
  self.launch(k.remap,self.n,[self.v,self.codes,self.lookup,self.ids,self.w,self.mass,self.r])
  self.launch(k.remap_couple,(self.count,self.ng),[self.m,self.r,self.active,self.count,self.vr])
  self.launch(k.deform,self.n,[self.F,self.codes,self.lookup,self.ids,self.g,self.vr,dt])
 def step(self,dt,steps=1,graph=True):
  # Graph changes neither the physical substep count nor the update sequence.
  if graph:
   key=(self.count,float(dt),int(steps))
   if key not in self.graphs:
    wp.synchronize();wp.capture_begin(device=self.device)
    for _ in range(steps):self._step(dt)
    self.graphs[key]=wp.capture_end(device=self.device)
   wp.capture_launch(self.graphs[key])
  else:
   for _ in range(steps):self._step(dt)
  self.steps+=steps;self.sim_time+=dt*steps
 def check(self):
  wp.synchronize()
  if self.bad.numpy()[0]:raise RuntimeError('inadmissible F detected; run rejected')
  state=self.state();J=np.linalg.det(state['F'])
  if not all(np.isfinite(state[x]).all() for x in ('x','v','F')) or J.min()<=.1 or J.max()>=10:raise RuntimeError('nonfinite/inadmissible state')
  return state
 def state(self):return {'X':self.X.copy(),'x':self.x.numpy(),'v':self.v.numpy(),'F':self.F.numpy(),'codes':self.codes.numpy()}
 def set_state(self,**kwargs):
  for name,a in kwargs.items():
   obj=getattr(self,name);obj.assign(np.asarray(a))
  if 'codes' in kwargs:self.refresh_codes()
 def refresh_codes(self):
  active=np.unique(self.codes.numpy());self.count=len(active)
  if self.count>self.capacity:raise RuntimeError('logical-state capacity exhausted')
  lookup=np.full(81,-1,np.int32);lookup[active]=np.arange(len(active));a=np.zeros(81,np.int32);a[:len(active)]=active
  self.lookup.assign(lookup);self.active.assign(a)
 def sweep(self,cut,old,new,normal,edge,half_length=.04):
  if not 0<=cut<4:raise ValueError('four-cut history capacity exhausted; state unchanged')
  old=np.asarray(old,float);new=np.asarray(new,float);normal=np.asarray(normal,float);edge=np.asarray(edge,float);d=new-old
  if np.linalg.norm(d)==0:return
  if abs(np.linalg.norm(normal)-1)>1e-6 or abs(np.linalg.norm(edge)-1)>1e-6 or abs(normal@edge)>1e-6 or abs(normal@d)>1e-8 or abs(edge@d)>1e-8:raise ValueError('initial test envelope requires orthonormal straight current sweep')
  self.launch(k.assign_sweep,self.n,[self.x,self.codes,wp.vec3(old),wp.vec3(new),wp.vec3(normal),wp.vec3(edge),half_length,6*self.h,3**cut]);self.refresh_codes();self.allocated_cuts=max(self.allocated_cuts,cut+1)
 def save(self,path):np.savez_compressed(path,**self.state(),mass=self.mass,steps=self.steps,sim_time=self.sim_time)
 def memory(self):
  arrays=[getattr(self,name) for name in ('ids','w','g','x','v','F','codes','lookup','active','m','p','q','r','v0','v1','vr','bad')]
  return {'array_bytes':sum(a.size*wp.types.type_size_in_bytes(a.dtype) for a in arrays),'particles':self.n,'reference_nodes':self.ng,'active_states':self.count,'reserved_states':self.capacity}
