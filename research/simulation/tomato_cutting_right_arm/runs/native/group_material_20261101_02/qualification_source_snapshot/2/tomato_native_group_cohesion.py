"""Shared-budget, multi-quadrature fixed-frame cohesion for guarded native coupons.

All vertices in a patch must have distinct colors. Not an objective rotating
material frame or a volumetric tomato calibration.
"""
import warp as wp
from newton import State,Contacts
from newton._src.solvers.vbd.solver_vbd import (SolverVBD,SolverBase,accumulate_particle_body_contact_force_and_hessian,
 accumulate_spring_force_and_hessian,accumulate_self_contact_force_and_hessian,solve_elasticity_tile,solve_elasticity,TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE)

@wp.kernel
def group_blocks(color:int,colors:wp.array[int],x:wp.array[wp.vec3],pairs:wp.array2d[wp.vec2i],rest:wp.array2d[wp.vec3],weights:wp.array2d[float],counts:wp.array[int],
 nodes:wp.array2d[int],node_counts:wp.array[int],stiffness:wp.array[wp.mat33],law:wp.array[wp.vec3],history:wp.array[wp.vec2],eligible:wp.array[int],invalid:wp.array[int],forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 patch=wp.tid();k=stiffness[patch];u=float(0.)
 for j in range(counts[patch]):
  pair=pairs[patch,j];g=x[pair[1]]-x[pair[0]]-rest[patch,j];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);u+=.5*weights[patch,j]*wp.dot(e,k*e)
  if g[0]<-1.e-12 and wp.length(wp.vec2(g[1],g[2]))>1.e-12:wp.atomic_add(invalid,0,1)
 q=wp.sqrt(wp.max(2.*u/law[patch][0],0.));a=law[patch][1];b=law[patch][2];old=history[patch];d=old[1];derivative=float(0.)
 if eligible[patch]!=0 and q>=old[0]:
  if q>=b:d=1.
  elif q>a:
   candidate=b*(q-a)/(q*(b-a))
   if candidate>=d:d=candidate;derivative=b*a/((b-a)*q*q)
 for n in range(node_counts[patch]):
  node=nodes[patch,n]
  if colors[node]==color:
   gradient=wp.vec3(0.);h=wp.mat33(0.)
   for j in range(counts[patch]):
    pair=pairs[patch,j];sign=float(0.)
    if node==pair[0]:sign=-1.
    if node==pair[1]:sign=1.
    if sign!=0.:
     g=x[pair[1]]-x[pair[0]]-rest[patch,j];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);gradient+=sign*weights[patch,j]*(k*e)
     block=k
     if g[0]<0.:block[0,0]=0.
     h+=weights[patch,j]*block
   h=(1.-d)*h
   if derivative>0.:h-=derivative/(law[patch][0]*q)*wp.outer(gradient,gradient)
   wp.atomic_add(forces,node,-(1.-d)*gradient);wp.atomic_add(hessians,node,h)

@wp.kernel
def commit_group_history(x:wp.array[wp.vec3],pairs:wp.array2d[wp.vec2i],rest:wp.array2d[wp.vec3],weights:wp.array2d[float],counts:wp.array[int],stiffness:wp.array[wp.mat33],law:wp.array[wp.vec3],eligible:wp.array[int],history:wp.array[wp.vec2]):
 p=wp.tid()
 if eligible[p]!=0:
  u=float(0.)
  for j in range(counts[p]):
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]]-rest[p,j];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);u+=.5*weights[p,j]*wp.dot(e,stiffness[p]*e)
  q=wp.sqrt(wp.max(2.*u/law[p][0],0.));a=law[p][1];b=law[p][2];old=history[p];maximum=wp.max(q,old[0]);d=old[1]
  if maximum>=b:d=1.
  elif maximum>a:d=wp.max(d,b*(maximum-a)/(maximum*(b-a)))
  history[p]=wp.vec2(maximum,d)

class GroupCohesiveVBD(SolverVBD):
 def configure(self,pairs,rest,weights,counts,nodes,node_counts,stiffness,law,history,eligible):
  self.pairs=pairs;self.rest=rest;self.weights=weights;self.counts=counts;self.nodes=nodes;self.node_counts=node_counts;self.stiffness=stiffness;self.law=law;self.history=history;self.eligible=eligible
  self.invalid=wp.zeros(1,dtype=int,device=self.device)
  colors=self.model.particle_colors.numpy().tolist()
  for ids,n in zip(nodes.numpy().tolist(),node_counts.numpy().tolist()):
   if len({colors[i] for i in ids[:n]})!=n:raise ValueError('Patch clique coloring required')
  for w,n in zip(weights.numpy().tolist(),counts.numpy().tolist()):
   if any(v<=0 for v in w[:n]) or abs(sum(w[:n])-1.)>1.e-6:raise ValueError('Normalized positive patch quadrature required')

 def commit_cohesion(self,state):
  if int(self.invalid.numpy()[0]):raise ValueError('Unsupported compression/shear trial; shared history not committed')
  wp.launch(commit_group_history,dim=self.pairs.shape[0],inputs=[state.particle_q,self.pairs,self.rest,self.weights,self.counts,self.stiffness,self.law,self.eligible,self.history],device=self.device)

 def _solve_particle_iteration(
     self, state_in: State, state_out: State, contacts: Contacts | None, dt: float, iter_num: int
 ):
     """Solve one VBD iteration for particles."""
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
         wp.launch(group_blocks,dim=self.pairs.shape[0],inputs=[color,model.particle_colors,state_in.particle_q,self.pairs,self.rest,self.weights,self.counts,self.nodes,self.node_counts,self.stiffness,self.law,self.history,self.eligible,self.invalid],outputs=[self.particle_forces,self.particle_hessians],device=self.device)
         if contacts is not None:
             wp.launch(
                 kernel=accumulate_particle_body_contact_force_and_hessian,
                 dim=contacts.soft_contact_max,
                 inputs=[
                     dt,
                     color,
                     self.particle_q_prev,
                     state_in.particle_q,
                     model.particle_colors,
                     # body-particle contact
                     self.friction_epsilon,
                     model.particle_radius,
                     contacts.soft_contact_indices,
                     contacts.soft_contact_count,
                     contacts.soft_contact_max,
                     self.body_particle_contact_penalty_k,
                     self.body_particle_contact_material_ke,
                     self.body_particle_contact_material_kd,
                     self.body_particle_contact_material_mu,
                     model.shape_body,
                     body_q_for_particles,
                     body_q_prev_for_particles,
                     body_qd_for_particles,
                     model.body_com,
                     contacts.soft_contact_shape,
                     contacts.soft_contact_body_pos,
                     contacts.soft_contact_body_vel,
                     contacts.soft_contact_normal,
                     model.shape_margin,
                     contacts.soft_contact_barycentric,
                 ],
                 outputs=[
                     self.particle_forces,
                     self.particle_hessians,
                 ],
                 device=self.device,
             )

         if model.spring_count:
             wp.launch(
                 kernel=accumulate_spring_force_and_hessian,
                 inputs=[
                     dt,
                     color,
                     self.particle_q_prev,
                     state_in.particle_q,
                     self.model.particle_colors,
                     model.spring_count,
                     self.model.spring_indices,
                     self.model.spring_rest_length,
                     self.model.spring_stiffness,
                     self.model.spring_damping,
                 ],
                 outputs=[self.particle_forces, self.particle_hessians],
                 dim=model.spring_count,
                 device=self.device,
             )

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
         self._penetration_free_truncation(state_in.particle_q)

     wp.copy(state_out.particle_q, state_in.particle_q)
