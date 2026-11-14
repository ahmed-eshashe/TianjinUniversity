"""Conservative held nodal loads for synthetic support challenges only.

These are disclosed external forces, not knife contact or measured tomato
loads. Each interval holds its force field fixed in both mechanical force and
potential. Fresh physical ledgers include the actual external impulse, moment
and exact held-force displacement work. Original material, contact and reset
criteria are retained; live damage remains refused by the parent.
"""
import numpy as np
import warp as wp
from tomato_failed_safe_global import FailedSafeFractionCandidate
from tomato_failed_safe_ledger import FailedSafeLocalLedger
from tomato_double_blocks import double_bulk
from tomato_failed_safe_objective import objective_force
from tomato_local_frame import translate_points

@wp.kernel(enable_backward=False)
def load_rhs(extra:wp.array[wp.vec3d],free:wp.array[int],mass:wp.array[wp.float64],rhs:wp.array[wp.vec3d],norm_sum:wp.array[wp.float64],maximum:wp.array[wp.float64]):
 i=wp.tid()
 if free[i]!=0:rhs[i]+=extra[i];wp.atomic_add(norm_sum,0,wp.length(rhs[i]));wp.atomic_max(maximum,0,wp.length(rhs[i])/mass[i])

@wp.kernel(enable_backward=False)
def load_potential(x:wp.array[wp.vec3d],reference:wp.array[wp.vec3d],extra:wp.array[wp.vec3d],energy:wp.array[wp.float64]):
 i=wp.tid();wp.atomic_add(energy,0,-wp.dot(extra[i],x[i]-reference[i]))

@wp.kernel(enable_backward=False)
def collect_loaded_external(x:wp.array[wp.vec3d],velocity:wp.array[wp.vec3d],previous_velocity:wp.array[wp.vec3d],previous_position:wp.array[wp.vec3d],mass:wp.array[wp.float64],fixed:wp.array[int],bulk:wp.array[wp.vec3d],cohesion:wp.array[wp.vec3d],closure:wp.array[wp.vec3d],extra:wp.array[wp.vec3d],board_k:wp.array[float],dt:wp.float64,impulse:wp.array[wp.vec3d],angular:wp.array[wp.vec3d],instant:wp.array[wp.vec3d],residual_sum:wp.array[wp.float64],step_residual:wp.array[wp.float64],maximum_node:wp.array[wp.float64],load_work:wp.array[wp.float64]):
 i=wp.tid();p=x[i];current=velocity[i];g=wp.vec3d(wp.float64(0.),wp.float64(0.),-mass[i]*wp.float64(9.81));board=wp.vec3d(wp.float64(0.),wp.float64(0.),wp.float64(board_k[i])*wp.max(-p[2],wp.float64(0.)));force=bulk[i]+cohesion[i]+closure[i]+board+g+extra[i];reaction=wp.vec3d(0.)
 if fixed[i]!=0:reaction=-force
 else:
  residual=mass[i]*(current-previous_velocity[i])-dt*force;size=wp.length(residual);wp.atomic_add(residual_sum,0,size);wp.atomic_add(step_residual,0,size);wp.atomic_max(maximum_node,0,size)
 previous_velocity[i]=current;wp.atomic_add(load_work,0,wp.dot(extra[i],p-previous_position[i]));previous_position[i]=p
 wp.atomic_add(instant,0,g);wp.atomic_add(instant,1,board);wp.atomic_add(instant,2,reaction);wp.atomic_add(instant,3,extra[i]);wp.atomic_add(impulse,0,dt*g);wp.atomic_add(impulse,1,dt*board);wp.atomic_add(impulse,2,dt*reaction);wp.atomic_add(impulse,3,dt*extra[i]);wp.atomic_add(angular,0,dt*wp.cross(p,g));wp.atomic_add(angular,1,dt*wp.cross(p,board));wp.atomic_add(angular,2,dt*wp.cross(p,reaction));wp.atomic_add(angular,3,dt*wp.cross(p,extra[i]))

