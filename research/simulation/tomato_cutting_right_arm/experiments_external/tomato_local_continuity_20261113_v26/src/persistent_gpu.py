"""Reusable GPU buffers/graphs, independent geometry streams, unchanged dynamics."""
import numpy as np
import warp as wp
from selective_gpu import GPU as ReferenceGPU
from fast_data import reduced_data

@wp.kernel
def stress(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),bad:wp.array(dtype=int),counts:wp.array(dtype=int)):
 p=wp.tid()
 if p<counts[1]:
  F=wp.identity(n=3,dtype=float);q0=q[idx[ptr[p]]]
  for e in range(ptr[p]+1,ptr[p+1]):F+=wp.outer(q[idx[e]]-q0,grad[e])
  J=wp.determinant(F)
  if J<=0.1 or J>=10.0 or not wp.isfinite(J):wp.atomic_max(bad,0,1);P[p]=wp.mat33(0.0);energy[p]=0.0
  else:
   lj=wp.log(J);P[p]=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)));norm=float(0.0)
   for i in range(3):
    for j in range(3):norm+=F[i,j]*F[i,j]
   energy[p]=vol[p]*(0.5*mu*(norm-3.0)-mu*lj+0.5*lam*lj*lj)

@wp.kernel(module='unique')
def gather(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),counts:wp.array(dtype=int)):
 t=wp.tid();i=t//32;lane=t%32;f=wp.vec3(0.0)
 if i<counts[0]:
  for e in range(ptr[i]+lane,ptr[i+1],32):f-=P[idx[e]]*grad[e]
  if lane==0:f+=external[i]
 total=wp.tile_sum(wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32)),axis=1)
 wp.tile_store(force,total,offset=(t//128)*4)

@wp.kernel
def advance(mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int),counts:wp.array(dtype=int)):
 i=wp.tid()
 if i<counts[0] and bad[0]==0:
  acc=wp.vec3(0.0)
  for k in range(mptr[i],mptr[i+1]):acc+=mi[k]*force[midx[k]]
  vn=v[i]+kick*acc;v[i]=vn
  if drift>0.:q[i]+=drift*vn
  for axis in range(3):
   if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)

def pack(aggregates,external=None):
 if not aggregates:raise ValueError('empty environment list')
 material={(a.body.mu,a.body.lam,a.body.rho) for a in aggregates}
 if len(material)!=1:raise ValueError('shared material constants required in this adapter')
 arrays={k:[] for k in ['ptr','idx','grad','iptr','iidx','ig','mptr','midx','mi','vol','q','v','external']};no=po=eo=mo=0;bounds=[0]
 for j,a in enumerate(aggregates):
  if not np.isfinite(a.q).all() or not np.isfinite(a.v).all():raise ValueError('nonfinite replacement state')
  det=np.linalg.det(a.body.fields()[2])
  if not np.isfinite(det).all() or det.min()<=.1 or det.max()>=10:raise ValueError('inadmissible replacement volume')
  d=reduced_data(a)
  arrays['ptr'].append(d['ptr'][:-1]+eo);arrays['idx'].append(d['idx']+no);arrays['grad'].append(d['grad'])
  arrays['iptr'].append(d['iptr'][:-1]+eo);arrays['iidx'].append(d['iidx']+po);arrays['ig'].append(d['ig'])
  arrays['mptr'].append(d['mptr'][:-1]+mo);arrays['midx'].append(d['midx']+no);arrays['mi'].append(d['mi'])
  arrays['vol'].append(a.body.V);arrays['q'].append(a.q);arrays['v'].append(a.v)
  arrays['external'].append(np.zeros_like(a.q) if external is None else a.E.T@np.asarray(external[j]))
  no+=len(a.q);po+=len(a.body.V);eo+=len(d['idx']);mo+=len(d['mi']);bounds.append(no)
 out={k:np.concatenate(v) for k,v in arrays.items()}
 for k,last in [('ptr',eo),('iptr',eo),('mptr',mo)]:out[k]=np.r_[out[k],last]
 out.update(n=no,p=po,e=eo,m=mo,bounds=np.array(bounds),material=next(iter(material)))
 return out

class CapacityError(ValueError):pass

