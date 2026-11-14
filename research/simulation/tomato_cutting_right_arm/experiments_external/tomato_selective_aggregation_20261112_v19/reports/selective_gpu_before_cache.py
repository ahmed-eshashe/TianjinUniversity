"""Fixed-topology GPU equivalent: reduced inertia and staggered Verlet velocity.

Two launches per material substep. Full velocities are reconstructed for export
and before changing external forces. No contact or geometry update is implied.
"""
from pathlib import Path
import numpy as np
from scipy.linalg import cho_solve
import warp as wp

wp.config.kernel_cache_dir=str(Path(__file__).resolve().parents[1]/'cache/warp')
wp.config.enable_backward=False
wp.init()

@wp.kernel
def stress(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),bad:wp.array(dtype=int)):
 p=wp.tid()
 F=wp.identity(n=3,dtype=float)
 q0=q[idx[ptr[p]]]
 for e in range(ptr[p]+1,ptr[p+1]):
  F+=wp.outer(q[idx[e]]-q0,grad[e])
 J=wp.determinant(F)
 if J<=0.1 or J>=10.0 or not wp.isfinite(J):
  wp.atomic_max(bad,0,1)
  P[p]=wp.mat33(0.0)
  energy[p]=0.0
 else:
  lj=wp.log(J)
  P[p]=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)))
  norm=float(0.0)
  for i in range(3):
   for j in range(3):norm+=F[i,j]*F[i,j]
  energy[p]=vol[p]*(0.5*mu*(norm-3.0)-mu*lj+0.5*lam*lj*lj)

@wp.kernel
def advance(iptr:wp.array(dtype=int),iidx:wp.array(dtype=int),ig:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),external:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int)):
 i=wp.tid()
 acc=wp.vec3(0.0)
 for k in range(mptr[i],mptr[i+1]):
  j=midx[k]
  force=external[j]
  for e in range(iptr[j],iptr[j+1]):force-=P[iidx[e]]*ig[e]
  acc+=mi[k]*force
 if bad[0]==0:
  vn=v[i]+kick*acc
  v[i]=vn
  if drift>0.0:q[i]+=drift*vn
  for axis in range(3):
   if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)

def reduced_data(a):
 b=a.body;E=a.E;ptr=[0];idx=[];grad=[]
 for p,ids in enumerate(b.ids):
  row={}
  for k,old in enumerate(ids):
   for e in range(E.indptr[old],E.indptr[old+1]):
    j=int(E.indices[e]);row[j]=row.get(j,np.zeros(3))+E.data[e]*b.G[p,k]
  keys=sorted(j for j,g in row.items() if np.any(g!=0))
  gg=np.array([row[j] for j in keys]);gg[0]=-gg[1:].sum(0)
  idx.extend(keys);grad.extend(gg);ptr.append(len(idx))
 idx=np.asarray(idx,np.int32);grad=np.asarray(grad);regions=np.repeat(np.arange(len(b.V)),np.diff(ptr));order=np.argsort(idx,kind='stable');iptr=np.r_[0,np.cumsum(np.bincount(idx,minlength=len(a.q)))].astype(np.int32)
 massrows=[[] for _ in range(len(a.q))]
 for ids,factor in zip(a.blocks,a.factors):
  inv=cho_solve(factor,np.eye(len(ids)),check_finite=False)
  for ii,i in enumerate(ids):massrows[i]=[(int(j),float(inv[ii,jj])) for jj,j in enumerate(ids) if inv[ii,jj]!=0]
 mptr=[0];midx=[];mi=[]
 for row in massrows:
  for j,v in row:midx.append(j);mi.append(v)
  mptr.append(len(midx))
 return {'ptr':np.array(ptr,np.int32),'idx':idx,'grad':grad,'iptr':iptr,'iidx':regions[order].astype(np.int32),'ig':grad[order],'mptr':np.array(mptr,np.int32),'midx':np.array(midx,np.int32),'mi':np.array(mi)}

