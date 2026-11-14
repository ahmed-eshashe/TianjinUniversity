"""Fresh physical-world float64 ledger for the explicit global solver candidate."""
from types import SimpleNamespace
from tomato_local_frame import translate_points
import numpy as np
import warp as wp
from tomato_support_ledger import SupportLedger
from tomato_double_blocks import double_bulk

from tomato_global_ledger import collect_world_external

class LocalFrameSupportLedger(SupportLedger):
 def __init__(self,solver,data,fixed,board_k,origin):
  holder=solver.holder;super().__init__(holder,data,fixed,board_k);self.global_solver=solver;n=len(data['x']);self.force=wp.zeros(n,dtype=wp.vec3d);self.hessian=wp.zeros(n,dtype=wp.mat33d);self.spring_rest=holder.relative_spring_rest.numpy();self.board_k=holder.board_stiffness.numpy().astype(float);self.zero=wp.zeros(n,dtype=wp.vec3);self.previous_velocity=wp.zeros(n,dtype=wp.vec3d);self.residual_sum=wp.zeros(1,dtype=wp.float64);self.step_residual=wp.zeros(1,dtype=wp.float64);self.maximum_node=wp.zeros(1,dtype=wp.float64);self.origin=wp.vec3d(*origin);self.world_x=wp.empty(n,dtype=wp.vec3d)
 def reset(self):
  super().reset();self.previous_velocity.zero_();self.residual_sum.zero_();self.step_residual.zero_();self.maximum_node.zero_()
 def step(self,state,dt):
  from tomato_native_objective_reference import objective_force
  s=self.solver;e=s.surface_contact;x=state.particle_q;e.reference=x;e.detect(self.zero);e.evaluate(self.zero,dt);wp.launch(double_bulk,dim=s.model.particle_count,inputs=[-1,s.model.particle_colors,x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[s.volume_invalid,self.force,self.hessian],block_dim=64);self.objective_force.zero_();wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.objective_force]);self.instant.zero_();self.step_residual.zero_();wp.launch(translate_points,dim=s.model.particle_count,inputs=[x,self.origin],outputs=[self.world_x],block_dim=64);wp.launch(collect_world_external,dim=s.model.particle_count,inputs=[self.world_x,state.particle_qd,self.previous_velocity,self.mass,self.fixed_mask,self.force,self.objective_force,e.physical_force,s.board_stiffness,wp.float64(dt)],outputs=[self.impulse,self.angular,self.instant,self.residual_sum,self.step_residual,self.maximum_node])
 def measurements(self,state):
  wp.launch(translate_points,dim=self.solver.model.particle_count,inputs=[state.particle_q,self.origin],outputs=[self.world_x],block_dim=64);result=super().measurements(SimpleNamespace(particle_q=self.world_x,particle_qd=state.particle_qd));result.update(cumulative_absolute_nodal_impulse_residual_ns=float(self.residual_sum.numpy()[0]),last_step_absolute_nodal_impulse_residual_ns=float(self.step_residual.numpy()[0]),maximum_single_node_step_residual_ns=float(self.maximum_node.numpy()[0]));return result
