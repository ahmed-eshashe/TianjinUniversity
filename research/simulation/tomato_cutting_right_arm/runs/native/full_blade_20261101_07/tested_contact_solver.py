"""Two-stage, stable contact reduction for the full tomato diagnostic solver.

The installed edge/face contact force law is reused. Parallel contact evaluation
is followed by node-owned reduction in a fixed registry order.
"""
import warp as wp
from newton._src.solvers.vbd.rigid_vbd_kernels import _eval_soft_ef_contact
from tomato_native_full_model import FullTomatoVBD
from tomato_native_full_gather import adjacency
from tomato_mesh_weighted_contact import set_penalty
from newton import State,Contacts
from newton._src.solvers.vbd.solver_vbd import SolverBase,accumulate_self_contact_force_and_hessian,solve_elasticity_tile,solve_elasticity,TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE

@wp.kernel
def evaluate_contacts(x:wp.array[wp.vec3],previous:wp.array[wp.vec3],radius:wp.array[float],corners:wp.array[wp.vec3i],bary:wp.array[wp.vec3],k:wp.array[float],kd:wp.array[float],mu:wp.array[float],eps:float,shape_body:wp.array[int],body_q:wp.array[wp.transform],body_prev:wp.array[wp.transform],body_qd:wp.array[wp.spatial_vector],body_com:wp.array[wp.vec3],shape:wp.array[int],point:wp.array[wp.vec3],velocity:wp.array[wp.vec3],normal:wp.array[wp.vec3],margin:wp.array[float],dt:float,forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 i=wp.tid();f,h,p=_eval_soft_ef_contact(i,corners[i],bary[i],x,previous,radius,k[i],kd[i],mu[i],eps,shape_body,body_q,body_prev,body_qd,body_com,shape,point,velocity,normal,margin,dt);forces[i]=f;hessians[i]=h

@wp.kernel
def reduce_contacts(color:int,colors:wp.array[int],offsets:wp.array[int],rows:wp.array[int],corners:wp.array[wp.vec3i],bary:wp.array[wp.vec3],contact_force:wp.array[wp.vec3],contact_hessian:wp.array[wp.mat33],forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 node=wp.tid()
 if colors[node]==color:
  f=forces[node];h=hessians[node]
  for j in range(offsets[node],offsets[node+1]):
   i=rows[j];w=float(0.)
   for c in range(3):
    if corners[i][c]==node:w=bary[i][c]
   f+=w*contact_force[i];h+=(w*w)*contact_hessian[i]
  forces[node]=f;hessians[node]=h

class FullBladeVBD(FullTomatoVBD):
 def prepare_contacts(self,payload):
  count=payload['soft_contact_count'][0];ids=payload['arrays']['soft_contact_indices']
  if len(ids)!=count or any(len(set(row))!=3 or min(row)<0 for row in ids):raise ValueError('Current deterministic blade stream requires three distinct valid face corners')
  self.contact_offsets,self.contact_rows=adjacency(ids,self.model.particle_count);self.contact_forces=wp.empty(count,dtype=wp.vec3);self.contact_hessians=wp.empty(count,dtype=wp.mat33)
 def _contact_gather(self,color,state_in,state_out,contacts,dt):
  count=self.contact_forces.size
  if not count:return
  model=self.model
  wp.launch(evaluate_contacts,dim=count,inputs=[state_in.particle_q,self.particle_q_prev,model.particle_radius,contacts.soft_contact_indices,contacts.soft_contact_barycentric,self.body_particle_contact_penalty_k,self.body_particle_contact_material_kd,self.body_particle_contact_material_mu,self.friction_epsilon,model.shape_body,state_out.body_q,state_in.body_q,state_out.body_qd,model.body_com,contacts.soft_contact_shape,contacts.soft_contact_body_pos,contacts.soft_contact_body_vel,contacts.soft_contact_normal,model.shape_margin,dt],outputs=[self.contact_forces,self.contact_hessians],device=self.device)
  wp.launch(reduce_contacts,dim=model.particle_count,inputs=[color,model.particle_colors,self.contact_offsets,self.contact_rows,contacts.soft_contact_indices,contacts.soft_contact_barycentric,self.contact_forces,self.contact_hessians],outputs=[self.particle_forces,self.particle_hessians],device=self.device)

 def _solve_particle_iteration(
     self, state_in: State, state_out: State, contacts: Contacts | None, dt: float, iter_num: int
 ):
     """Solve one VBD iteration for particles."""
     if iter_num==0 and contacts is not None and self.contact_weights.size:
         wp.launch(set_penalty,dim=self.contact_weights.size,inputs=[self.contact_weights],outputs=[self.body_particle_contact_penalty_k,self.body_particle_contact_material_ke],device=self.device)
     model = self.model

     # Select rigid-body poses for particle-rigid contact evaluation
     if self.integrate_with_external_rigid_solver:
         body_q_for_particles = state_out.body_q
         body_q_prev_for_particles = state_in.body_q
         body_qd_for_particles = state_out.body_qd
     else:
         body_q_for_particles = state_in.body_q
         if model.body_count > 0:
             body_q_prev_for_particles = self.body_q_prev
         else:
             body_q_prev_for_particles = None
         body_qd_for_particles = state_in.body_qd

     # Early exit if no particles
     if model.particle_count == 0:
         return

     # Update collision detection if needed (penetration-free mode only)
     if self.particle_enable_self_contact:
         _Frequency = SolverBase.CollisionFrequencyType
         if (self._sc_mode_this_step == _Frequency.PRE_POST_INIT and iter_num == 0) or (
             self._sc_mode_this_step == _Frequency.ITERATIONS and (iter_num + 1) % self._sc_freq_this_step == 0
         ):
             self._collision_detection_penetration_free(state_in)

     # Zero out forces and hessians
     self.particle_forces.zero_()
     self.particle_hessians.zero_()

     # Iterate over color groups
     for color in range(len(self.model.particle_color_groups)):
         self._gather_blocks(color,state_in,dt)
         if contacts is not None:
             self._contact_gather(color,state_in,state_out,contacts,dt)

         if self.particle_enable_self_contact:
             wp.launch(
                 kernel=accumulate_self_contact_force_and_hessian,
                 dim=self.particle_self_contact_evaluation_kernel_launch_size,
                 inputs=[
                     dt,
                     color,
                     self.particle_q_prev,
                     state_in.particle_q,
                     self.model.particle_colors,
                     self.model.tri_indices,
                     self.model.edge_indices,
                     # self-contact
                     self.trimesh_collision_info,
                     self.particle_self_contact_margin,
                     self.model.soft_contact_ke,
                     self.model.soft_contact_kd,
                     self.model.soft_contact_mu,
                     self.friction_epsilon,
                     self._self_contact_edge_edge_parallel_epsilon,
                 ],
                 outputs=[self.particle_forces, self.particle_hessians],
                 device=self.device,
                 max_blocks=self.model.device.sm_count,
             )
         if self.use_particle_tile_solve:
             wp.launch(
                 kernel=solve_elasticity_tile,
                 dim=self.model.particle_color_groups[color].size * TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE,
                 block_dim=TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE,
                 inputs=[
                     dt,
                     self.model.particle_color_groups[color],
                     self.particle_q_prev,
                     state_in.particle_q,
                     self.model.particle_mass,
                     self.inertia,
                     self.model.particle_flags,
                     self.model.tri_indices,
                     self.model.tri_poses,
                     self.model.tri_materials,
                     self.model.tri_areas,
                     self.model.edge_indices,
                     self.model.edge_rest_angle,
                     self.model.edge_rest_length,
                     self.model.edge_bending_properties,
                     self.model.tet_indices,
                     self.model.tet_poses,
                     self.model.tet_materials,
                     self.particle_adjacency,
                     self.particle_forces,
                     self.particle_hessians,
                 ],
                 outputs=[
                     self.particle_displacements,
                 ],
                 device=self.device,
             )
         else:
             wp.launch(
                 kernel=solve_elasticity,
                 dim=self.model.particle_color_groups[color].size,
                 inputs=[
                     dt,
                     self.model.particle_color_groups[color],
                     self.particle_q_prev,
                     state_in.particle_q,
                     self.model.particle_mass,
                     self.inertia,
                     self.model.particle_flags,
                     self.model.tri_indices,
                     self.model.tri_poses,
                     self.model.tri_materials,
                     self.model.tri_areas,
                     self.model.edge_indices,
                     self.model.edge_rest_angle,
                     self.model.edge_rest_length,
                     self.model.edge_bending_properties,
                     self.model.tet_indices,
                     self.model.tet_poses,
                     self.model.tet_materials,
                     self.particle_adjacency,
                     self.particle_forces,
                     self.particle_hessians,
                 ],
                 outputs=[
                     self.particle_displacements,
                 ],
                 device=self.device,
             )
         self._volume_safe_update(color,state_in.particle_q)

     wp.copy(state_out.particle_q, state_in.particle_q)
