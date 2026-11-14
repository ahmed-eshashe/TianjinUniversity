"""Complete physical collision surface driven by rest-relative mechanical state."""
import warp as wp
from tomato_colored_contact import ColoredFastMollifiedContact,current_contact_colored
from tomato_relative_kernels import physical_point

@wp.kernel(enable_backward=False)
def embed_relative(reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],indices:wp.array[wp.vec4i],weights:wp.array[wp.vec4d],precise:wp.array[wp.vec3d],query:wp.array[wp.vec3]):
 i=wp.tid();p=wp.vec3d(0.)
 for j in range(4):p+=weights[i][j]*physical_point(reference,u,indices[i][j])
 precise[i]=p;query[i]=wp.vec3(float(p[0]),float(p[1]),float(p[2]))

class RelativeSurfaceContact(ColoredFastMollifiedContact):
 def __init__(self,data,reference,**kwargs):
  super().__init__(data,**kwargs);self.reference=reference
 def detect(self,u):
  from tomato_embedded_self_contact import physical_bounds
  from tomato_relative_contact_bounds import precise_contact_bounds
  from tomato_mollified_self_contact import candidate_pairs
  from tomato_fast_mollified_contact import cache_embedding
  wp.copy(self.query_physical,u) # query displacement: differences equal physical motion
  wp.launch(embed_relative,dim=self.model.particle_count,inputs=[self.reference,u,self.indices,self.weights],outputs=[self.precise_position,self.state.particle_q],block_dim=64);wp.copy(self.previous,self.state.particle_q);self.solver._collision_detection_penetration_free(self.state);self.proxy_bounds.fill_(self.relaxation*(self.query_radius-self.margin))
  wp.launch(precise_contact_bounds,dim=max(self.model.particle_count,self.model.edge_count),inputs=[self.precise_position,self.model.tri_indices,self.model.edge_indices,self.solver.trimesh_collision_info,self.relaxation],outputs=[self.proxy_bounds,self.invalid]);wp.launch(physical_bounds,dim=self.node_count,inputs=[self.offsets,self.rows,self.proxy_bounds],outputs=[self.bounds]);self.stencil_count.zero_()
  wp.launch(candidate_pairs,dim=max(self.model.particle_count,self.model.edge_count),inputs=[self.rest_precise,self.model.tri_indices,self.model.edge_indices,self.solver.trimesh_collision_info,self.stencil_capacity],outputs=[self.endpoint,self.kind,self.mollifier_threshold,self.stencil_count,self.invalid]);wp.launch(cache_embedding,dim=self.stencil_capacity,inputs=[self.endpoint,self.stencil_count,self.stencil_capacity,self.indices,self.weights],outputs=[self.physical_ids,self.endpoint_weight])
 def evaluate(self,u,dt):
  wp.launch(embed_relative,dim=self.model.particle_count,inputs=[self.reference,u,self.indices,self.weights],outputs=[self.precise_position,self.state.particle_q],block_dim=64);self.force.zero_();self.hessian.zero_();self.physical_force.zero_();self.physical_hessian.zero_();self.contact_energy.zero_()
  wp.launch(current_contact_colored,dim=self.stencil_capacity,inputs=[self.current_color,self.physical_colors,self.precise_position,self.physical_ids,self.endpoint_weight,self.endpoint,self.kind,self.mollifier_threshold,self.stencil_count,self.stencil_capacity,wp.float64(self.margin),wp.float64(self.model.soft_contact_ke)],outputs=[self.physical_force,self.physical_hessian,self.force,self.hessian,self.contact_energy,self.invalid],block_dim=64)
