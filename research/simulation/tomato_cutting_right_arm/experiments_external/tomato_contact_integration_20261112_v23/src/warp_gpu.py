"""One GPU warp per exact inverse-mass row; identical material integration."""
import warp as wp
from persistent_gpu import GPU as StorageGPU,CapacityError

@wp.kernel(module='unique')
def gather_advance(iptr:wp.array(dtype=int),iidx:wp.array(dtype=int),ig:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),q:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int),counts:wp.array(dtype=int)):
 t=wp.tid();i=t//32;lane=t%32;acc=wp.vec3(0.0)
 if i<counts[0]:
  for m in range(mptr[i],mptr[i+1]):
   f=wp.vec3(0.0);j=midx[m]
   for e in range(iptr[j]+lane,iptr[j+1],32):f-=P[iidx[e]]*ig[e]
   if lane==0:f+=external[j]
   total=wp.tile_sum(wp.tile(f,preserve_type=True))
   force=wp.tile_extract(total,0)
   acc+=mi[m]*force
  if lane==0 and bad[0]==0:
   vn=velocity[i]+kick*acc;velocity[i]=vn
   if drift>0.:q[i]+=drift*vn
   for axis in range(3):
    if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)

class GPU(StorageGPU):
 def advance(self,v,kick,drift):
  wp.launch(gather_advance,self.ncap*32,inputs=[self.iptr,self.iidx,self.ig,self.P,self.external,self.mptr,self.midx,self.mi,self.q,v,kick,drift,self.bad,self.counts],block_dim=32,device='cuda:0')