class GPU:
 def __init__(self,aggregates,dt=12.5e-6,capacity_factor=1.75,external=None):
  self.dt=float(dt);d=pack(aggregates,external);self.mu,self.lam,_=d['material'];self.ncap=int(np.ceil(d['n']*capacity_factor));self.pcap=int(np.ceil(d['p']*capacity_factor));self.ecap=int(np.ceil(d['e']*capacity_factor*1.5));self.mcap=max(int(d['m']*4),self.ncap*4);self.graphs={};self.arrays={};self.replacements=0
  def arr(name,size,dtype):
   a=wp.zeros(size,dtype=dtype,device='cuda:0');self.arrays[name]=a;setattr(self,name,a)
  for name,size in [('ptr',self.pcap+1),('idx',self.ecap),('iptr',self.ncap+1),('iidx',self.ecap),('mptr',self.ncap+1),('midx',self.mcap),('bad',1),('counts',2)]:arr(name,size,int)
  for name,size in [('grad',self.ecap),('ig',self.ecap),('q',self.ncap),('vh',self.ncap),('external',self.ncap),('vfull',self.ncap),('force',self.ncap)]:arr(name,size,wp.vec3)
  arr('vol',self.pcap,float);arr('mi',self.mcap,float);arr('P',self.pcap,wp.mat33);arr('energy',self.pcap,float);self.backup=[wp.clone(self.q),wp.clone(self.vh)];self._upload(d,aggregates)
 def _fits(self,d):return d['n']<=self.ncap and d['p']<=self.pcap and d['e']<=self.ecap and d['m']<=self.mcap
 def _upload(self,d,aggregates):
  if not self._fits(d):raise CapacityError('Persistent GPU capacity exhausted; no state or history discarded')
  if d['material'][:2]!=(self.mu,self.lam):raise ValueError('material replacement forbidden')
  for key in ['ptr','idx','grad','iptr','iidx','ig','mptr','midx','mi','vol','q','external']:
   a=self.arrays[key];src=d[key];shape=(a.size,3) if a.dtype==wp.vec3 else (a.size,);padded=np.zeros(shape,dtype=np.int32 if a.dtype==wp.int32 else np.float32);padded[:len(src)]=src
   if key in ['ptr','iptr','mptr']:padded[len(src):]=src[-1]
   a.assign(padded)
  vv=np.zeros((self.ncap,3),np.float32);vv[:d['n']]=d['v'];self.vh.assign(vv);self.counts.assign(np.array([d['n'],d['p']],np.int32));self.bad.zero_()
  self.n=d['n'];self.p=d['p'];self.bounds=d['bounds'];self.aggregates=aggregates;self.base=[(a.body.time,a.body.steps) for a in aggregates];self.steps=0
  self.stress();self.advance(self.vh,-.5*self.dt,0.);self.check()
 def replace(self,aggregates,external=None):
  d=pack(aggregates,external)
  if not self._fits(d):raise CapacityError('Persistent GPU capacity exhausted before mutation')
  snapshots={k:wp.clone(a) for k,a in self.arrays.items()};old=(self.n,self.p,self.bounds,self.aggregates,self.base,self.steps)
  try:self._upload(d,aggregates)
  except Exception:
   for k,v in snapshots.items():wp.copy(self.arrays[k],v)
   self.n,self.p,self.bounds,self.aggregates,self.base,self.steps=old;raise
  self.replacements+=1
 def stress(self):wp.launch(stress,self.pcap,inputs=[self.ptr,self.idx,self.grad,self.q,self.vol,self.mu,self.lam,self.P,self.energy,self.bad,self.counts],device='cuda:0')
 def advance(self,v,kick,drift):
  wp.launch(gather,((self.ncap+3)//4)*128,inputs=[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128,device='cuda:0')
  wp.launch(advance,self.ncap,inputs=[self.mptr,self.midx,self.mi,self.force,self.q,v,kick,drift,self.bad,self.counts],device='cuda:0')
 def check(self):
  code=int(self.bad.numpy()[0])
  if code:raise ValueError(('persistent GPU mechanics rejected',code))
 def one(self):self.stress();self.advance(self.vh,self.dt,self.dt)
 def graph(self,n):
  if n not in self.graphs:
   wp.load_module(device='cuda:0');wp.capture_begin(device='cuda:0')
   try:
    for _ in range(n):self.one()
   finally:g=wp.capture_end(device='cuda:0')
   self.graphs[n]=g
  return self.graphs[n]
 def step(self,n,block=64):
  if n<=0:raise ValueError('positive step count required')
  full,rem=divmod(n,block);graphs=[self.graph(block)]*full
  if rem:graphs.append(self.graph(rem))
  wp.copy(self.backup[0],self.q);wp.copy(self.backup[1],self.vh);self.bad.zero_()
  for g in graphs:wp.capture_launch(g)
  try:self.check()
  except Exception:wp.copy(self.q,self.backup[0]);wp.copy(self.vh,self.backup[1]);self.bad.zero_();raise
  self.steps+=n
 def state(self):
  self.stress();wp.copy(self.vfull,self.vh);self.advance(self.vfull,.5*self.dt,0.);self.check();return self.q.numpy()[:self.n].astype(float),self.vfull.numpy()[:self.n].astype(float)
 def export_all(self):
  q,v=self.state();out=[]
  for j,a in enumerate(self.aggregates):
   lo,hi=self.bounds[j:j+2];a.q=q[lo:hi];a.v=v[lo:hi];a.sync();a.body.time=self.base[j][0]+self.steps*self.dt;a.body.steps=self.base[j][1]+self.steps;out.append(a.body)
  return out
 def export(self,environment=0):return self.export_all()[environment]
 def memory(self):return sum(a.size*wp.types.type_size_in_bytes(a.dtype) for a in list(self.arrays.values())+self.backup)
