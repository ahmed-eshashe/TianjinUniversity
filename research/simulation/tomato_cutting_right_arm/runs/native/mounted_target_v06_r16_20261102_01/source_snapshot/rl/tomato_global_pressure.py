"""Double precision frozen pressure packets for the separately versioned solver.

Original material/contact forces remain unchanged. The added pressure uses
positive material-reference areas, the qualified physical soft-point moment,
and complete cross-node barycentric search blocks. This module does NOT
qualify packet generation, coverage, robot exchange or whole-system work.
Live fracture remains refused by the parent. Coupled stepping additionally
requires a separately qualified interval adapter; it is deliberately refused
here until that gate exists.
"""
import numpy as np
import warp as wp
from warp import sparse
from tomato_physical_pressure import pressure_packet
from tomato_failed_safe_global import FailedSafeFractionCandidate
from tomato_global_gn_assembly import put_block

@wp.kernel(enable_backward=False)
def scatter_double(indices:wp.array[wp.vec3i],bary:wp.array[wp.vec3d],sample_force:wp.array[wp.vec3d],force:wp.array[wp.vec3d]):
 i,corner=wp.tid();wp.atomic_add(force,indices[i][corner],bary[i][corner]*sample_force[i])

@wp.kernel(enable_backward=False)
def pressure_blocks(indices:wp.array[wp.vec3i],bary:wp.array[wp.vec3d],hessian:wp.array[wp.mat33d],free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 i,a,b=wp.tid();put_block(9*i+3*a+b,indices[i][a],indices[i][b],bary[i][a]*bary[i][b]*hessian[i],free,rows,cols,values)

@wp.kernel(enable_backward=False)
def add_pressure(force:wp.array[wp.vec3d],free:wp.array[int],mass:wp.array[wp.float64],rhs:wp.array[wp.vec3d],norm_sum:wp.array[wp.float64],maximum:wp.array[wp.float64]):
 i=wp.tid()
 if free[i]!=0:rhs[i]+=force[i];wp.atomic_add(norm_sum,0,wp.length(rhs[i]));wp.atomic_max(maximum,0,wp.length(rhs[i])/mass[i])

class FrozenPressurePacket:
 def __init__(self,n):self.n=n;self.count=0;self.force=wp.zeros(n,dtype=wp.vec3d);self.source_scope='empty'
 def set(self,*,indices,barycentric,areas,closest_local,normals_local,rotation,translation,com_local,source_scope):
  ids=np.asarray(indices,dtype=np.int32);bary=np.asarray(barycentric,dtype=float);area=np.asarray(areas,dtype=float);points=np.asarray(closest_local,dtype=float);normal=np.asarray(normals_local,dtype=float);R=np.asarray(rotation,dtype=float);t=np.asarray(translation,dtype=float);com=np.asarray(com_local,dtype=float);n=len(area)
  if ids.shape!=(n,3)or bary.shape!=(n,3)or points.shape!=(n,3)or normal.shape!=(n,3)or R.shape!=(3,3)or t.shape!=(3,)or com.shape!=(3,)or not source_scope:raise ValueError('Invalid frozen pressure packet shapes/scope')
  if any(not np.isfinite(a).all()for a in [bary,area,points,normal,R,t,com])or np.any(ids<0)or np.any(ids>=self.n)or np.any(area<=0)or np.any(bary<0)or np.max(abs(bary.sum(1)-1),initial=0)>1e-12 or np.max(abs(np.linalg.norm(normal,axis=1)-1),initial=0)>1e-10 or abs(np.linalg.det(R)-1)>1e-10 or np.max(abs(R.T@R-np.eye(3)))>1e-10:raise ValueError('Invalid positive reference-area pressure packet')
  self.count=n;self.source_scope=source_scope;self.indices=wp.array(ids,dtype=wp.vec3i);self.bary=wp.array(bary,dtype=wp.vec3d);self.area=wp.array(area,dtype=wp.float64);self.points=wp.array(points,dtype=wp.vec3d);self.normals=wp.array(normal,dtype=wp.vec3d);self.rotation=wp.array(R[None],dtype=wp.mat33d);self.translation=wp.array(t[None],dtype=wp.vec3d);self.com=wp.array(com[None],dtype=wp.vec3d);self.sample_force=wp.zeros(n,dtype=wp.vec3d);self.sample_hessian=wp.zeros(n,dtype=wp.mat33d);self.body_force=wp.zeros(n,dtype=wp.vec3d);self.body_torque=wp.zeros(n,dtype=wp.vec3d);self.energy=wp.zeros(n,dtype=wp.float64)
 def evaluate(self,x):
  self.force.zero_()
  if not self.count:return 0.
  wp.launch(pressure_packet,dim=self.count,inputs=[x,self.indices,self.bary,self.area,self.points,self.normals,self.rotation,self.translation,self.com],outputs=[self.sample_force,self.sample_hessian,self.body_force,self.body_torque,self.energy],block_dim=64);wp.launch(scatter_double,dim=(self.count,3),inputs=[self.indices,self.bary,self.sample_force],outputs=[self.force],block_dim=64);return float(self.energy.numpy().sum())
 def reaction(self):
  if not self.count:return np.zeros(6)
  return np.r_[self.body_force.numpy().sum(0),self.body_torque.numpy().sum(0)]

class PressureAssembly:
 def __init__(self,base,packet):self.base=base;self.packet=packet;self.extra=sparse.bsr_zeros(base.n,base.n,block_type=wp.mat33d,device='cuda:0')
 def __getattr__(self,name):return getattr(self.base,name)
 def assemble(self,x,dt):
  counts=self.base.assemble(x,dt);p=self.packet;n=p.count
  if n:
   rows=wp.empty(9*n,dtype=int);columns=wp.empty(9*n,dtype=int);values=wp.empty(9*n,dtype=wp.mat33d);wp.launch(pressure_blocks,dim=(n,3,3),inputs=[p.indices,p.bary,p.sample_hessian,self.free],outputs=[rows,columns,values],block_dim=64);sparse.bsr_set_from_triplets(self.extra,rows,columns,values);sparse.bsr_axpy(self.extra,self.base.matrix,alpha=1.,beta=1.)
  return dict(**counts,pressure_samples=n)

class GlobalPressureCandidate(FailedSafeFractionCandidate):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.pressure=FrozenPressurePacket(self.n);self.assembly=PressureAssembly(self.assembly,self.pressure)
 def force(self,x,dt):
  super().force(x,dt);self.pressure.evaluate(x);self.norm_sum.zero_();self.maximum_acceleration_defect.zero_();wp.launch(add_pressure,dim=self.n,inputs=[self.pressure.force,self.assembly.free,self.assembly.mass],outputs=[self.rhs,self.norm_sum,self.maximum_acceleration_defect],block_dim=64);return float(self.norm_sum.numpy()[0])
 def energy(self,x,dt,*,trial=False):return super().energy(x,dt,trial=trial)+self.pressure.evaluate(x)
 def step(self,*args,**kwargs):raise ValueError('Frozen pressure operators only: generated coverage and actual mounted interval/work adapter not qualified')
