"""Support ledger in physical coordinates for rest-relative mechanical storage."""
import warp as wp
from types import SimpleNamespace
from tomato_support_ledger import SupportLedger
from tomato_relative_kernels import reconstruct,relative_bulk

@wp.kernel(enable_backward=False)
def collect_relative_external(x:wp.array[wp.vec3d],mass:wp.array[wp.float64],fixed:wp.array[int],bulk:wp.array[wp.vec3],cohesion:wp.array[wp.vec3d],closure:wp.array[wp.vec3d],board_k:wp.array[float],dt:wp.float64,impulse:wp.array[wp.vec3d],angular:wp.array[wp.vec3d],instant:wp.array[wp.vec3d]):
 i=wp.tid();p=x[i];g=wp.vec3d(wp.float64(0.),wp.float64(0.),-mass[i]*wp.float64(9.81));board=wp.vec3d(wp.float64(0.),wp.float64(0.),wp.float64(board_k[i])*wp.max(-p[2],wp.float64(0.)));reaction=wp.vec3d(0.)
 if fixed[i]!=0:
  f=bulk[i];reaction=-wp.vec3d(wp.float64(f[0]),wp.float64(f[1]),wp.float64(f[2]))-cohesion[i]-closure[i]-board-g
 wp.atomic_add(instant,0,g);wp.atomic_add(instant,1,board);wp.atomic_add(instant,2,reaction);wp.atomic_add(impulse,0,dt*g);wp.atomic_add(impulse,1,dt*board);wp.atomic_add(impulse,2,dt*reaction);wp.atomic_add(angular,0,dt*wp.cross(p,g));wp.atomic_add(angular,1,dt*wp.cross(p,board));wp.atomic_add(angular,2,dt*wp.cross(p,reaction))

class RelativeSupportLedger(SupportLedger):
 def __init__(self,solver,data,fixed,board_k):
  super().__init__(solver,data,fixed,board_k);self.spring_rest=solver.relative_spring_rest.numpy();self.board_k=solver.board_stiffness.numpy().astype(float)
 def step(self,state,dt):
  from tomato_native_objective_reference import objective_force
  s=self.solver;wp.launch(reconstruct,dim=s.model.particle_count,inputs=[s.spatial_reference,state.particle_q],outputs=[self.objective_x],block_dim=64);wp.launch(relative_bulk,dim=s.model.particle_count,inputs=[-1,s.model.particle_colors,self.objective_x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[s.volume_invalid,self.force,self.hessian],block_dim=64);self.objective_force.zero_();wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[self.objective_x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.objective_force]);s.surface_contact.evaluate(state.particle_q,dt);self.instant.zero_();wp.launch(collect_relative_external,dim=s.model.particle_count,inputs=[self.objective_x,self.mass,self.fixed_mask,self.force,self.objective_force,s.surface_contact.physical_force,s.board_stiffness,wp.float64(dt)],outputs=[self.impulse,self.angular,self.instant])
 def measurements(self,state):
  wp.launch(reconstruct,dim=self.solver.model.particle_count,inputs=[self.solver.spatial_reference,state.particle_q],outputs=[self.objective_x],block_dim=64);return super().measurements(SimpleNamespace(particle_q=self.objective_x,particle_qd=state.particle_qd))
