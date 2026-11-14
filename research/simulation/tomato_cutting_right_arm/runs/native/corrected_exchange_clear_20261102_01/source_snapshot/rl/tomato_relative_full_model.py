"""Precision-extension candidate: u=x-X, exact source geometry in float64.

No material/topology/mass retuning. Original central springs and volume barrier
remain; force and geometric evaluations retain precision until native VBD block
assembly. All 5,504 collision triangles live in the complete proxy model.
The mechanical model omits the old zero-stiffness render triangles so native
elasticity never evaluates a collapsed displacement-space triangle.
"""
import numpy as np
import warp as wp
import newton
from tomato_objective_full_model import ObjectiveTomatoVBD,configure_objective
from tomato_relative_kernels import reconstruct,relative_bulk,relative_plane,relative_predictor_check,relative_colored_step

class RelativeObjectiveVBD(ObjectiveTomatoVBD):
 def _initialize_particles(self,state_in,state_out,dt):
  self.surface_contact.detect(state_in.particle_q)
  super()._initialize_particles(state_in,state_out,dt)
 def _solve_particle_iteration(self,state_in,state_out,contacts,dt,iter_num):
  # Refresh after prediction and between iterations: bounds must not impose
  # a permanent per-step velocity cap on two faces moving together.
  self.surface_contact.detect(state_in.particle_q)
  super()._solve_particle_iteration(state_in,state_out,contacts,dt,iter_num)
 def _penetration_free_truncation(self,particle_q_out=None):
  from tomato_native_volume_steps import apply_predictor
  from tomato_checked_volume_steps import finish_predictor,reject_unverified_predictor
  self.surface_contact.cap(-1,self.model.particle_colors,self.pos_prev_collision_detection,self.particle_displacements);self.volume_step_fraction.fill_(1.);self.candidate_active.fill_(1)
  for _ in range(40):
   self.candidate_bad.zero_();wp.launch(relative_predictor_check,dim=self.cells.size,inputs=[self.spatial_reference,self.pos_prev_collision_detection,self.particle_displacements,self.cells,self.volumes64,self.volume_step_fraction,self.candidate_active],outputs=[self.candidate_bad,self.volume_invalid],block_dim=64);wp.launch(finish_predictor,dim=1,inputs=[self.volume_step_fraction,self.candidate_active,self.candidate_bad])
  wp.launch(reject_unverified_predictor,dim=1,inputs=[self.volume_step_fraction,self.candidate_active,self.volume_invalid]);wp.launch(apply_predictor,dim=self.model.particle_count,inputs=[particle_q_out,self.pos_prev_collision_detection,self.particle_displacements,self.volume_step_fraction])
 def _volume_safe_update(self,color,positions):
  self.surface_contact.cap(color,self.model.particle_colors,self.pos_prev_collision_detection,self.particle_displacements);wp.launch(relative_colored_step,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.spatial_reference,positions,self.pos_prev_collision_detection,self.particle_displacements,self.cell_offsets,self.cell_ids,self.cells,self.volumes64],outputs=[self.volume_invalid,self.volume_clip_count],block_dim=64)
 def _gather_blocks(self,color,state,dt):
  from tomato_native_objective_reference import objective_force,validate_frames,add_objective_blocks
  from tomato_objective_gn_compact import objective_gn
  wp.launch(reconstruct,dim=self.model.particle_count,inputs=[self.spatial_reference,state.particle_q],outputs=[self.objective_x],block_dim=64)
  wp.launch(relative_bulk,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_x,self.spring_offsets,self.spring_ids,self.model.spring_indices,self.relative_spring_rest,self.relative_spring_k,self.cell_offsets,self.cell_ids,self.cells,self.volumes64],outputs=[self.volume_invalid,self.particle_forces,self.particle_hessians],block_dim=64)
  wp.launch(validate_frames,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.objective_anchors],outputs=[self.objective_invalid]);self.objective_force.zero_();self.objective_hessian.zero_();common=[self.objective_x,self.pairs,self.counts,self.objective_anchors,self.objective_sign,self.objective_weights,self.objective_stiffness,self.objective_law,self.objective_history,self.eligible]
  wp.launch(objective_force,dim=self.pairs.shape[0],inputs=common,outputs=[self.objective_force]);wp.launch(objective_gn,dim=(self.pairs.shape[0],16),inputs=common,outputs=[self.objective_hessian],block_dim=32);wp.launch(add_objective_blocks,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_force,self.objective_hessian],outputs=[self.particle_forces,self.particle_hessians]);wp.launch(relative_plane,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_x,self.board_stiffness,wp.float64(self.board_height)],outputs=[self.particle_forces,self.particle_hessians],block_dim=64)
  self.surface_contact.current_color=color
  try:self.surface_contact.evaluate(state.particle_q,dt)
  finally:self.surface_contact.current_color=-1
  self.surface_contact.scatter(color,self.model.particle_colors,self.particle_forces,self.particle_hessians)
 def commit_cohesion(self,state):
  from tomato_native_objective_reference import validate_frames,commit_objective_history
  if int(self.volume_invalid.numpy()[0]) or int(self.surface_contact.invalid.numpy()[0]):raise ValueError('Relative candidate volume/contact invalid; history not committed')
  wp.launch(reconstruct,dim=self.model.particle_count,inputs=[self.spatial_reference,state.particle_q],outputs=[self.objective_x],block_dim=64);wp.launch(validate_frames,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.objective_anchors],outputs=[self.objective_invalid])
  if int(self.objective_invalid.numpy()[0]):raise ValueError('Relative candidate material frame invalid')
  wp.launch(commit_objective_history,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.counts,self.objective_anchors,self.objective_sign,self.objective_weights,self.objective_stiffness,self.objective_law,self.eligible],outputs=[self.objective_history,self.history])

def build_relative_model(data,fixed_nodes=()):
 b=newton.ModelBuilder(gravity=(0.,0.,0.));fixed=set(fixed_nodes)
 for i,(p,m) in enumerate(zip(data['x'],data['mass'])):b.add_particle(wp.vec3(*p),wp.vec3(0.),0. if i in fixed else float(m),radius=0.)
 for (a,c),k in zip(data['springs'],data['k']):b.add_spring(int(a),int(c),float(k),0.,0.)
 b.color();b.set_coloring(data['colors']);model=b.finalize(device='cuda:0');model.particle_q.zero_();model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.;return model

def configure_relative(solver,data,*,board_stiffness=None,board_height=0.):
 configure_objective(solver,data,board_stiffness=board_stiffness,board_height=board_height);solver.spatial_reference=wp.array(data['x'],dtype=wp.vec3d);solver.relative_spring_rest=wp.array(np.linalg.norm(data['x'][data['springs'][:,1]]-data['x'][data['springs'][:,0]],axis=1),dtype=wp.float64);solver.relative_spring_k=wp.array(data['k'],dtype=wp.float64);return solver
