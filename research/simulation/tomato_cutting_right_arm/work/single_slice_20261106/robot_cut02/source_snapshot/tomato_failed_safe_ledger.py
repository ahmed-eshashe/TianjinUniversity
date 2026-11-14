"""Fresh physical-world ledger for prepared partial/full failure mechanics.

The vanished stored-energy term skips its no-longer-physical frame; committed
fracture dissipation is recorded separately and included in total energy.
Original gravity (-9.81 world Z), fixture and board audit are retained.
"""
import numpy as np
import warp as wp
from tomato_local_frame_ledger import LocalFrameSupportLedger
from tomato_local_frame import translate_points
from tomato_double_blocks import double_bulk
from tomato_global_ledger import collect_world_external
from tomato_failed_cohesion_reference import fracture_dissipation

class FailedSafeLocalLedger(LocalFrameSupportLedger):
 def step(self,state,dt):
  from tomato_failed_safe_objective import objective_force
  s=self.solver;e=s.surface_contact;x=state.particle_q;e.reference=x;e.detect(self.zero);e.evaluate(self.zero,dt);wp.launch(double_bulk,dim=s.model.particle_count,inputs=[-1,s.model.particle_colors,x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[s.volume_invalid,self.force,self.hessian],block_dim=64);self.objective_force.zero_();wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.objective_force]);self.instant.zero_();self.step_residual.zero_();wp.launch(translate_points,dim=s.model.particle_count,inputs=[x,self.origin],outputs=[self.world_x],block_dim=64);wp.launch(collect_world_external,dim=s.model.particle_count,inputs=[self.world_x,state.particle_qd,self.previous_velocity,self.mass,self.fixed_mask,self.force,self.objective_force,e.physical_force,s.board_stiffness,wp.float64(dt)],outputs=[self.impulse,self.angular,self.instant,self.residual_sum,self.step_residual,self.maximum_node])
 def measurements(self,state):
  s=self.solver;d=self.data;wp.launch(translate_points,dim=s.model.particle_count,inputs=[state.particle_q,self.origin],outputs=[self.world_x],block_dim=64);x=self.world_x.numpy().astype(float);v=state.particle_qd.numpy().astype(float);mv=d['mass'][:,None]*v;p=mv.sum(0);angular=np.cross(x,mv).sum(0);external=self.impulse.numpy();external_angular=self.angular.numpy();length=np.linalg.norm(x[d['springs'][:,1]]-x[d['springs'][:,0]],axis=1);spring=float(np.sum(.5*d['k']*(length-self.spring_rest)**2));ratios=np.linalg.det(x[d['cells'][:,1:]]-x[d['cells'][:,:1]])/(6*d['volumes']);r=(np.minimum(ratios,.5)-.1)/.4;barrier=float(np.sum(10000*d['volumes']*(r-1-np.log(r))));kinetic=float(np.sum(.5*d['mass']*np.sum(v*v,axis=1)));gravity=float(np.sum(d['mass']*9.81*x[:,2]));board=float(np.sum(.5*self.board_k*np.maximum(-x[:,2],0)**2));cohesion=0.
  anchors=s.objective_anchors.numpy();sign=s.objective_sign.numpy();K=s.objective_stiffness.numpy();history=s.objective_history.numpy()
  for i,patch in enumerate(d['cohesion'].patches):
   if history[i,1]>=1.:continue
   q=x[d['pairs'][patch['indices']]];mid=q.mean(1);a,b,c=anchors[i];u=mid[b]-mid[a];v0=mid[c]-mid[a];t=u/np.linalg.norm(u);normal=sign[i]*np.cross(u,v0);normal/=np.linalg.norm(normal);frame=np.column_stack([normal,t,np.cross(normal,t)]);g=(q[:,1]-q[:,0])@frame;g[:,0]=np.maximum(g[:,0],0);cohesion+=(1-history[i,1])*.5*np.sum(patch['weights'][:,None]*g*(g@K[i]))
  contact=float(s.surface_contact.contact_energy.numpy()[0]);energy=dict(kinetic_j=kinetic,gravity_j=gravity,spring_j=spring,volume_barrier_j=barrier,cohesion_stored_j=float(cohesion),fracture_dissipated_j=float(fracture_dissipation(history,s.objective_law.numpy()).sum()),self_contact_j=contact,board_j=board);energy['total_j']=sum(energy.values());return dict(momentum_kg_m_s=p.tolist(),angular_momentum_kg_m2_s=angular.tolist(),gravity_board_fixture_impulse_ns=external.tolist(),gravity_board_fixture_angular_impulse_nms=external_angular.tolist(),gravity_board_fixture_force_n=self.instant.numpy().tolist(),linear_impulse_residual_ns=float(np.linalg.norm(p-external.sum(0))),angular_impulse_residual_nms=float(np.linalg.norm(angular-external_angular.sum(0))),energy=energy,cumulative_absolute_nodal_impulse_residual_ns=float(self.residual_sum.numpy()[0]),last_step_absolute_nodal_impulse_residual_ns=float(self.step_residual.numpy()[0]),maximum_single_node_step_residual_ns=float(self.maximum_node.numpy()[0]))
