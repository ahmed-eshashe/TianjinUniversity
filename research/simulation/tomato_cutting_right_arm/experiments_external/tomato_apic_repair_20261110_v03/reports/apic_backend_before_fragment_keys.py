from pathlib import Path
import numpy as np,warp as wp
from scipy.sparse import coo_matrix
W=Path(__file__).resolve().parents[1];wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False;wp.init()
import apic_kernels as k
from reference import swept_codes
from apic_reference import kinetic,momentum
class APICBackend:
 def __init__(self,X,spacing=.0015,h=.003,E=1e5,nu=.4,fixed=None,margin=.04):
  self.X=np.asarray(X,float).copy();self.n=len(X);self.h=h;self.mass=1000*spacing**3;self.vol=spacing**3;self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu));self.device='cuda:0';self.fixed=np.zeros(self.n,bool) if fixed is None else np.array(fixed,bool);self.origin=np.floor((self.X.min(0)-margin)/h).astype(int)-2;last=np.ceil((self.X.max(0)+margin)/h).astype(int)+2;self.dims=last-self.origin+1;self.ng=int(np.prod(self.dims));self.grid=None
  def arr(a,t):return wp.array(a,dtype=t,device=self.device)
  self.x=arr(X,wp.vec3d);self.v=arr(np.zeros_like(X),wp.vec3d);self.C=arr(np.zeros((self.n,3,3)),wp.mat33d);self.F=arr(np.tile(np.eye(3),(self.n,1,1)),wp.mat33d);self.codes=arr(np.zeros(self.n,int),int);self.ids=wp.zeros((self.n,27),dtype=int,device=self.device);self.w=wp.zeros((self.n,27),dtype=wp.float64,device=self.device);self.g=wp.zeros((self.n,27),dtype=wp.vec3d,device=self.device);self.r=wp.zeros((self.n,27),dtype=wp.vec3d,device=self.device);self.external=wp.zeros(self.n,dtype=wp.vec3d,device=self.device);self.lookup=arr(np.zeros(81,int),int);self.active=arr(np.zeros(81,int),int);self.bad=wp.zeros(1,dtype=int,device=self.device);self.stats=wp.zeros(6,dtype=wp.float64,device=self.device);self.totals=wp.zeros(2,dtype=wp.float64,device=self.device);self.count=1;self.allocated=0;self.graphs={};self.steps=0;self.sim_time=0.;self.refresh_codes()
 def launch(self,fn,dim,args):wp.launch(fn,dim=dim,inputs=args,device=self.device)
 def refresh_codes(self):
  active=np.unique(self.codes.numpy());self.count=len(active);assert active.min()>=0 and active.max()<81
  look=np.full(81,-1,int);look[active]=np.arange(self.count);a=np.zeros(81,int);a[:self.count]=active;self.active.assign(a);self.lookup.assign(look)
  if self.count>self.allocated:
   self.allocated=self.count;self.m=wp.zeros((self.allocated,self.ng),dtype=wp.float64,device=self.device)
   for n in ['p','force','vg']:setattr(self,n,wp.zeros((self.allocated,self.ng),dtype=wp.vec3d,device=self.device))
   self.graphs={}
 def _prepare(self,dt):
  self.stats.zero_();self.launch(k.stencil_current,self.n,[self.x,self.h,wp.vec3i(*self.origin),wp.vec3i(*self.dims),self.ids,self.w,self.g,self.r,self.bad]);self.launch(k.clear,(self.count,self.ng),[self.m,self.p,self.force]);self.launch(k.p2g,self.n,[self.v,self.C,self.F,self.codes,self.lookup,self.ids,self.w,self.g,self.r,self.external,self.mass,self.vol,self.mu,self.lam,self.h,self.m,self.p,self.force,self.stats,self.bad]);self.launch(k.grid_update,(self.count,self.ng),[self.m,self.p,self.force,self.active,self.count,dt,self.vg,self.stats])
 def _finish(self,dt):
  self.launch(k.grid_energy,(self.count,self.ng),[self.m,self.vg,self.stats]);self.launch(k.g2p,self.n,[self.x,self.v,self.C,self.F,self.codes,self.lookup,self.ids,self.w,self.g,self.r,self.vg,dt,self.h,self.mass,self.stats]);self.launch(k.tally,1,[self.stats,self.totals])
 def _W(self):
  ids=self.ids.numpy();w=self.w.numpy();slots=self.lookup.numpy()[self.codes.numpy()];return coo_matrix((w.ravel(),(np.repeat(np.arange(self.n),27),(slots[:,None]*self.ng+ids).ravel())),shape=(self.n,self.allocated*self.ng)).tocsr()
 def prepare(self,dt,force=None):
  self.dt=dt;self.external.zero_() if force is None else self.external.assign(np.asarray(force));self._prepare(dt);self.W=self._W();self.mass_grid=self.m.numpy().ravel();self.inv=np.zeros_like(self.mass_grid);np.divide(1,self.mass_grid,out=self.inv,where=self.mass_grid>0);self.support_impulse=np.zeros(3);self.support_moment=np.zeros(3);self.S=self.W[self.fixed];self.project_support();return self.W@self.vg.numpy().reshape(-1,3)
 def project_support(self):
  if not np.any(self.fixed):return
  H=(self.S.multiply(self.inv)@self.S.T).toarray();val,vec=np.linalg.eigh(H);iv=np.zeros_like(val);np.divide(1,val,out=iv,where=val>max(val.max()*1e-12,1e-30));self.Hpinv=(vec*iv)@vec.T;vg=self.vg.numpy().reshape(-1,3);lam=-self.Hpinv@(self.S@vg);J=self.S.T@lam;vg+=self.inv[:,None]*J;self.support_impulse+=J.sum(0)
  if self.grid is None:self.grid=np.stack(np.meshgrid(*[np.arange(n) for n in self.dims],indexing='ij'),axis=-1).reshape(-1,3);self.grid=(self.grid+self.origin)*self.h
  self.support_moment+=np.cross(np.tile(self.grid,(self.allocated,1)),J).sum(0);res=float(abs(self.S@vg).max())
  if res>1e-7:raise RuntimeError(f'support projection residual {res}')
  self.vg.assign(vg.reshape(self.allocated,self.ng,3))
 def add_particle_impulse(self,J):
  vg=self.vg.numpy().reshape(-1,3);vg+=(self.W.T@J)*self.inv[:,None];self.vg.assign(vg.reshape(self.allocated,self.ng,3));self.project_support()
 def marker_mobility(self,marker,direction):
  a=np.asarray(marker@self.W).ravel();z=self.inv*a;out=np.repeat(z[:,None],3,axis=1)*direction
  if np.any(self.fixed):out-=self.inv[:,None]*(self.S.T@(self.Hpinv@(self.S@out)))
  return float(direction@(a@out)),a@self.vg.numpy().reshape(-1,3)
 def finish(self):self._finish(self.dt);self.steps+=1;self.sim_time+=self.dt
 def physical_step(self,dt,force):self.prepare(dt,force);self.finish()
 def step(self,dt,steps=1,graph=True):
  if np.any(self.fixed):
   for j in range(steps):self.physical_step(dt,None)
   return
  self.external.zero_();key=(self.count,float(dt),int(steps))
  if graph:
   if key not in self.graphs:
    wp.synchronize();wp.capture_begin(device=self.device)
    for j in range(steps):self._prepare(dt);self._finish(dt)
    self.graphs[key]=wp.capture_end(device=self.device)
   wp.capture_launch(self.graphs[key])
  else:
   for j in range(steps):self._prepare(dt);self._finish(dt)
  self.steps+=steps;self.sim_time+=dt*steps
 def state(self):return {'X':self.X.copy(),**{a:getattr(self,a).numpy() for a in ['x','v','C','F','codes']}}
 def check(self):
  wp.synchronize();s=self.state();J=np.linalg.det(s['F'])
  if self.bad.numpy()[0] or not all(np.isfinite(s[k]).all() for k in ['x','v','C','F']) or J.min()<=.1 or J.max()>=10:raise RuntimeError('inadmissible state or spatial-grid overflow')
  return s
 def set_state(self,**state):
  for name,value in state.items():
   if name=='X':assert np.array_equal(value,self.X)
   else:getattr(self,name).assign(value)
  if 'codes' in state:self.refresh_codes()
 def sweep(self,cut,old,new,normal,edge,half_length=.04):
  if not 0<=cut<4:raise ValueError('four-cut capacity exceeded; no state mutation')
  s=self.state();self.set_state(codes=swept_codes(s['x'],s['codes'],cut,np.asarray(old),np.asarray(new),np.asarray(normal),np.asarray(edge),half_length,6*self.h))
 def save(self,path):np.savez_compressed(path,**self.state(),mass=self.mass,sim_time=self.sim_time,steps=self.steps,transfer_and_support_losses=self.totals.numpy())
 def memory(self):
  names=['x','v','C','F','codes','ids','w','g','r','external','lookup','active','bad','stats','totals','m','p','force','vg'];return {'array_bytes':sum(getattr(self,n).size*wp.types.type_size_in_bytes(getattr(self,n).dtype) for n in names),'particles':self.n,'spatial_grid_nodes':self.ng,'active_states':self.count,'allocated_states':self.allocated}
