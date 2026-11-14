"""Candidate full-model objective force/tangent integration, not yet qualified.

Original springs and volume potential are retained. Exact patch frame forces
and diagonal tangents are evaluated in float64 and cast to the VBD blocks.
Self-contact is deliberately refused until its zero-gap interface is resolved.
"""
import numpy as np
import warp as wp
from tomato_board_support import CheckedBoardSupportVBD
from tomato_objective_cohesion_reference import make_patch
from tomato_native_objective_reference import objective_force,force_seed,hessian_column,cast_positions,add_objective_blocks,validate_frames,commit_objective_history

class ObjectiveTomatoVBD(CheckedBoardSupportVBD):
 def _gather_blocks(self,color,state,dt):
  from tomato_objective_bulk_gather import gather_bulk
  from tomato_board_support import plane_blocks
  wp.launch(gather_bulk,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,state.particle_q,self.particle_q_prev,dt,self.spring_offsets,self.spring_ids,self.model.spring_indices,self.model.spring_rest_length,self.model.spring_stiffness,self.model.spring_damping,self.patch_offsets,self.patch_ids,self.pairs,self.rest,self.weights,self.counts,self.stiffness,self.law,self.history,self.eligible,self.invalid,self.cell_offsets,self.cell_ids,self.cells,self.volumes,self.volume_invalid],outputs=[self.particle_forces,self.particle_hessians],device=self.device)
  wp.launch(cast_positions,dim=self.model.particle_count,inputs=[state.particle_q],outputs=[self.objective_x],device=self.device)
  wp.launch(validate_frames,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.objective_anchors],outputs=[self.objective_invalid],device=self.device)
  self.objective_force.zero_()
  with wp.Tape() as tape:
   wp.launch(objective_force,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.counts,self.objective_anchors,self.objective_sign,self.objective_weights,self.objective_stiffness,self.objective_law,self.objective_history,self.eligible],outputs=[self.objective_force],device=self.device)
  for axis in range(3):
   tape.zero();self.objective_x.grad.zero_();self.objective_force.grad.zero_();wp.launch(force_seed,dim=self.model.particle_count,inputs=[self.model.particle_colors,color,axis],outputs=[self.objective_seed],device=self.device);tape.backward(grads={self.objective_force:self.objective_seed});wp.launch(hessian_column,dim=self.model.particle_count,inputs=[self.model.particle_colors,color,axis,tape.gradients[self.objective_x]],outputs=[self.objective_hessian],device=self.device)
  wp.launch(add_objective_blocks,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_force,self.objective_hessian],outputs=[self.particle_forces,self.particle_hessians],device=self.device)
  wp.launch(plane_blocks,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,state.particle_q,self.board_stiffness,self.board_height],outputs=[self.particle_forces,self.particle_hessians],device=self.device)

 def commit_cohesion(self,state):
  if int(self.volume_invalid.numpy()[0]):raise ValueError('Candidate objective step crossed unchanged volume floor')
  wp.launch(cast_positions,dim=self.model.particle_count,inputs=[state.particle_q],outputs=[self.objective_x],device=self.device)
  wp.launch(validate_frames,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.objective_anchors],outputs=[self.objective_invalid],device=self.device)
  if int(self.objective_invalid.numpy()[0]):raise ValueError('Degenerate objective frame; history not committed')
  wp.launch(commit_objective_history,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.counts,self.objective_anchors,self.objective_sign,self.objective_weights,self.objective_stiffness,self.objective_law,self.eligible],outputs=[self.objective_history,self.history],device=self.device)

 def reset_material(self):
  self.objective_history.zero_();self.history.zero_();self.eligible.zero_();self.objective_invalid.zero_();self.invalid.zero_();self.volume_invalid.zero_();self.volume_step_fraction.fill_(1.);self.volume_clip_count.zero_()


def configure_objective(solver,data,*,board_stiffness=None,board_height=0.):
 patches=data['cohesion'].patches;weights=np.zeros(solver.weights.shape);anchors=[];sign=[];stiffness=[];laws=[]
 for i,p in enumerate(patches):
  ids=data['pairs'][p['indices']];law=p['law'];model=make_patch(data['x'][ids],p['weights'],p['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m));anchors.append(model['anchors']);sign.append(model['sign']);stiffness.append(model['local_k']);laws.append([law.stiffness_n_m,law.onset_m,law.failure_m]);weights[i,:len(ids)]=p['weights']
 solver.objective_x=wp.empty(solver.model.particle_count,dtype=wp.vec3d,requires_grad=True);solver.objective_force=wp.zeros(solver.model.particle_count,dtype=wp.vec3d,requires_grad=True);solver.objective_seed=wp.empty(solver.model.particle_count,dtype=wp.vec3d);solver.objective_hessian=wp.zeros(solver.model.particle_count,dtype=wp.mat33d)
 solver.objective_anchors=wp.array(anchors,dtype=wp.vec3i);solver.objective_sign=wp.array(sign,dtype=wp.float64);solver.objective_weights=wp.array(weights,dtype=wp.float64);solver.objective_stiffness=wp.array(stiffness,dtype=wp.mat33d);solver.objective_law=wp.array(laws,dtype=wp.vec3d);solver.objective_history=wp.zeros(len(patches),dtype=wp.vec2d);solver.objective_invalid=wp.zeros(1,dtype=int)
 solver.volumes64=wp.array(data['volumes'],dtype=wp.float64);solver.candidate_active=wp.zeros(1,dtype=int);solver.candidate_bad=wp.zeros(1,dtype=int);solver.board_stiffness=wp.array(np.zeros(solver.model.particle_count) if board_stiffness is None else board_stiffness,dtype=float);solver.board_height=board_height
 return solver
