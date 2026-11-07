"""Sum identical material-triangle pressure blocks before sparse assembly.

Algebraically identical barycentric GN blocks; no contact sample is removed.
The original assembly remains available for parity tests.
"""
import numpy as np
import warp as wp
from warp import sparse
from tomato_global_pressure import PressureAssembly
from tomato_global_gn_assembly import put_block

@wp.kernel(enable_backward=False)
def grouped_blocks(group:wp.array[int],bary:wp.array[wp.vec3d],hessian:wp.array[wp.mat33d],values:wp.array[wp.mat33d]):
 i,a,b=wp.tid();wp.atomic_add(values,9*group[i]+3*a+b,bary[i][a]*bary[i][b]*hessian[i])

@wp.kernel(enable_backward=False)
def grouped_indices(ids:wp.array[wp.vec3i],free:wp.array[int],accumulated:wp.array[wp.mat33d],rows:wp.array[int],columns:wp.array[int],values:wp.array[wp.mat33d]):
 i,a,b=wp.tid();at=9*i+3*a+b;put_block(at,ids[i][a],ids[i][b],accumulated[at],free,rows,columns,values)

class GroupedPressureAssembly(PressureAssembly):
 def prepare(self):
  p=self.packet;key=p.indices
  if getattr(self,'packet_key',None) is not key:
   ids,inverse=np.unique(p.indices.numpy(),axis=0,return_inverse=True);self.group_ids=wp.array(ids,dtype=wp.vec3i);self.group=wp.array(inverse.astype(np.int32),dtype=int);self.groups=len(ids);self.accumulated=wp.zeros(9*self.groups,dtype=wp.mat33d);self.rows=wp.empty(9*self.groups,dtype=int);self.columns=wp.empty(9*self.groups,dtype=int);self.values=wp.empty(9*self.groups,dtype=wp.mat33d);self.packet_key=key
 def assemble(self,x,dt):
  counts=self.base.assemble(x,dt);p=self.packet;n=p.count
  if n:
   self.prepare();self.accumulated.zero_();wp.launch(grouped_blocks,dim=(n,3,3),inputs=[self.group,p.bary,p.sample_hessian],outputs=[self.accumulated],block_dim=64);wp.launch(grouped_indices,dim=(self.groups,3,3),inputs=[self.group_ids,self.free,self.accumulated],outputs=[self.rows,self.columns,self.values],block_dim=64);sparse.bsr_set_from_triplets(self.extra,self.rows,self.columns,self.values);sparse.bsr_axpy(self.extra,self.base.matrix,alpha=1.,beta=1.)
  return dict(**counts,pressure_samples=n,pressure_triangle_groups=getattr(self,'groups',0))