class GPU:
 def __init__(self,aggregate,dt=12.5e-6,batch=1,external=None):
  self.aggregate=aggregate;self.body=aggregate.body;self.dt=float(dt);self.batch=int(batch);self.n=len(aggregate.q);self.p=len(self.body.V);self.steps=0;self.time0=self.body.time;self.steps0=self.body.steps;self.graphs={};self.arrays=[]
  d=reduced_data(aggregate)
  def ptr_batch(ptr):return np.r_[np.concatenate([ptr[:-1]+k*ptr[-1] for k in range(batch)]),batch*ptr[-1]].astype(np.int32)
  def indices(x,stride):return np.concatenate([x+k*stride for k in range(batch)])
  def array(x,dtype):
   out=wp.array(np.ascontiguousarray(x),dtype=dtype,device='cuda:0');self.arrays.append(out);return out
  self.ptr=array(ptr_batch(d['ptr']),int);self.idx=array(indices(d['idx'],self.n),int);self.grad=array(np.tile(d['grad'],(batch,1)),wp.vec3);self.vol=array(np.tile(self.body.V,batch),float)
  self.iptr=array(ptr_batch(d['iptr']),int);self.iidx=array(indices(d['iidx'],self.p),int);self.ig=array(np.tile(d['ig'],(batch,1)),wp.vec3)
  self.mptr=array(ptr_batch(d['mptr']),int);self.midx=array(indices(d['midx'],self.n),int);self.mi=array(np.tile(d['mi'],batch),float)
  self.q=array(np.tile(aggregate.q,(batch,1)),wp.vec3);self.vh=array(np.tile(aggregate.v,(batch,1)),wp.vec3);self.external=array(self._external(external),wp.vec3)
  self.P=array(np.zeros((batch*self.p,3,3)),wp.mat33);self.energy=array(np.zeros(batch*self.p),float);self.bad=array(np.zeros(1,np.int32),int);self.vfull=array(np.zeros((batch*self.n,3)),wp.vec3);self.backup=[wp.clone(self.q),wp.clone(self.vh)]
  self.stress();self.advance(self.vh,-.5*self.dt,0.0);self.check()
 def _external(self,f):
  if f is None:return np.zeros((self.batch*self.n,3))
  f=np.asarray(f)
  if f.ndim==2:f=np.broadcast_to(f,(self.batch,)+f.shape)
  if f.shape!=(self.batch,len(self.body.u),3):raise ValueError('external force shape')
  return np.concatenate([self.aggregate.E.T@ff for ff in f])
 def stress(self):
  wp.launch(stress,self.batch*self.p,inputs=[self.ptr,self.idx,self.grad,self.q,self.vol,self.body.mu,self.body.lam,self.P,self.energy,self.bad],device='cuda:0')
 def advance(self,v,kick,drift):
  wp.launch(advance,self.batch*self.n,inputs=[self.iptr,self.iidx,self.ig,self.P,self.mptr,self.midx,self.mi,self.external,self.q,v,kick,drift,self.bad],device='cuda:0')
 def check(self):
  code=int(self.bad.numpy()[0])
  if code:raise ValueError(('GPU mechanics rejected',code))
 def one(self):self.stress();self.advance(self.vh,self.dt,self.dt)
 def graph(self,n):
  if n not in self.graphs:
   wp.load_module(device='cuda:0');wp.capture_begin(device='cuda:0')
   try:
    for _ in range(n):self.one()
   finally:graph=wp.capture_end(device='cuda:0')
   self.graphs[n]=graph
  return self.graphs[n]
 def step(self,n,block=64):
  if n<=0:raise ValueError('positive step count required')
  full,rem=divmod(n,block);graphs=[]
  if full:graphs=[self.graph(block)]*full
  if rem:graphs.append(self.graph(rem))
  wp.copy(self.backup[0],self.q);wp.copy(self.backup[1],self.vh);self.bad.zero_()
  for graph in graphs:wp.capture_launch(graph)
  try:self.check()
  except Exception:
   wp.copy(self.q,self.backup[0]);wp.copy(self.vh,self.backup[1]);raise
  self.steps+=n
 def state(self):
  self.stress();wp.copy(self.vfull,self.vh);self.advance(self.vfull,.5*self.dt,0.0);self.check()
  return self.q.numpy().reshape(self.batch,self.n,3).astype(float),self.vfull.numpy().reshape(self.batch,self.n,3).astype(float)
 def export(self,environment=0):
  q,v=self.state();self.aggregate.q=q[environment];self.aggregate.v=v[environment];self.aggregate.sync();self.body.time=self.time0+self.steps*self.dt;self.body.steps=self.steps0+self.steps;return self.body
 def set_external(self,f):
  q,v=self.state();self.external.assign(self._external(f));self.vh.assign(v.reshape(-1,3));self.bad.zero_();self.stress();self.advance(self.vh,-.5*self.dt,0.0);self.check()
 def memory(self):return sum(x.size*wp.types.type_size_in_bytes(x.dtype) for x in self.arrays+self.backup)