class ExternalLoadCandidate(FailedSafeFractionCandidate):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.external_force=wp.zeros(self.n,dtype=wp.vec3d);self.load_reference=wp.array(self.data['x'],dtype=wp.vec3d);self.load_energy=wp.zeros(1,dtype=wp.float64)
 def set_load(self,field):
  f=np.asarray(field,dtype=float)
  if f.shape!=(self.n,3)or not np.isfinite(f).all()or np.any(f[self.assembly.free.numpy()==0]):raise ValueError('Finite force field on free nodes only required')
  self.external_force.assign(f)
 def reset(self,state):super().reset(state);self.external_force.zero_()
 def force(self,x,dt):
  super().force(x,dt);self.norm_sum.zero_();self.maximum_acceleration_defect.zero_();wp.launch(load_rhs,dim=self.n,inputs=[self.external_force,self.assembly.free,self.assembly.mass],outputs=[self.rhs,self.norm_sum,self.maximum_acceleration_defect],block_dim=64);return float(self.norm_sum.numpy()[0])
 def energy(self,x,dt,*,trial=False):
  original=super().energy(x,dt,trial=trial);self.load_energy.zero_();wp.launch(load_potential,dim=self.n,inputs=[x,self.load_reference,self.external_force],outputs=[self.load_energy],block_dim=64);return original+float(self.load_energy.numpy()[0])

class ExternalLoadLedger(FailedSafeLocalLedger):
 def __init__(self,solver,*args,**kwargs):
  super().__init__(solver,*args,**kwargs);self.impulse=wp.zeros(4,dtype=wp.vec3d);self.angular=wp.zeros(4,dtype=wp.vec3d);self.instant=wp.zeros(4,dtype=wp.vec3d);self.previous_position=wp.zeros(solver.n,dtype=wp.vec3d);self.load_work=wp.zeros(1,dtype=wp.float64)
 def reset(self,state):
  super().reset();self.load_work.zero_();wp.launch(translate_points,dim=self.global_solver.n,inputs=[state.particle_q,self.origin],outputs=[self.previous_position],block_dim=64)
 def step(self,state,dt):
  s=self.solver;e=s.surface_contact;x=state.particle_q;e.reference=x;e.detect(self.zero);e.evaluate(self.zero,dt);wp.launch(double_bulk,dim=s.model.particle_count,inputs=[-1,s.model.particle_colors,x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[s.volume_invalid,self.force,self.hessian],block_dim=64);self.objective_force.zero_();wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.objective_force]);self.instant.zero_();self.step_residual.zero_();wp.launch(translate_points,dim=s.model.particle_count,inputs=[x,self.origin],outputs=[self.world_x],block_dim=64);wp.launch(collect_loaded_external,dim=s.model.particle_count,inputs=[self.world_x,state.particle_qd,self.previous_velocity,self.previous_position,self.mass,self.fixed_mask,self.force,self.objective_force,e.physical_force,self.global_solver.external_force,s.board_stiffness,wp.float64(dt)],outputs=[self.impulse,self.angular,self.instant,self.residual_sum,self.step_residual,self.maximum_node,self.load_work],block_dim=64)
 def measurements(self,state):
  d=super().measurements(state);d['external_force_types']=['gravity','board','fixed_fixture','prescribed_synthetic_load'];d['prescribed_load_work_j']=float(self.load_work.numpy()[0]);d['energy_less_prescribed_work_j']=d['energy']['total_j']-d['prescribed_load_work_j'];return d

def balanced_cap_field(x,mass,cap,force,moment):
 """Mass-weighted dead load with declared resultant and centroidal moment."""
 x=np.asarray(x,dtype=float);mass=np.asarray(mass,dtype=float);cap=np.asarray(cap,dtype=bool);force=np.asarray(force,dtype=float);moment=np.asarray(moment,dtype=float);weights=mass[cap];total=weights.sum();center=np.sum(weights[:,None]*x[cap],axis=0)/total;r=x[cap]-center;inertia=np.sum(weights[:,None,None]*(np.sum(r*r,axis=1)[:,None,None]*np.eye(3)-r[:,:,None]*r[:,None,:]),axis=0);alpha=np.linalg.solve(inertia,moment);field=np.zeros_like(x);field[cap]=weights[:,None]*(force/total+np.cross(alpha,r));net=field.sum(0);torque=np.cross(x-center,field).sum(0)
 if not np.isfinite(field).all()or np.linalg.norm(net-force)>1e-12 or np.linalg.norm(torque-moment)>1e-12:raise ValueError('Synthetic load resultant/moment construction failed')
 return field,center
