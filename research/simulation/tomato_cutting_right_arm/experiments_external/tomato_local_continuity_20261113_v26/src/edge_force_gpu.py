"""Store each material-to-node force once, then gather in reference order."""
import numpy as np
import warp as wp
from cached_gpu import GPU as StorageGPU,CapacityError
from persistent_gpu import advance
from fast_data import reduced_data

@wp.kernel
def stress_edges(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),edgeforce:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),counts:wp.array(dtype=int)):
 p=wp.tid()
 if p<counts[1]:
  F=wp.identity(n=3,dtype=float);q0=q[idx[ptr[p]]]
  for e in range(ptr[p]+1,ptr[p+1]):F+=wp.outer(q[idx[e]]-q0,grad[e])
  J=wp.determinant(F);stress=wp.mat33(0.0)
  if J<=0.1 or J>=10.0 or not wp.isfinite(J):wp.atomic_max(bad,0,1);P[p]=wp.mat33(0.0);energy[p]=0.0
  else:
   lj=wp.log(J);stress=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)));P[p]=stress;norm=float(0.0)
   for i in range(3):
    for j in range(3):norm+=F[i,j]*F[i,j]
   energy[p]=vol[p]*(0.5*mu*(norm-3.0)-mu*lj+0.5*lam*lj*lj)
  for e in range(ptr[p],ptr[p+1]):edgeforce[e]=stress*grad[e]

@wp.kernel(module='unique')
def gather_edges(ptr:wp.array(dtype=int),edge:wp.array(dtype=int),edgeforce:wp.array(dtype=wp.vec3),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),counts:wp.array(dtype=int)):
 t=wp.tid();i=t//32;lane=t%32;f=wp.vec3(0.0)
 if i<counts[0]:
  for e in range(ptr[i]+lane,ptr[i+1],32):f-=edgeforce[edge[e]]
  if lane==0:f+=external[i]
 total=wp.tile_sum(wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32)),axis=1)
 wp.tile_store(force,total,offset=(t//128)*4)

class GPU(StorageGPU):
 def _upload(self,d,aggregates):
  if not hasattr(self,'edgeforce'):
   self.edgeforce=wp.zeros(self.ecap,dtype=wp.vec3,device='cuda:0');self.iedge=wp.zeros(self.ecap,dtype=int,device='cuda:0')
   self.arrays.update(edgeforce=self.edgeforce,iedge=self.iedge)
   self.rollback.update(edgeforce=wp.empty_like(self.edgeforce),iedge=wp.empty_like(self.iedge))
   self.staging['iedge']=wp.empty(self.ecap,dtype=int,device='cpu',pinned=True);self.host['iedge']=self.staging['iedge'].numpy()
  order=np.argsort(d['idx'],kind='stable').astype(np.int32)
  self.host['iedge'][:len(order)]=order;wp.copy(self.iedge,self.staging['iedge'],count=len(order))
  super()._upload(d,aggregates)
 def stress(self):
  wp.launch(stress_edges,self.pcap,inputs=[self.ptr,self.idx,self.grad,self.q,self.vol,self.mu,self.lam,self.P,self.energy,self.edgeforce,self.bad,self.counts],device='cuda:0')
 def advance(self,v,kick,drift):
  wp.launch(gather_edges,((self.ncap+3)//4)*128,inputs=[self.iptr,self.iedge,self.edgeforce,self.external,self.force,self.counts],block_dim=128,device='cuda:0')
  wp.launch(advance,self.ncap,inputs=[self.mptr,self.midx,self.mi,self.force,self.q,v,kick,drift,self.bad,self.counts],device='cuda:0')
