"""Independent final-state force/impulse ledger for undamaged gravity support.

Uses the original bulk gradient, exact objective frame forces and independently
collected closure/board forces. It does not infer support reaction from the
measured particle momentum. Fixed support work is zero only at fixed position.
"""
import numpy as np
import warp as wp

@wp.kernel(enable_backward=False)
def collect_external(x:wp.array[wp.vec3],mass:wp.array[wp.float64],fixed:wp.array[int],bulk:wp.array[wp.vec3],cohesion:wp.array[wp.vec3d],closure:wp.array[wp.vec3d],board_k:wp.array[float],dt:wp.float64,impulse:wp.array[wp.vec3d],angular:wp.array[wp.vec3d],instant:wp.array[wp.vec3d]):
 i=wp.tid();q=x[i];p=wp.vec3d(wp.float64(q[0]),wp.float64(q[1]),wp.float64(q[2]));g=wp.vec3d(wp.float64(0.),wp.float64(0.),-mass[i]*wp.float64(9.81));bf=board_k[i]*wp.max(-q[2],0.);board=wp.vec3d(wp.float64(0.),wp.float64(0.),wp.float64(bf));reaction=wp.vec3d(0.)
 if fixed[i]!=0:
  f=bulk[i];reaction=-wp.vec3d(wp.float64(f[0]),wp.float64(f[1]),wp.float64(f[2]))-cohesion[i]-closure[i]-board-g
 wp.atomic_add(instant,0,g);wp.atomic_add(instant,1,board);wp.atomic_add(instant,2,reaction)
 wp.atomic_add(impulse,0,dt*g);wp.atomic_add(impulse,1,dt*board);wp.atomic_add(impulse,2,dt*reaction)
 wp.atomic_add(angular,0,dt*wp.cross(p,g));wp.atomic_add(angular,1,dt*wp.cross(p,board));wp.atomic_add(angular,2,dt*wp.cross(p,reaction))

class SupportLedger:
 def __init__(self,solver,data,fixed,board_k):
  self.solver=solver;self.data=data;self.board_k=np.asarray(board_k);self.fixed=np.asarray(fixed);n=solver.model.particle_count;self.colors=wp.zeros(n,dtype=int);self.force=wp.zeros(n,dtype=wp.vec3);self.hessian=wp.zeros(n,dtype=wp.mat33);self.objective_force=wp.zeros(n,dtype=wp.vec3d);self.objective_x=wp.empty(n,dtype=wp.vec3d);self.mass=wp.array(data['mass'],dtype=wp.float64);mask=np.zeros(n,dtype=int);mask[fixed]=1;self.fixed_mask=wp.array(mask,dtype=int);self.impulse=wp.zeros(3,dtype=wp.vec3d);self.angular=wp.zeros(3,dtype=wp.vec3d);self.instant=wp.zeros(3,dtype=wp.vec3d);self.spring_rest=solver.model.spring_rest_length.numpy().astype(float)
 def reset(self):
  self.impulse.zero_();self.angular.zero_();self.instant.zero_()
 def step(self,state,dt):
  from tomato_objective_bulk_gather import gather_bulk
  from tomato_native_objective_reference import cast_positions,objective_force
  s=self.solver
  wp.launch(gather_bulk,dim=s.model.particle_count,inputs=[0,self.colors,state.particle_q,s.particle_q_prev,dt,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.model.spring_rest_length,s.model.spring_stiffness,s.model.spring_damping,s.patch_offsets,s.patch_ids,s.pairs,s.rest,s.weights,s.counts,s.stiffness,s.law,s.history,s.eligible,s.invalid,s.cell_offsets,s.cell_ids,s.cells,s.volumes,s.volume_invalid],outputs=[self.force,self.hessian])
  wp.launch(cast_positions,dim=s.model.particle_count,inputs=[state.particle_q],outputs=[self.objective_x]);self.objective_force.zero_()
  wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[self.objective_x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.objective_force]);s.surface_contact.evaluate(state.particle_q,dt);self.instant.zero_()
  wp.launch(collect_external,dim=s.model.particle_count,inputs=[state.particle_q,self.mass,self.fixed_mask,self.force,self.objective_force,s.surface_contact.physical_force,s.board_stiffness,wp.float64(dt)],outputs=[self.impulse,self.angular,self.instant])
 def measurements(self,state):
  s=self.solver;d=self.data;x=state.particle_q.numpy().astype(float);v=state.particle_qd.numpy().astype(float);mv=d['mass'][:,None]*v;p=mv.sum(0);angular=np.cross(x,mv).sum(0);external=self.impulse.numpy();external_angular=self.angular.numpy();length=np.linalg.norm(x[d['springs'][:,1]]-x[d['springs'][:,0]],axis=1);spring=float(np.sum(.5*d['k']*(length-self.spring_rest)**2));ratios=np.linalg.det(x[d['cells'][:,1:]]-x[d['cells'][:,:1]])/(6*d['volumes']);r=(np.minimum(ratios,.5)-.1)/.4;barrier=float(np.sum(10000*d['volumes']*(r-1-np.log(r))));kinetic=float(np.sum(.5*d['mass']*np.sum(v*v,axis=1)));gravity=float(np.sum(d['mass']*9.81*x[:,2]));board=float(np.sum(.5*self.board_k*np.maximum(-x[:,2],0)**2));cohesion=0.
  anchors=s.objective_anchors.numpy();sign=s.objective_sign.numpy();K=s.objective_stiffness.numpy();history=s.objective_history.numpy()
  for i,patch in enumerate(d['cohesion'].patches):
   q=x[d['pairs'][patch['indices']]];mid=q.mean(1);a,b,c=anchors[i];u=mid[b]-mid[a];v0=mid[c]-mid[a];t=u/np.linalg.norm(u);normal=sign[i]*np.cross(u,v0);normal/=np.linalg.norm(normal);frame=np.column_stack([normal,t,np.cross(normal,t)]);g=(q[:,1]-q[:,0])@frame;g[:,0]=np.maximum(g[:,0],0);cohesion+=(1-history[i,1])*.5*np.sum(patch['weights'][:,None]*g*(g@K[i]))
  contact=float(s.surface_contact.contact_energy.numpy()[0]);energy=dict(kinetic_j=kinetic,gravity_j=gravity,spring_j=spring,volume_barrier_j=barrier,cohesion_stored_j=float(cohesion),self_contact_j=contact,board_j=board);energy['total_j']=sum(energy.values());return dict(momentum_kg_m_s=p.tolist(),angular_momentum_kg_m2_s=angular.tolist(),gravity_board_fixture_impulse_ns=external.tolist(),gravity_board_fixture_angular_impulse_nms=external_angular.tolist(),gravity_board_fixture_force_n=self.instant.numpy().tolist(),linear_impulse_residual_ns=float(np.linalg.norm(p-external.sum(0))),angular_impulse_residual_nms=float(np.linalg.norm(angular-external_angular.sum(0))),energy=energy)
