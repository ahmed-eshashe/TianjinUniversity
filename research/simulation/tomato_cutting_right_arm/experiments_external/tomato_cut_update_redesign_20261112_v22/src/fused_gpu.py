"""Same stress, exact inverse inertia and staggered Verlet; fused gather/kick.

P is read-only throughout the fused launch, so all force contributions use the
same material state. No node reads another node's changing velocity/position.
"""
import warp as wp
from persistent_gpu import GPU as StorageGPU,CapacityError

@wp.kernel(module='unique')
def gather_advance(iptr:wp.array(dtype=int),iidx:wp.array(dtype=int),ig:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),q:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int),counts:wp.array(dtype=int)):
 t=wp.tid();i=t//32;lane=t%32;acc=wp.vec3(0.0)
 # All four rows in a block participate in each tile reduction. Padding is
 # inactive, not material. Mixed row lengths cannot skip a tile barrier.
 width=int(0)
 if i<counts[0]:width=mptr[i+1]-mptr[i]
 widths=wp.tile(width,preserve_type=True)
 widthmax=wp.tile_max(widths)
 steps=wp.untile(wp.tile_broadcast(widthmax,shape=(128,)))
 for m in range(steps):
  f=wp.vec3(0.0);weight=float(0.0)
  if m<width:
   e=mptr[i]+m;j=midx[e];weight=mi[e]
   for e2 in range(iptr[j]+lane,iptr[j+1],32):f-=P[iidx[e2]]*ig[e2]
   if lane==0:f+=external[j]
  total=wp.tile_sum(wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32)),axis=1)
  # Broadcast each reduced row back to its 32 lanes; only lane zero writes.
  ff=wp.tile_broadcast(wp.tile_reshape(total,(4,1)),shape=(4,32))
  copied=wp.tile_zeros(shape=(4,32),dtype=wp.vec3)
  wp.tile_assign(copied,ff)
  force=wp.untile(wp.tile_reshape(copied,(128,)))
  acc+=weight*force
 if lane==0 and i<counts[0] and bad[0]==0:
  vn=velocity[i]+kick*acc;velocity[i]=vn
  if drift>0.:q[i]+=drift*vn
  for axis in range(3):
   if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)

class GPU(StorageGPU):
 def advance(self,v,kick,drift):
  wp.launch(gather_advance,((self.ncap+3)//4)*128,inputs=[self.iptr,self.iidx,self.ig,self.P,self.external,self.mptr,self.midx,self.mi,self.q,v,kick,drift,self.bad,self.counts],block_dim=128,device='cuda:0')
