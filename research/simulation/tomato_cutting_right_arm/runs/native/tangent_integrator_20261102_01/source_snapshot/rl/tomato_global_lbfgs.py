"""Limited-memory inverse-BFGS corrections around the qualified global GN solve.

Only positive-curvature secants are retained. Memory is reset every physical
step because the incremental objective changes. Exact force/energy and all
admissibility, true-residual and acceptance gates are inherited unchanged.
Two-loop recursion follows Liu & Nocedal (1989); this custom candidate still
requires its own operator/integration qualification.
"""
import numpy as np
import warp as wp
from warp import sparse
from warp.optim.linear import cg,preconditioner
from tomato_global_implicit import GlobalImplicitCandidate,inertial_target,direction_bound,trial_position,global_volume_path,finalize_velocity

@wp.kernel(enable_backward=False)
def secant(x:wp.array[wp.vec3d],previous_x:wp.array[wp.vec3d],force:wp.array[wp.vec3d],previous_force:wp.array[wp.vec3d],s:wp.array[wp.vec3d],y:wp.array[wp.vec3d]):
 i=wp.tid();s[i]=x[i]-previous_x[i];y[i]=previous_force[i]-force[i]

@wp.kernel(enable_backward=False)
def axpy(x:wp.array[wp.vec3d],direction:wp.array[wp.vec3d],coefficient:wp.float64):
 i=wp.tid();x[i]+=coefficient*direction[i]

class PositiveLBFGSMemory:
 def __init__(self,n,*,maximum_pairs=8):
  self.n=n;self.maximum_pairs=maximum_pairs;self.pairs=[];self.previous_x=wp.empty(n,dtype=wp.vec3d);self.previous_force=wp.empty(n,dtype=wp.vec3d);self.ready=False;self.q=wp.empty(n,dtype=wp.vec3d);self.alphas=[];self.last_update={}
 def observe(self,x,force):
  accepted=False;curvature=0.;relative=0.
  if self.ready:
   s=wp.empty(self.n,dtype=wp.vec3d);y=wp.empty(self.n,dtype=wp.vec3d);wp.launch(secant,dim=self.n,inputs=[x,self.previous_x,force,self.previous_force],outputs=[s,y],block_dim=64);curvature=float(wp.utils.array_inner(s,y));scale=np.sqrt(max(0.,float(wp.utils.array_inner(s,s))*float(wp.utils.array_inner(y,y))));relative=curvature/max(scale,1e-300)
   if np.isfinite(curvature)and np.isfinite(scale)and curvature>max(1e-280,1e-10*scale):
    self.pairs.append((s,y,1/curvature));self.pairs=self.pairs[-self.maximum_pairs:];accepted=True
  wp.copy(self.previous_x,x);wp.copy(self.previous_force,force);self.ready=True;self.last_update=dict(accepted=accepted,curvature_j=curvature,relative_curvature=relative,memory_pairs=len(self.pairs));return self.last_update
 def transform(self,force):
  wp.copy(self.q,force);self.alphas=[0.]*len(self.pairs)
  for index in range(len(self.pairs)-1,-1,-1):
   s,y,rho=self.pairs[index];alpha=rho*float(wp.utils.array_inner(s,self.q));self.alphas[index]=alpha;wp.launch(axpy,dim=self.n,inputs=[self.q,y,wp.float64(-alpha)],block_dim=64)
  return self.q
 def finish(self,direction):
  for index,(s,y,rho)in enumerate(self.pairs):
   beta=rho*float(wp.utils.array_inner(y,direction));wp.launch(axpy,dim=self.n,inputs=[direction,s,wp.float64(self.alphas[index]-beta)],block_dim=64)
 def clear(self):self.pairs=[];self.alphas=[]

class GlobalLBFGSCandidate(GlobalImplicitCandidate):
 def _linear_direction(self,rhs):
  self.direction.zero_();iterations,recursive,tolerance=cg(self.assembly.matrix,rhs,self.direction,tol=1e-9,atol=1e-13,maxiter=self.maximum_cg,M=preconditioner(self.assembly.matrix,'diag'),check_every=10,use_cuda_graph=True);sparse.bsr_mv(self.assembly.matrix,self.direction,self.product);b=rhs.numpy();true=float(np.linalg.norm(self.product.numpy()-b));scale=float(np.linalg.norm(b));valid=bool(np.isfinite(true)and true<=max(5e-9*scale,1e-12));return dict(cg_iterations=int(iterations),cg_true_residual_n=true,cg_rhs_norm_n=scale,linear_valid=valid)
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
    wp.launch(trial_position,dim=self.n,inputs=[self.x,self.direction,wp.float64(fraction)],outputs=[self.trial],block_dim=64);self.trial_invalid.zero_();wp.launch(global_volume_path,dim=len(self.data['cells']),inputs=[self.x,self.trial,self.holder.cells,self.holder.volumes64],outputs=[self.trial_invalid],block_dim=64)
    if not self.trial_invalid.numpy()[0]:
     trial_energy=self.energy(self.trial,dt,trial=True);roundoff=64*np.finfo(float).eps*max(abs(G),1e-8)
     if np.isfinite(trial_energy)and trial_energy<=G-1e-4*fraction*descent+roundoff:accepted=True;break
    fraction*=.5
   row.update(line_search_halvings=line,step_fraction=fraction,descent=descent,line_accepted=accepted);self.last_trace.append(row)
   if not accepted:raise ValueError('No admissible descending corrected step; state/history not committed')
   wp.copy(self.x,self.trial)
  if not converged:raise ValueError('Global nonlinear solve exceeded its iteration budget; state/history not committed')
  wp.copy(state_out.particle_q,self.x);wp.launch(finalize_velocity,dim=self.n,inputs=[self.x,self.previous,wp.float64(dt)],outputs=[state_out.particle_qd],block_dim=64)
