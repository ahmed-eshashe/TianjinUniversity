"""Fresh physical-world float64 ledger for the explicit global solver candidate."""
import numpy as np
import warp as wp
from tomato_support_ledger import SupportLedger
from tomato_double_blocks import double_bulk

@wp.kernel(enable_backward=False)
def collect_world_external(x:wp.array[wp.vec3d],velocity:wp.array[wp.vec3d],previous_velocity:wp.array[wp.vec3d],mass:wp.array[wp.float64],fixed:wp.array[int],bulk:wp.array[wp.vec3d],cohesion:wp.array[wp.vec3d],closure:wp.array[wp.vec3d],board_k:wp.array[float],dt:wp.float64,impulse:wp.array[wp.vec3d],angular:wp.array[wp.vec3d],instant:wp.array[wp.vec3d],residual_sum:wp.array[wp.float64],step_residual:wp.array[wp.float64],maximum_node:wp.array[wp.float64]):
 i=wp.tid();p=x[i];current=velocity[i];g=wp.vec3d(wp.float64(0.),wp.float64(0.),-mass[i]*wp.float64(9.81));board=wp.vec3d(wp.float64(0.),wp.float64(0.),wp.float64(board_k[i])*wp.max(-p[2],wp.float64(0.)));force=bulk[i]+cohesion[i]+closure[i]+board+g;reaction=wp.vec3d(0.)
 if fixed[i]!=0:reaction=-force
 else:
  residual=mass[i]*(current-previous_velocity[i])-dt*force;size=wp.length(residual);wp.atomic_add(residual_sum,0,size);wp.atomic_add(step_residual,0,size);wp.atomic_max(maximum_node,0,size)
 previous_velocity[i]=current;wp.atomic_add(instant,0,g);wp.atomic_add(instant,1,board);wp.atomic_add(instant,2,reaction);wp.atomic_add(impulse,0,dt*g);wp.atomic_add(impulse,1,dt*board);wp.atomic_add(impulse,2,dt*reaction);wp.atomic_add(angular,0,dt*wp.cross(p,g));wp.atomic_add(angular,1,dt*wp.cross(p,board));wp.atomic_add(angular,2,dt*wp.cross(p,reaction))

class GlobalSupportLedger(SupportLedger):
 def __init__(self,solver,data,fixed,board_k):
  holder=solver.holder;super().__init__(holder,data,fixed,board_k);self.global_solver=solver;n=len(data['x']);self.force=wp.zeros(n,dtype=wp.vec3d);self.hessian=wp.zeros(n,dtype=wp.mat33d);self.spring_rest=holder.relative_spring_rest.numpy();self.board_k=holder.board_stiffness.numpy().astype(float);self.zero=wp.zeros(n,dtype=wp.vec3);self.previous_velocity=wp.zeros(n,dtype=wp.vec3d);self.residual_sum=wp.zeros(1,dtype=wp.float64);self.step_residual=wp.zeros(1,dtype=wp.float64);self.maximum_node=wp.zeros(1,dtype=wp.float64)
 def reset(self):
  super().reset();self.previous_velocity.zero_();self.residual_sum.zero_();self.step_residual.zero_();self.maximum_node.zero_()
 def step(self,state,dt):
  from tomato_native_objective_reference import objective_force
  s=self.solver;e=s.surface_contact;x=state.particle_q;e.reference=x;e.detect(self.zero);e.evaluate(self.zero,dt);wp.launch(double_bulk,dim=s.model.particle_count,inputs=[-1,s.model.particle_colors,x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[s.volume_invalid,self.force,self.hessian],block_dim=64);self.objective_force.zero_();wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.objective_force]);self.instant.zero_();self.step_residual.zero_();wp.launch(collect_world_external,dim=s.model.particle_count,inputs=[x,state.particle_qd,self.previous_velocity,self.mass,self.fixed_mask,self.force,self.objective_force,e.physical_force,s.board_stiffness,wp.float64(dt)],outputs=[self.impulse,self.angular,self.instant,self.residual_sum,self.step_residual,self.maximum_node])
 def measurements(self,state):
  result=super().measurements(state);result.update(cumulative_absolute_nodal_impulse_residual_ns=float(self.residual_sum.numpy()[0]),last_step_absolute_nodal_impulse_residual_ns=float(self.step_residual.numpy()[0]),maximum_single_node_step_residual_ns=float(self.maximum_node.numpy()[0]));return result
