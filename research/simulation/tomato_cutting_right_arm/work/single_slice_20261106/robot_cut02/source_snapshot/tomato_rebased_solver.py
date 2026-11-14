"""Versioned precision candidate; unchanged force laws, float64 block solve.

Local coordinates are rebased before every color to retain tiny increments.
Canonical step origins/inertial targets are float64. This is not qualified by
construction; native-body Contacts are explicitly refused. No physical clocks,
material values, fracture energies, fixtures or contact margins are retuned.
"""
import warp as wp
from tomato_relative_full_model import RelativeObjectiveVBD
from tomato_relative_contact import RelativeSurfaceContact
from tomato_relative_kernels import reconstruct
from tomato_double_blocks import double_bulk
from tomato_cohesive_color_blocks import cohesive_color_blocks

@wp.kernel(enable_backward=False)
def rebase(reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],step_origin:wp.array[wp.vec3d],inertial_world:wp.array[wp.vec3d],query_world:wp.array[wp.vec3d],previous:wp.array[wp.vec3],inertia:wp.array[wp.vec3],baseline:wp.array[wp.vec3],displacement:wp.array[wp.vec3],query_local:wp.array[wp.vec3]):
 i=wp.tid();a=u[i];r=reference[i]+wp.vec3d(wp.float64(a[0]),wp.float64(a[1]),wp.float64(a[2]));reference[i]=r;u[i]=wp.vec3(0.);p=step_origin[i]-r;t=inertial_world[i]-r;q=query_world[i]-r;previous[i]=wp.vec3(float(p[0]),float(p[1]),float(p[2]));inertia[i]=wp.vec3(float(t[0]),float(t[1]),float(t[2]));baseline[i]=wp.vec3(0.);displacement[i]=wp.vec3(0.);query_local[i]=wp.vec3(float(q[0]),float(q[1]),float(q[2]))

@wp.kernel(enable_backward=False)
def solve_double(color:int,colors:wp.array[int],mass:wp.array[float],x:wp.array[wp.vec3d],inertial_world:wp.array[wp.vec3d],dt:wp.float64,bulk_force:wp.array[wp.vec3d],bulk_hessian:wp.array[wp.mat33d],cohesive_force:wp.array[wp.vec3d],cohesive_hessian:wp.array[wp.mat33d],contact_force:wp.array[wp.vec3d],contact_hessian:wp.array[wp.mat33d],board_k:wp.array[float],board_height:wp.float64,delta:wp.array[wp.vec3],fallback_count:wp.array[int],invalid:wp.array[int]):
 i=wp.tid()
 if colors[i]==color:
  delta[i]=wp.vec3(0.)
  if mass[i]>0.:
   inertial_k=wp.float64(mass[i])/(dt*dt);force=inertial_k*(inertial_world[i]-x[i])+bulk_force[i]+cohesive_force[i]+contact_force[i];h=inertial_k*wp.identity(n=3,dtype=wp.float64)+bulk_hessian[i]+cohesive_hessian[i]+contact_hessian[i]
   if x[i][2]<board_height:
    force[2]+=wp.float64(board_k[i])*(board_height-x[i][2]);h[2,2]+=wp.float64(board_k[i])
   scale=inertial_k
   for row in range(3):
    for col in range(3):scale=wp.max(scale,wp.abs(h[row,col]))
   normalized=h/scale;det=wp.determinant(normalized);direction=force/scale;fallback=bool(True)
   if wp.abs(det)>wp.float64(1.e-280) and wp.isfinite(det):
    trial=wp.inverse(normalized)*(force/scale)
    if wp.dot(trial,force)>wp.float64(0.) and wp.isfinite(trial[0]) and wp.isfinite(trial[1]) and wp.isfinite(trial[2]):direction=trial;fallback=False
   if fallback:wp.atomic_add(fallback_count,0,1)
   if not wp.isfinite(direction[0]) or not wp.isfinite(direction[1]) or not wp.isfinite(direction[2]):wp.atomic_add(invalid,0,1)
   else:delta[i]=wp.vec3(float(direction[0]),float(direction[1]),float(direction[2]))

@wp.kernel(enable_backward=False)
def double_velocity(reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],previous_world:wp.array[wp.vec3d],dt:wp.float64,velocity:wp.array[wp.vec3]):
 i=wp.tid();a=u[i];world=reference[i]+wp.vec3d(wp.float64(a[0]),wp.float64(a[1]),wp.float64(a[2]));v=(world-previous_world[i])/dt;velocity[i]=wp.vec3(float(v[0]),float(v[1]),float(v[2]))

