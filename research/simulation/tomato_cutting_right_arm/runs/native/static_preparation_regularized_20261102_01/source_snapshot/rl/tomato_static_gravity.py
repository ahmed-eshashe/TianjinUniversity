"""Explicit gravity-preload equilibrium preparation; no physical time advances.

Forces/potential contain the original elastic/contact law and gravity only.
The mass/(regularizer_s^2) term exists ONLY in the numerical search matrix;
it supplies neither inertia nor material damping. Original rest geometry,
fixture, constitutive values, history and collision surface remain unchanged.
A prepared equilibrium is a new, disclosed initial configuration. It cannot
qualify an earlier failed floating-target transient or dynamic time accuracy.
"""
import numpy as np
import warp as wp
from tomato_failed_safe_global import FailedSafeFractionCandidate
from tomato_failed_safe_objective import objective_force,incremental_objective_energy,validate_active_frames
from tomato_double_blocks import double_bulk
from tomato_global_implicit import spring_energy,volume_energy,direction_bound,trial_position
from tomato_fraction_boundary import fraction_volume_path
from tomato_global_lbfgs import PositiveLBFGSMemory

@wp.kernel(enable_backward=False)
def static_rhs(x:wp.array[wp.vec3d],mass:wp.array[wp.float64],free:wp.array[int],gravity:wp.vec3d,bulk:wp.array[wp.vec3d],cohesion:wp.array[wp.vec3d],contact:wp.array[wp.vec3d],board_k:wp.array[float],height:wp.float64,rhs:wp.array[wp.vec3d],norm_sum:wp.array[wp.float64],maximum_acceleration_defect:wp.array[wp.float64]):
 i=wp.tid();f=wp.vec3d(0.)
 if free[i]!=0:
  f=mass[i]*gravity+bulk[i]+cohesion[i]+contact[i]
  if x[i][2]<height:f[2]+=wp.float64(board_k[i])*(height-x[i][2])
 rhs[i]=f;wp.atomic_add(norm_sum,0,wp.length(f))
 if free[i]!=0:wp.atomic_max(maximum_acceleration_defect,0,wp.length(f)/mass[i])

@wp.kernel(enable_backward=False)
def static_node_energy(x:wp.array[wp.vec3d],reference:wp.array[wp.vec3d],mass:wp.array[wp.float64],free:wp.array[int],gravity:wp.vec3d,board_k:wp.array[float],height:wp.float64,energy:wp.array[wp.float64]):
 i=wp.tid();wp.atomic_add(energy,0,-mass[i]*wp.dot(gravity,x[i]-reference[i]));gap=wp.min(x[i][2]-height,wp.float64(0.));wp.atomic_add(energy,1,wp.float64(.5)*wp.float64(board_k[i])*gap*gap)

