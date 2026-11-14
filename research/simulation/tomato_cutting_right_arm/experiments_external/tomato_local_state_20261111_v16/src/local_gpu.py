from pathlib import Path
import numpy as np
import warp as wp
wp.config.kernel_cache_dir=str(Path(__file__).resolve().parents[1]/'cache/warp');wp.config.enable_backward=False;wp.init()

@wp.kernel
def stress(ids:wp.array2d(dtype=int),grad:wp.array2d(dtype=wp.vec3),u:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),bad:wp.array(dtype=int)):
 p=wp.tid();F=wp.identity(n=3,dtype=float);u0=u[ids[p,0]]
 for j in range(1,8):F+=wp.outer(u[ids[p,j]]-u0,grad[p,j])
 J=wp.determinant(F)
 if J<=0.1 or J>=10.0 or not wp.isfinite(J):wp.atomic_max(bad,0,1);P[p]=wp.mat33(0.0);energy[p]=0.0
 else:
  lj=wp.log(J);P[p]=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)));s=float(0.)
  for i in range(3):
   for j in range(3):s+=F[i,j]*F[i,j]
  energy[p]=vol[p]*(.5*mu*(s-3.)-mu*lj+.5*lam*lj*lj)

@wp.kernel
def update(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),mass:wp.array(dtype=float),external:wp.array(dtype=wp.vec3),u:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dt:float,drift:int,bad:wp.array(dtype=int)):
 i=wp.tid();force=external[i]
 for e in range(ptr[i],ptr[i+1]):force-=P[idx[e]]*grad[e]
 if bad[0]==0:
  vn=v[i]+(.5*dt/mass[i])*force;v[i]=vn
  if drift==1:u[i]+=dt*vn
  for j in range(3):
   if not wp.isfinite(vn[j]) or not wp.isfinite(u[i][j]):wp.atomic_max(bad,0,2)

class GPU:
 def __init__(self,body,dt=.0000125,external=None):
  self.body=body;self.dt=float(dt);self.steps=0;self.time0=body.time;self.steps0=body.steps;self.graphs={};self.arrays=[]
  def a(v,t):
   r=wp.array(np.ascontiguousarray(v),dtype=t,device='cuda:0');self.arrays.append(r);return r
  self.ids=a(body.ids,int);self.grad=a(body.G,wp.vec3);self.u=a(body.u,wp.vec3);self.v=a(body.v,wp.vec3);self.vol=a(body.V,float);self.mass=a(body.mass,float);self.ptr=a(body.ptr,int);self.idx=a(body.edge_p,int);self.edgeg=a(body.edge_g,wp.vec3);self.external=a(np.zeros_like(body.u) if external is None else external,wp.vec3);self.P=a(np.zeros((len(body.X),3,3)),wp.mat33);self.energy=a(np.zeros(len(body.X)),float);self.bad=a(np.zeros(1,np.int32),int);self.backup=[wp.clone(self.u),wp.clone(self.v)]
 def one(self):
  for drift in [1,0]:
   wp.launch(stress,len(self.body.X),inputs=[self.ids,self.grad,self.u,self.vol,self.body.mu,self.body.lam,self.P,self.energy,self.bad],device='cuda:0')
   wp.launch(update,len(self.body.u),inputs=[self.ptr,self.idx,self.edgeg,self.P,self.mass,self.external,self.u,self.v,self.dt,drift,self.bad],device='cuda:0')
 def graph(self,n):
  if n not in self.graphs:
   wp.load_module(device='cuda:0');wp.capture_begin(device='cuda:0')
   try:
    for _ in range(n):self.one()
   finally:g=wp.capture_end(device='cuda:0')
   self.graphs[n]=g
  return self.graphs[n]
 def step(self,n=1,block=64):
  if n<=0:raise ValueError('positive step count required')
  full,rem=divmod(n,block);graphs=[]
  if full:graphs=[self.graph(block)]*full
  if rem:graphs.append(self.graph(rem))
  wp.copy(self.backup[0],self.u);wp.copy(self.backup[1],self.v);self.bad.zero_()
  for g in graphs:wp.capture_launch(g)
  code=int(self.bad.numpy()[0])
  if code:
   wp.copy(self.u,self.backup[0]);wp.copy(self.v,self.backup[1]);raise ValueError(('GPU mechanics rejected',code))
  self.steps+=n
 def export(self):
  self.body.u=self.u.numpy().astype(float);self.body.v=self.v.numpy().astype(float);self.body.time=self.time0+self.steps*self.dt;self.body.steps=self.steps0+self.steps;return self.body
 def memory(self):return sum(x.size*wp.types.type_size_in_bytes(x.dtype) for x in self.arrays+self.backup)
