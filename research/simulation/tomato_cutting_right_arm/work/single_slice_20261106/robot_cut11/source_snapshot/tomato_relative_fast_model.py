"""Same relative-coordinate model with verified color-only cohesive assembly."""
import warp as wp
from tomato_relative_full_model import RelativeObjectiveVBD
from tomato_relative_kernels import reconstruct,relative_bulk,relative_plane
from tomato_cohesive_color_blocks import cohesive_color_blocks

class RelativeFastObjectiveVBD(RelativeObjectiveVBD):
 def _gather_blocks(self,color,state,dt):
  from tomato_native_objective_reference import validate_frames,add_objective_blocks
  wp.launch(reconstruct,dim=self.model.particle_count,inputs=[self.spatial_reference,state.particle_q],outputs=[self.objective_x],block_dim=64);wp.launch(relative_bulk,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_x,self.spring_offsets,self.spring_ids,self.model.spring_indices,self.relative_spring_rest,self.relative_spring_k,self.cell_offsets,self.cell_ids,self.cells,self.volumes64],outputs=[self.volume_invalid,self.particle_forces,self.particle_hessians],block_dim=64);wp.launch(validate_frames,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.objective_anchors],outputs=[self.objective_invalid]);self.objective_force.zero_();self.objective_hessian.zero_();common=[self.objective_x,self.pairs,self.counts,self.objective_anchors,self.objective_sign,self.objective_weights,self.objective_stiffness,self.objective_law,self.objective_history,self.eligible]
  wp.launch(cohesive_color_blocks,dim=(self.pairs.shape[0],16),inputs=[color,self.model.particle_colors,*common],outputs=[self.objective_force,self.objective_hessian],block_dim=32);wp.launch(add_objective_blocks,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_force,self.objective_hessian],outputs=[self.particle_forces,self.particle_hessians]);wp.launch(relative_plane,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_x,self.board_stiffness,wp.float64(self.board_height)],outputs=[self.particle_forces,self.particle_hessians],block_dim=64);self.surface_contact.current_color=color
  try:self.surface_contact.evaluate(state.particle_q,dt)
  finally:self.surface_contact.current_color=-1
  self.surface_contact.scatter(color,self.model.particle_colors,self.particle_forces,self.particle_hessians)
