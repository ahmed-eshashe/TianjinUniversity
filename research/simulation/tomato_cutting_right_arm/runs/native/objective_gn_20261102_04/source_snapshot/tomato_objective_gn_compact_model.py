"""Exact objective force with positive GN blocks; versioned solver candidate."""
import warp as wp
from tomato_objective_full_model import ObjectiveTomatoVBD
from tomato_contact_full_model import EmbeddedContactMixin

class ObjectiveGNTomatoVBD(ObjectiveTomatoVBD):
 def _gather_blocks(self,color,state,dt):
  from tomato_objective_bulk_gather import gather_bulk
  from tomato_board_support import plane_blocks
  from tomato_native_objective_reference import cast_positions,objective_force,validate_frames,add_objective_blocks
  from tomato_objective_gn_compact import objective_gn
  wp.launch(gather_bulk,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,state.particle_q,self.particle_q_prev,dt,self.spring_offsets,self.spring_ids,self.model.spring_indices,self.model.spring_rest_length,self.model.spring_stiffness,self.model.spring_damping,self.patch_offsets,self.patch_ids,self.pairs,self.rest,self.weights,self.counts,self.stiffness,self.law,self.history,self.eligible,self.invalid,self.cell_offsets,self.cell_ids,self.cells,self.volumes,self.volume_invalid],outputs=[self.particle_forces,self.particle_hessians],device=self.device)
  wp.launch(cast_positions,dim=self.model.particle_count,inputs=[state.particle_q],outputs=[self.objective_x],device=self.device)
  wp.launch(validate_frames,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.objective_anchors],outputs=[self.objective_invalid],device=self.device)
  self.objective_force.zero_();self.objective_hessian.zero_()
  common=[self.objective_x,self.pairs,self.counts,self.objective_anchors,self.objective_sign,self.objective_weights,self.objective_stiffness,self.objective_law,self.objective_history,self.eligible]
  wp.launch(objective_force,dim=self.pairs.shape[0],inputs=common,outputs=[self.objective_force],device=self.device)
  wp.launch(objective_gn,dim=(self.pairs.shape[0],16),inputs=common,outputs=[self.objective_hessian],device=self.device)
  wp.launch(add_objective_blocks,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_force,self.objective_hessian],outputs=[self.particle_forces,self.particle_hessians],device=self.device)
  wp.launch(plane_blocks,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,state.particle_q,self.board_stiffness,self.board_height],outputs=[self.particle_forces,self.particle_hessians],device=self.device)

class ContactObjectiveGNTomatoVBD(EmbeddedContactMixin,ObjectiveGNTomatoVBD):pass
