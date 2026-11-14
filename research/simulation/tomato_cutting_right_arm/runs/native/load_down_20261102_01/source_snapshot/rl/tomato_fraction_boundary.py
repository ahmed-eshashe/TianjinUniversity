"""Numerical fraction-to-volume-boundary safeguard, physical J floor unchanged.

Each nonlinear trial retains >=20% of its current gap to J=.1 along the
conservative exact-cubic path bound. Multiple valid trials may approach the
same physical boundary. This is a line-search strategy, not a higher material
volume floor. Forces, energy, convergence and output gates are unchanged.
General method precedent: Wachter & Biegler (2006), Eq15; our nonlinear-volume
adaptation, conservative bound and 0.8 fraction require independent checks.
"""
import numpy as np
import warp as wp
from tomato_tangent_gn import TangentCandidate
from tomato_global_lbfgs import PositiveLBFGSMemory,inertial_target,direction_bound,trial_position,finalize_velocity

@wp.kernel(enable_backward=False)
def fraction_volume_path(x:wp.array[wp.vec3d],trial:wp.array[wp.vec3d],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],invalid:wp.array[int]):
 i=wp.tid();ids=cells[i];a=x[ids[1]]-x[ids[0]];b=x[ids[2]]-x[ids[0]];c=x[ids[3]]-x[ids[0]];da=(trial[ids[1]]-trial[ids[0]])-a;db=(trial[ids[2]]-trial[ids[0]])-b;dc=(trial[ids[3]]-trial[ids[0]])-c;scale=wp.float64(1.)/(wp.float64(6.)*volumes[i]);j=wp.dot(a,wp.cross(b,c))*scale;c1=(wp.dot(da,wp.cross(b,c))+wp.dot(a,wp.cross(db,c))+wp.dot(a,wp.cross(b,dc)))*scale;c2=(wp.dot(da,wp.cross(db,c))+wp.dot(da,wp.cross(b,dc))+wp.dot(a,wp.cross(db,dc)))*scale;c3=wp.dot(da,wp.cross(db,dc))*scale
 if j-wp.abs(c1)-wp.abs(c2)-wp.abs(c3)<=wp.float64(.1)+wp.float64(.2)*(j-wp.float64(.1)):wp.atomic_add(invalid,0,1)


class FractionBoundaryCandidate(TangentCandidate):
 def step(self,state_in,state_out,control,contacts,dt):
  if contacts is not None or control is not None or self.model.body_count:raise ValueError('Global implicit candidate has no robot/body-contact adapter')
  if state_in.particle_q.dtype!=wp.vec3d or state_in.particle_qd.dtype!=wp.vec3d:raise ValueError('Explicit float64 candidate state required')
  wp.copy(self.previous,state_in.particle_q);wp.copy(self.x,state_in.particle_q);wp.launch(inertial_target,dim=self.n,inputs=[self.previous,state_in.particle_qd,self.assembly.free,self.gravity,wp.float64(dt)],outputs=[self.target]);self.last_trace=[];step_budget=self.local_budget_ns*dt/self.declared_duration_s;converged=False;memory=PositiveLBFGSMemory(self.n)
  for outer in range(self.maximum_outer):
   residual=self.force(self.x,dt)*dt;G=self.energy(self.x,dt);velocity_defect=float(self.maximum_acceleration_defect.numpy()[0])*dt;row=dict(outer=outer,absolute_nodal_impulse_residual_ns=residual,maximum_euler_velocity_defect_m_s=velocity_defect,incremental_energy_j=G)
   if not np.isfinite(G):raise ValueError('Current state has invalid incremental potential')
   if residual<=step_budget and velocity_defect<=self.velocity_defect_budget_m_s*dt/self.declared_duration_s:row['converged']=True;self.last_trace.append(row);converged=True;break
   update=memory.observe(self.x,self.rhs);counts=self.assembly.assemble(self.x,dt);linear_rhs=memory.transform(self.rhs);linear=self._linear_direction(linear_rhs);fallback=not linear['linear_valid']
   if not fallback:
    memory.finish(self.direction);dot=float(wp.utils.array_inner(self.rhs,self.direction));fallback=not np.isfinite(dot)or dot<=0
   if fallback:
    memory.clear();linear=self._linear_direction(self.rhs)
    if not linear['linear_valid']:self.last_trace.append(dict(row,**linear));raise ValueError('Coupled linear solve failed true-residual gate, including plain-GN fallback')
   row.update(**counts,**linear,lbfgs_update=update,plain_gn_fallback=fallback);self.fraction.fill_(1.);self.descent.zero_();wp.launch(direction_bound,dim=self.n,inputs=[self.direction,self.holder.surface_contact.bounds,self.assembly.free,self.fraction,self.descent,self.rhs],block_dim=64);fraction=float(self.fraction.numpy()[0]);descent=float(self.descent.numpy()[0]);accepted=False
   if not np.isfinite(descent)or descent<=0:raise ValueError('Corrected global direction is not a descent direction')
   for line in range(40):
    wp.launch(trial_position,dim=self.n,inputs=[self.x,self.direction,wp.float64(fraction)],outputs=[self.trial],block_dim=64);self.trial_invalid.zero_();wp.launch(fraction_volume_path,dim=len(self.data['cells']),inputs=[self.x,self.trial,self.holder.cells,self.holder.volumes64],outputs=[self.trial_invalid],block_dim=64)
    if not self.trial_invalid.numpy()[0]:
     trial_energy=self.energy(self.trial,dt,trial=True);roundoff=64*np.finfo(float).eps*max(abs(G),1e-8)
     if np.isfinite(trial_energy)and trial_energy<=G-1e-4*fraction*descent+roundoff:accepted=True;break
    fraction*=.5
   row.update(line_search_halvings=line,step_fraction=fraction,descent=descent,line_accepted=accepted);self.last_trace.append(row)
   if not accepted:raise ValueError('No admissible descending corrected step; state/history not committed')
   wp.copy(self.x,self.trial)
  if not converged:raise ValueError('Global nonlinear solve exceeded its iteration budget; state/history not committed')
  wp.copy(state_out.particle_q,self.x);wp.launch(finalize_velocity,dim=self.n,inputs=[self.x,self.previous,wp.float64(dt)],outputs=[state_out.particle_qd],block_dim=64)