class RebasedSurfaceContact(RelativeSurfaceContact):
 def __init__(self,data,reference,**kwargs):
  super().__init__(data,reference,**kwargs);self.query_world=wp.empty(len(data['x']),dtype=wp.vec3d)
 def detect(self,u):
  super().detect(u);wp.launch(reconstruct,dim=self.node_count,inputs=[self.reference,u],outputs=[self.query_world],block_dim=64)

class RebasedRelativeVBD(RelativeObjectiveVBD):
 def step(self,state_in,state_out,control,contacts,dt):
  if contacts is not None or self.model.body_count:raise ValueError('Rebased physical-coordinate solver does not accept native rigid-body Contacts')
  super().step(state_in,state_out,control,contacts,dt)
 def _initialize_particles(self,state_in,state_out,dt):
  wp.launch(reconstruct,dim=self.model.particle_count,inputs=[self.spatial_reference,state_in.particle_q],outputs=[self.step_origin_world],block_dim=64);super()._initialize_particles(state_in,state_out,dt);wp.launch(reconstruct,dim=self.model.particle_count,inputs=[self.spatial_reference,self.inertia],outputs=[self.inertial_world],block_dim=64)
 def _solve_particle_iteration(self,state_in,state_out,contacts,dt,iter_num):
  self.surface_contact.detect(state_in.particle_q)
  for color in range(len(self.model.particle_color_groups)):
   wp.launch(rebase,dim=self.model.particle_count,inputs=[self.spatial_reference,state_in.particle_q,self.step_origin_world,self.inertial_world,self.surface_contact.query_world],outputs=[self.particle_q_prev,self.inertia,self.pos_prev_collision_detection,self.particle_displacements,self.surface_contact.query_physical],block_dim=64)
   wp.launch(reconstruct,dim=self.model.particle_count,inputs=[self.spatial_reference,state_in.particle_q],outputs=[self.objective_x],block_dim=64)
   wp.launch(double_bulk,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.objective_x,self.spring_offsets,self.spring_ids,self.model.spring_indices,self.relative_spring_rest,self.relative_spring_k,self.cell_offsets,self.cell_ids,self.cells,self.volumes64],outputs=[self.volume_invalid,self.double_bulk_force,self.double_bulk_hessian],block_dim=64)
   from tomato_native_objective_reference import validate_frames
   wp.launch(validate_frames,dim=self.pairs.shape[0],inputs=[self.objective_x,self.pairs,self.objective_anchors],outputs=[self.objective_invalid]);self.objective_force.zero_();self.objective_hessian.zero_();wp.launch(cohesive_color_blocks,dim=(self.pairs.shape[0],16),inputs=[color,self.model.particle_colors,self.objective_x,self.pairs,self.counts,self.objective_anchors,self.objective_sign,self.objective_weights,self.objective_stiffness,self.objective_law,self.objective_history,self.eligible],outputs=[self.objective_force,self.objective_hessian],block_dim=32)
   self.surface_contact.current_color=color
   try:self.surface_contact.evaluate(state_in.particle_q,dt)
   finally:self.surface_contact.current_color=-1
   wp.launch(solve_double,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,self.model.particle_mass,self.objective_x,self.inertial_world,wp.float64(dt),self.double_bulk_force,self.double_bulk_hessian,self.objective_force,self.objective_hessian,self.surface_contact.physical_force,self.surface_contact.physical_hessian,self.board_stiffness,wp.float64(self.board_height)],outputs=[self.particle_displacements,self.double_fallback_count,self.volume_invalid],block_dim=64);self._volume_safe_update(color,state_in.particle_q)
  wp.copy(state_out.particle_q,state_in.particle_q)
 def _finalize_particles(self,state_out,dt):
  wp.launch(double_velocity,dim=self.model.particle_count,inputs=[self.spatial_reference,state_out.particle_q,self.step_origin_world,wp.float64(dt)],outputs=[state_out.particle_qd],block_dim=64)

def configure_rebased(solver):
 n=solver.model.particle_count;solver.step_origin_world=wp.empty(n,dtype=wp.vec3d);solver.inertial_world=wp.empty(n,dtype=wp.vec3d);solver.double_bulk_force=wp.zeros(n,dtype=wp.vec3d);solver.double_bulk_hessian=wp.zeros(n,dtype=wp.mat33d);solver.double_fallback_count=wp.zeros(1,dtype=int);return solver
