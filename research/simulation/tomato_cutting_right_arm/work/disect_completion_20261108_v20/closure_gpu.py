"""GPU-resident evaluation of the preserved contact proxy and force law."""
import torch
import warp as wp
from preserved_closure import Closure
from tomato_fast_mollified_contact import current_contact_fast

@wp.kernel
def embed_double(q:wp.array(dtype=wp.vec3d),ids:wp.array(dtype=wp.vec4i),weights:wp.array(dtype=wp.vec4d),out:wp.array(dtype=wp.vec3d)):
 i=wp.tid();p=wp.vec3d(0.0)
 for j in range(4):p+=weights[i][j]*q[ids[i][j]]
 out[i]=p

class ClosureGPU:
 def __init__(self,source):
  self.reference=Closure(source);self.engine=self.reference.engine
 def evaluate(self,q):
  e=self.engine
  # Detection retains the original float32 geometry; forces use double embedding.
  self.query=q.to(torch.float32).contiguous()
  e.invalid.zero_();e.detect(wp.from_torch(self.query,dtype=wp.vec3))
  wp.launch(embed_double,dim=len(e.embedding['indices']),inputs=[wp.from_torch(q,dtype=wp.vec3d),e.indices,e.weights],outputs=[e.precise_position])
  e.force.zero_();e.hessian.zero_();e.physical_force.zero_();e.physical_hessian.zero_();e.contact_energy.zero_()
  wp.launch(current_contact_fast,dim=e.stencil_capacity,inputs=[e.precise_position,e.physical_ids,e.endpoint_weight,e.endpoint,e.kind,e.mollifier_threshold,e.stencil_count,e.stencil_capacity,wp.float64(e.margin),wp.float64(e.model.soft_contact_ke)],outputs=[e.physical_force,e.physical_hessian,e.force,e.hessian,e.contact_energy,e.invalid])
  return wp.to_torch(e.physical_force)
