"""Prepared-history global mechanics with safe vanished-interface branches.

Exact source forces/energy are retained. Only the fully failed branch avoids
constructing a material frame whose traction is identically zero. This class
REFUSES active eligibility: live fracture committing/coupled blade eligibility
still needs its own transaction qualification.
"""
import numpy as np
import warp as wp
from warp import sparse
from tomato_fraction_boundary import FractionBoundaryCandidate
from tomato_tangent_gn import TangentGNAssembly,tensile_tangent_blocks
from tomato_global_gn_assembly import contact_cache,mass_blocks,spring_blocks,volume_blocks,contact_blocks
from tomato_patch_frame_coupled import failed_safe_coupled_blocks
from tomato_patch_frame_objective import objective_force,incremental_objective_energy,validate_active_frames
from tomato_double_blocks import double_bulk
from tomato_global_implicit import global_rhs,node_energy,spring_energy,volume_energy

class FailedSafeGNAssembly(TangentGNAssembly):
 def assemble(self,x,dt):
  from warp import sparse
  s=self.s;e=s.surface_contact;self.active_count.zero_();wp.launch(contact_cache,dim=e.stencil_capacity,inputs=[e.precise_position,e.endpoint,e.kind,e.mollifier_threshold,e.stencil_count,e.stencil_capacity,wp.float64(e.margin),wp.float64(e.model.soft_contact_ke)],outputs=[self.active_ids,self.active_count,self.coefficients,self.normals,self.us,self.vs,self.normal_k,self.mollifier_k,e.invalid],block_dim=64);active=int(self.active_count.numpy()[0]);ns=len(self.data['springs']);nc=len(self.data['cells']);np=s.pairs.shape[0];spring_offset=self.n;volume_offset=spring_offset+4*ns;cohesive_offset=volume_offset+16*nc;contact_offset=cohesive_offset+256*np;total=contact_offset+256*active
  if total>self.maximum_triplets:raise ValueError('Global sparse GN triplet memory budget exceeded; no state advanced')
  self.rows=wp.empty(total,dtype=int);self.cols=wp.empty(total,dtype=int);self.values=wp.empty(total,dtype=wp.mat33d);wp.launch(mass_blocks,dim=self.n,inputs=[self.mass,self.free,x,s.board_stiffness,wp.float64(s.board_height),wp.float64(dt)],outputs=[self.rows,self.cols,self.values],block_dim=64);wp.launch(spring_blocks,dim=(ns,2,2),inputs=[spring_offset,x,self.springs,s.relative_spring_k,self.free],outputs=[self.rows,self.cols,self.values],block_dim=64);wp.launch(volume_blocks,dim=(nc,4,4),inputs=[volume_offset,x,s.cells,s.volumes64,self.free],outputs=[self.rows,self.cols,self.values,s.volume_invalid],block_dim=64);wp.launch(failed_safe_coupled_blocks,dim=(np,16,16),inputs=[cohesive_offset,x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible,self.free],outputs=[self.rows,self.cols,self.values],block_dim=64)
  if active:wp.launch(contact_blocks,dim=(active,16,16),inputs=[contact_offset,self.active_ids,e.physical_ids,e.endpoint_weight,self.coefficients,self.normals,self.us,self.vs,self.normal_k,self.mollifier_k,self.free],outputs=[self.rows,self.cols,self.values],block_dim=64)
  sparse.bsr_set_from_triplets(self.matrix,self.rows,self.cols,self.values);counts=dict(active_contact_stencils=active,triplets=total);ns=len(self.data['springs']);wp.launch(tensile_tangent_blocks,dim=(ns,2,2),inputs=[x,self.springs,self.s.relative_spring_rest,self.s.relative_spring_k,self.free],outputs=[self.tangent_rows,self.tangent_cols,self.tangent_values],block_dim=64);sparse.bsr_set_from_triplets(self.tangent,self.tangent_rows,self.tangent_cols,self.tangent_values);sparse.bsr_axpy(self.tangent,self.matrix,alpha=1.,beta=1.);return counts

class FailedSafeFractionCandidate(FractionBoundaryCandidate):
 def __init__(self,holder,data,fixed,**kwargs):
  super().__init__(holder,data,fixed,**kwargs);self.assembly=FailedSafeGNAssembly(holder,data,fixed)
 def step(self,state_in,state_out,control,contacts,dt):
  if np.any(self.holder.eligible.numpy()):raise ValueError('Prepared-history candidate refuses live damage eligibility; accepted-history transaction is not qualified')
  return super().step(state_in,state_out,control,contacts,dt)
 def force(self,x,dt):
  s=self.holder;e=s.surface_contact;e.reference=x;e.invalid.zero_();s.volume_invalid.zero_();s.objective_invalid.zero_();self.invalid.zero_();e.detect(self.zero);e.evaluate(self.zero,dt);wp.launch(double_bulk,dim=self.n,inputs=[-1,s.model.particle_colors,x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[self.invalid,self.bulk_force,self.bulk_hessian],block_dim=64);s.objective_force.zero_();wp.launch(validate_active_frames,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.objective_anchors,s.objective_law,s.objective_history],outputs=[s.objective_invalid]);wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[s.objective_force]);self.norm_sum.zero_();self.maximum_acceleration_defect.zero_();wp.launch(global_rhs,dim=self.n,inputs=[x,self.target,self.assembly.mass,self.assembly.free,wp.float64(dt),self.bulk_force,s.objective_force,e.physical_force,s.board_stiffness,wp.float64(s.board_height)],outputs=[self.rhs,self.norm_sum,self.maximum_acceleration_defect],block_dim=64)
  if self.invalid.numpy()[0] or s.objective_invalid.numpy()[0] or e.invalid.numpy()[0]:raise ValueError('Invalid current geometry in global implicit candidate')
  value=float(self.norm_sum.numpy()[0])
  if not np.isfinite(value):raise ValueError('Nonfinite global force residual')
  return value
 def energy(self,x,dt,*,trial=False):
  s=self.holder;e=s.surface_contact;old_reference=e.reference;old_invalid=e.invalid;bad=self.trial_invalid if trial else self.invalid;bad.zero_();self.energy_parts.zero_();e.reference=x;e.invalid=bad
  try:
   wp.launch(validate_active_frames,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.objective_anchors,s.objective_law,s.objective_history],outputs=[bad]);wp.launch(node_energy,dim=self.n,inputs=[x,self.target,self.assembly.mass,self.assembly.free,wp.float64(dt),s.board_stiffness,wp.float64(s.board_height)],outputs=[self.energy_parts],block_dim=64);wp.launch(spring_energy,dim=len(self.data['springs']),inputs=[x,self.assembly.springs,s.relative_spring_rest,s.relative_spring_k],outputs=[self.energy_parts,bad],block_dim=64);wp.launch(volume_energy,dim=len(self.data['cells']),inputs=[x,s.cells,s.volumes64],outputs=[self.energy_parts,bad],block_dim=64);wp.launch(incremental_objective_energy,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.patch_energy]);e.evaluate(self.zero,dt);parts=self.energy_parts.numpy();cohesion=float(self.patch_energy.numpy().sum());contact=float(e.contact_energy.numpy()[0]);value=float(parts.sum()+cohesion+contact)
   if bad.numpy()[0] or not np.isfinite(value):return float('inf')
   return value
  finally:e.reference=old_reference;e.invalid=old_invalid
