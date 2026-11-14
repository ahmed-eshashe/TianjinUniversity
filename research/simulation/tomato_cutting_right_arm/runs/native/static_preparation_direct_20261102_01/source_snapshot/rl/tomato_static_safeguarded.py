"""Static search safeguard: compare a poorly progressing L-BFGS step to GN.

Original forces, potential, geometry and force-balance criteria are inherited.
A larger positive-curvature memory improves the search; if its trial needs
many halvings, a plain-GN trial competes on actual admissible potential.
No physical time, material damping or constitutive parameter is introduced.
"""
import numpy as np
import warp as wp
from tomato_static_gravity import StaticGravityCandidate
from tomato_global_lbfgs import PositiveLBFGSMemory
from tomato_global_implicit import direction_bound,trial_position
from tomato_fraction_boundary import fraction_volume_path

class SafeguardedStaticCandidate(StaticGravityCandidate):
 def _admissible_trial(self,G):
  self.fraction.fill_(1.);self.descent.zero_();wp.launch(direction_bound,dim=self.n,inputs=[self.direction,self.holder.surface_contact.bounds,self.assembly.free,self.fraction,self.descent,self.rhs],block_dim=64);fraction=float(self.fraction.numpy()[0]);descent=float(self.descent.numpy()[0])
  if not np.isfinite(descent)or descent<=0:return dict(accepted=False,line_search_halvings=0)
  for line in range(40):
   wp.launch(trial_position,dim=self.n,inputs=[self.x,self.direction,wp.float64(fraction)],outputs=[self.trial],block_dim=64);self.trial_invalid.zero_();wp.launch(fraction_volume_path,dim=len(self.data['cells']),inputs=[self.x,self.trial,self.holder.cells,self.holder.volumes64],outputs=[self.trial_invalid],block_dim=64)
   if not self.trial_invalid.numpy()[0]:
    value=self.energy(self.trial,self.regularizer_s,trial=True);roundoff=64*np.finfo(float).eps*max(abs(G),1e-8)
    if np.isfinite(value)and value<=G-1e-4*fraction*descent+roundoff:return dict(accepted=True,energy_j=value,position=wp.clone(self.trial),line_search_halvings=line,step_fraction=fraction,descent=descent)
   fraction*=.5
  return dict(accepted=False,line_search_halvings=40)
 def solve_load(self,state,scale,*,maximum_outer=2000,force_l1_budget_n=1e-6,acceleration_budget_m_s2=1e-5,callback=None):
  if np.any(self.holder.eligible.numpy())or np.any(self.holder.objective_history.numpy()):raise ValueError('Static preload requires intact disabled eligibility')
  self.set_load(scale);wp.copy(self.x,state.particle_q);self.last_trace=[];memory=PositiveLBFGSMemory(self.n,maximum_pairs=64);tau=self.regularizer_s
  for outer in range(maximum_outer):
   residual=self.force(self.x,tau);G=self.energy(self.x,tau);acc=float(self.maximum_acceleration_defect.numpy()[0]);row=dict(static_iteration=outer,gravity_load_fraction=scale,force_l1_residual_n=residual,maximum_force_acceleration_m_s2=acc,potential_j=G,search_regularizer_s=tau)
   if not np.isfinite(G):raise ValueError('Invalid static potential')
   if residual<=force_l1_budget_n and acc<=acceleration_budget_m_s2:
    row['converged']=True;self.last_trace.append(row)
    if callback:callback(row)
    wp.copy(state.particle_q,self.x);state.particle_qd.zero_();return row
   update=memory.observe(self.x,self.rhs);counts=self.assembly.assemble(self.x,tau);linear=self._linear_direction(memory.transform(self.rhs));fallback=not linear['linear_valid']
   if not fallback:
    memory.finish(self.direction);dot=float(wp.utils.array_inner(self.rhs,self.direction));fallback=not np.isfinite(dot)or dot<=0
   if fallback:
    memory.clear();linear=self._linear_direction(self.rhs)
    if not linear['linear_valid']:self.last_trace.append(dict(row,**linear));raise ValueError('Static linear true-residual gate failed')
   first=self._admissible_trial(G);chosen=first;selected='plain_gn'if fallback or not memory.pairs else'lbfgs';candidates=[dict(name=selected,**{k:v for k,v in first.items()if k!='position'})]
   if memory.pairs and(not first['accepted']or first['line_search_halvings']>=4):
    gn_linear=self._linear_direction(self.rhs)
    if gn_linear['linear_valid']:
     second=self._admissible_trial(G);candidates.append(dict(name='plain_gn',linear=gn_linear,**{k:v for k,v in second.items()if k!='position'}));roundoff=16*np.finfo(float).eps*max(abs(G),1e-8)
     if second['accepted']and(not first['accepted']or second['energy_j']<first['energy_j']-roundoff):chosen=second;selected='plain_gn';memory.clear()
    else:candidates.append(dict(name='plain_gn',accepted=False,linear=gn_linear))
   row.update(**counts,**linear,lbfgs_update=update,selected_search=selected,search_candidates=candidates,line_accepted=chosen['accepted'])
   if chosen['accepted']:row.update(accepted_potential_j=chosen['energy_j'],line_search_halvings=chosen['line_search_halvings'],step_fraction=chosen['step_fraction'],descent=chosen['descent'])
   self.last_trace.append(row)
   if callback:callback(row)
   if not chosen['accepted']:raise ValueError('Both static search candidates failed admissible descent')
   wp.copy(self.x,chosen['position'])
  raise ValueError('Safeguarded static preparation exceeded its iteration budget')
