from pathlib import Path
import numpy as np,warp as wp
from block_basis import block_basis
from reference import energy_stress
W=Path(__file__).resolve().parents[1];wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False;wp.init()
import consistent_kernels as k
class ConsistentBackend:
 def __init__(self,X,spacing=.0015,h=.003,E=1e5,nu=.4):
  self.X=np.array(X,float);self.mass=1000*spacing**3;self.vol=spacing**3;self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu));ids,w,g,self.grid,meta=block_basis(X,spacing,h);self.n=len(X);self.ng=len(self.grid);self.dims=meta['dims'];self.time=0.;self.steps=0;self.device='cuda:0';self.valid_accel=False;self.graphs={};self.spacing=spacing;self.h=h
  def arr(v,t):return wp.array(v,dtype=t,device=self.device)
  self.ids=arr(ids,int);self.w=arr(w,wp.float64);self.g=arr(g,wp.vec3d);self.q=arr(self.grid,wp.vec3d);self.vg=arr(np.zeros_like(self.grid),wp.vec3d);self.inverses=[arr(np.linalg.inv(m),wp.float64) for m in meta['mass1']];self.mass_matrices=meta['mass1'];self.bad=wp.zeros(1,dtype=int,device=self.device)
  for name in ['force','tmp0','tmp1','a']:setattr(self,name,wp.zeros(self.ng,dtype=wp.vec3d,device=self.device))
  for name in ['external','x','v']:setattr(self,name,wp.zeros(self.n,dtype=wp.vec3d,device=self.device))
  self.F=wp.zeros(self.n,dtype=wp.mat33d,device=self.device)
 def launch(self,f,n,args):wp.launch(f,dim=n,inputs=args,device=self.device)
 def acceleration(self):
  self.force.zero_();self.launch(k.internal,self.n,[self.q,self.ids,self.w,self.g,self.external,self.vol,self.mu,self.lam,self.force,self.bad]);dims=wp.vec3i(*self.dims)
  self.launch(k.solve_axis,self.ng,[self.force,self.tmp0,self.inverses[0],dims,0,1.]);self.launch(k.solve_axis,self.ng,[self.tmp0,self.tmp1,self.inverses[1],dims,1,1.]);self.launch(k.solve_axis,self.ng,[self.tmp1,self.a,self.inverses[2],dims,2,1/self.mass])
 def initialize(self,F=None,vg=None,q=None,external=None):
  if F is not None:self.q.assign(self.grid@np.asarray(F).T)
  if q is not None:self.q.assign(q)
  if vg is not None:self.vg.assign(vg)
  if external is not None:self.external.assign(external)
  self.valid_accel=False
 def one(self,dt):
  self.launch(k.drift,self.ng,[self.q,self.vg,self.a,dt]);self.acceleration();self.launch(k.kick,self.ng,[self.vg,self.a,dt])
 def step(self,dt,steps=1,graph=True):
  if not self.valid_accel:self.acceleration();self.valid_accel=True
  key=(float(dt),steps)
  if graph:
   if key not in self.graphs:
    wp.synchronize();wp.capture_begin(device=self.device)
    for i in range(steps):self.one(dt)
    self.graphs[key]=wp.capture_end(device=self.device)
   wp.capture_launch(self.graphs[key])
  else:
   for i in range(steps):self.one(dt)
  self.time+=dt*steps;self.steps+=steps
 def state(self):
  self.launch(k.reconstruct,self.n,[self.q,self.vg,self.ids,self.w,self.g,self.x,self.v,self.F]);return {'X':self.X.copy(),**{name:getattr(self,name).numpy() for name in ['x','v','F','q','vg']}}
 def check(self):
  s=self.state();J=np.linalg.det(s['F'])
  if self.bad.numpy()[0] or J.min()<=.1 or J.max()>=10 or not all(np.isfinite(s[n]).all() for n in ['x','v','F','q','vg']):raise RuntimeError('inadmissible trial/state')
  return s
 def metrics(self,s):
  E=self.vol*energy_stress(s['F'],self.mu,self.lam)[0].sum()+.5*self.mass*np.sum(s['v']**2);return {'energy':float(E),'momentum':self.mass*s['v'].sum(0),'angular':self.mass*np.cross(s['x'],s['v']).sum(0)}
 def save(self,path):np.savez_compressed(path,**self.check(),grid=self.grid,sim_time=self.time,steps=self.steps)
 def memory(self):
  arrays=[getattr(self,n) for n in ['ids','w','g','q','vg','bad','force','tmp0','tmp1','a','external','x','v','F']]+self.inverses;return {'array_bytes':sum(a.size*wp.types.type_size_in_bytes(a.dtype) for a in arrays),'particles':self.n,'control_points':self.ng}
