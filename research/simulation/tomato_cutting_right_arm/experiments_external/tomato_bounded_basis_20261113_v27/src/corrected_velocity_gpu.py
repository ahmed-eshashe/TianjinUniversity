"""Velocity-dependent Verlet with explicit predictor/corrector iterations.

The normal, friction and bulk forces are unchanged. The last force is used both
for the accepted half-kick and its work/impulse ledger. Temporal refinement is
required; a fixed number of corrections is not an implicit convergence claim.
"""
import warp as wp
from parallel_partition_gpu import ContactGPU as Base,TriangleSurface
from contact_gpu import drift
from contact_gpu_precise import tick_precise

@wp.kernel
def estimate(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),mass_inv:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),base:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),dt:float,n:int,bad:wp.array(dtype=int)):
 i=wp.tid()
 if i<n and bad[0]==0:
  if fixed[i]!=0:v[i]=wp.vec3(0.)
  else:
   acc=wp.vec3(0.)
   for j in range(ptr[i],ptr[i+1]):acc+=mass_inv[j]*force[ids[j]]
   v[i]=base[i]+dt*acc

class ContactGPU(Base):
 def __init__(self,*args,corrections=2,**kwargs):
  self.corrected=False;super().__init__(*args,**kwargs);self.corrections=corrections;self.mid_velocity=wp.empty_like(self.vh);self.corrected=True
 def one(self):
  if not self.corrected:return super().one()
  self.contact_force();self.half_kick();wp.launch(drift,self.n,[self.q,self.vh,self.dt,self.n,self.bad,self.maxspeed]);wp.launch(tick_precise,1,[self.clock,wp.float64(self.dt),self.bad]);wp.copy(self.mid_velocity,self.vh)
  for _ in range(self.corrections):
   self.contact_force();wp.launch(estimate,self.n,[self.mptr,self.midx,self.mi,self.force,self.mid_velocity,self.vh,self.fixed,.5*self.dt,self.n,self.bad])
  self.contact_force();wp.copy(self.vh,self.mid_velocity);self.half_kick()