class StaticGravityCandidate(FailedSafeFractionCandidate):
 def __init__(self,holder,data,fixed,*,regularizer_s=.002,**kwargs):
  super().__init__(holder,data,fixed,**kwargs);self.reference=wp.array(data['x'],dtype=wp.vec3d);self.load_gravity=self.gravity;self.regularizer_s=regularizer_s
 def step(self,*args,**kwargs):raise ValueError('Static preload preparation has no physical timestep; use solve_load')
 def set_load(self,scale):
  if not np.isfinite(scale)or not 0<=scale<=1:raise ValueError('Gravity load fraction must be within [0,1]')
  self.load_gravity=wp.vec3d(0.,0.,-9.81*scale)
 def solve_load(self,state,scale,*,maximum_outer=2000,force_l1_budget_n=1e-6,acceleration_budget_m_s2=1e-5,callback=None):
  if np.any(self.holder.eligible.numpy())or np.any(self.holder.objective_history.numpy()):raise ValueError('Gravity preload is intact/eligibility-disabled only')
  self.set_load(scale);wp.copy(self.x,state.particle_q);self.last_trace=[];memory=PositiveLBFGSMemory(self.n);tau=self.regularizer_s
  for outer in range(maximum_outer):
   residual=self.force(self.x,tau);G=self.energy(self.x,tau);acc=float(self.maximum_acceleration_defect.numpy()[0]);row=dict(static_iteration=outer,gravity_load_fraction=scale,force_l1_residual_n=residual,maximum_force_acceleration_m_s2=acc,potential_j=G,search_regularizer_s=tau)
   if not np.isfinite(G):raise ValueError('Invalid static current potential')
   if residual<=force_l1_budget_n and acc<=acceleration_budget_m_s2:
    row['converged']=True;self.last_trace.append(row)
    if callback:callback(row)
    wp.copy(state.particle_q,self.x);state.particle_qd.zero_();return row
   update=memory.observe(self.x,self.rhs);counts=self.assembly.assemble(self.x,tau);linear=self._linear_direction(memory.transform(self.rhs));fallback=not linear['linear_valid']
   if not fallback:
    memory.finish(self.direction);dot=float(wp.utils.array_inner(self.rhs,self.direction));fallback=not np.isfinite(dot)or dot<=0
   if fallback:
    memory.clear();linear=self._linear_direction(self.rhs)
    if not linear['linear_valid']:self.last_trace.append(dict(row,**linear));raise ValueError('Static coupled linear true-residual gate failed')
   row.update(**counts,**linear,lbfgs_update=update,plain_gn_fallback=fallback);self.fraction.fill_(1.);self.descent.zero_();wp.launch(direction_bound,dim=self.n,inputs=[self.direction,self.holder.surface_contact.bounds,self.assembly.free,self.fraction,self.descent,self.rhs],block_dim=64);fraction=float(self.fraction.numpy()[0]);descent=float(self.descent.numpy()[0]);accepted=False
   if not np.isfinite(descent)or descent<=0:raise ValueError('Static direction is not descending')
   for line in range(40):
    wp.launch(trial_position,dim=self.n,inputs=[self.x,self.direction,wp.float64(fraction)],outputs=[self.trial],block_dim=64);self.trial_invalid.zero_();wp.launch(fraction_volume_path,dim=len(self.data['cells']),inputs=[self.x,self.trial,self.holder.cells,self.holder.volumes64],outputs=[self.trial_invalid],block_dim=64)
    if not self.trial_invalid.numpy()[0]:
     trial=self.energy(self.trial,tau,trial=True);roundoff=64*np.finfo(float).eps*max(abs(G),1e-8)
     if np.isfinite(trial)and trial<=G-1e-4*fraction*descent+roundoff:accepted=True;break
    fraction*=.5
   row.update(line_search_halvings=line,step_fraction=fraction,descent=descent,line_accepted=accepted);self.last_trace.append(row)
   if callback:callback(row)
   if not accepted:raise ValueError('No admissible descending static trial; preparation state not committed')
   wp.copy(self.x,self.trial)
  raise ValueError('Static preparation exceeded its declared iteration budget')
 def force(self,x,dt):
  s=self.holder;e=s.surface_contact;e.reference=x;e.invalid.zero_();s.volume_invalid.zero_();s.objective_invalid.zero_();self.invalid.zero_();e.detect(self.zero);e.evaluate(self.zero,dt);wp.launch(double_bulk,dim=self.n,inputs=[-1,s.model.particle_colors,x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[self.invalid,self.bulk_force,self.bulk_hessian],block_dim=64);s.objective_force.zero_();wp.launch(validate_active_frames,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.objective_anchors,s.objective_law,s.objective_history],outputs=[s.objective_invalid]);wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[s.objective_force]);self.norm_sum.zero_();self.maximum_acceleration_defect.zero_();wp.launch(static_rhs,dim=self.n,inputs=[x,self.assembly.mass,self.assembly.free,self.load_gravity,self.bulk_force,s.objective_force,e.physical_force,s.board_stiffness,wp.float64(s.board_height)],outputs=[self.rhs,self.norm_sum,self.maximum_acceleration_defect],block_dim=64)
  if self.invalid.numpy()[0] or s.objective_invalid.numpy()[0] or e.invalid.numpy()[0]:raise ValueError('Invalid current geometry in global implicit candidate')
  value=float(self.norm_sum.numpy()[0])
  if not np.isfinite(value):raise ValueError('Nonfinite global force residual')
  return value
 def energy(self,x,dt,*,trial=False):
  s=self.holder;e=s.surface_contact;old_reference=e.reference;old_invalid=e.invalid;bad=self.trial_invalid if trial else self.invalid;bad.zero_();self.energy_parts.zero_();e.reference=x;e.invalid=bad
  try:
   wp.launch(validate_active_frames,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.objective_anchors,s.objective_law,s.objective_history],outputs=[bad]);wp.launch(static_node_energy,dim=self.n,inputs=[x,self.reference,self.assembly.mass,self.assembly.free,self.load_gravity,s.board_stiffness,wp.float64(s.board_height)],outputs=[self.energy_parts],block_dim=64);wp.launch(spring_energy,dim=len(self.data['springs']),inputs=[x,self.assembly.springs,s.relative_spring_rest,s.relative_spring_k],outputs=[self.energy_parts,bad],block_dim=64);wp.launch(volume_energy,dim=len(self.data['cells']),inputs=[x,s.cells,s.volumes64],outputs=[self.energy_parts,bad],block_dim=64);wp.launch(incremental_objective_energy,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.patch_energy]);e.evaluate(self.zero,dt);parts=self.energy_parts.numpy();cohesion=float(self.patch_energy.numpy().sum());contact=float(e.contact_energy.numpy()[0]);value=float(parts.sum()+cohesion+contact)
   if bad.numpy()[0] or not np.isfinite(value):return float('inf')
   return value
  finally:e.reference=old_reference;e.invalid=old_invalid
