"""Explicitly versioned float64 coupled implicit-Euler numerical candidate.

Newton supplies the actual registry and complete collision queries. Warp sparse
PCG solves a global positive GN system; accepted steps backtrack the unchanged
incremental potential. This is not the stock native VBD integrator. Original
material, mass, fixture, contact and fracture parameters are retained in their
canonical source precision. No robot/body-contact integration is provided here.
"""
from types import SimpleNamespace
import numpy as np
import warp as wp
from warp import sparse
from warp.optim.linear import cg,preconditioner
from tomato_double_blocks import double_bulk
from tomato_global_gn_assembly import GlobalGNAssembly
from tomato_native_objective_reference import objective_force,incremental_objective_energy,validate_frames

@wp.kernel(enable_backward=False)
def inertial_target(x:wp.array[wp.vec3d],velocity:wp.array[wp.vec3d],free:wp.array[int],gravity:wp.vec3d,dt:wp.float64,target:wp.array[wp.vec3d]):
 i=wp.tid();target[i]=x[i]
 if free[i]!=0:target[i]=x[i]+dt*velocity[i]+dt*dt*gravity

@wp.kernel(enable_backward=False)
def global_rhs(x:wp.array[wp.vec3d],target:wp.array[wp.vec3d],mass:wp.array[wp.float64],free:wp.array[int],dt:wp.float64,bulk:wp.array[wp.vec3d],cohesion:wp.array[wp.vec3d],contact:wp.array[wp.vec3d],board_k:wp.array[float],height:wp.float64,rhs:wp.array[wp.vec3d],norm_sum:wp.array[wp.float64]):
 i=wp.tid();f=wp.vec3d(0.)
 if free[i]!=0:
  f=mass[i]/(dt*dt)*(target[i]-x[i])+bulk[i]+cohesion[i]+contact[i]
  if x[i][2]<height:f[2]+=wp.float64(board_k[i])*(height-x[i][2])
 rhs[i]=f;wp.atomic_add(norm_sum,0,wp.length(f))

@wp.kernel(enable_backward=False)
def node_energy(x:wp.array[wp.vec3d],target:wp.array[wp.vec3d],mass:wp.array[wp.float64],free:wp.array[int],dt:wp.float64,board_k:wp.array[float],height:wp.float64,energy:wp.array[wp.float64]):
 i=wp.tid();d=x[i]-target[i]
 if free[i]!=0:wp.atomic_add(energy,0,wp.float64(.5)*mass[i]/(dt*dt)*wp.dot(d,d))
 gap=wp.min(x[i][2]-height,wp.float64(0.));wp.atomic_add(energy,1,wp.float64(.5)*wp.float64(board_k[i])*gap*gap)

@wp.kernel(enable_backward=False)
def spring_energy(x:wp.array[wp.vec3d],pairs:wp.array[wp.vec2i],rest:wp.array[wp.float64],k:wp.array[wp.float64],energy:wp.array[wp.float64],invalid:wp.array[int]):
 i=wp.tid();ids=pairs[i];length=wp.length(x[ids[0]]-x[ids[1]])
 if length<wp.float64(1.e-8):wp.atomic_add(invalid,0,1)
 gap=wp.max(length,wp.float64(1.e-8))-rest[i];wp.atomic_add(energy,1,wp.float64(.5)*k[i]*gap*gap)

@wp.kernel(enable_backward=False)
def volume_energy(x:wp.array[wp.vec3d],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],energy:wp.array[wp.float64],invalid:wp.array[int]):
 i=wp.tid();ids=cells[i];a=x[ids[1]]-x[ids[0]];b=x[ids[2]]-x[ids[0]];c=x[ids[3]]-x[ids[0]];j=wp.dot(a,wp.cross(b,c))/(wp.float64(6.)*volumes[i])
 if j<=wp.float64(.1):wp.atomic_add(invalid,0,1)
 elif j<wp.float64(.5):
  r=(j-wp.float64(.1))/wp.float64(.4);wp.atomic_add(energy,1,wp.float64(10000.)*volumes[i]*(r-wp.float64(1.)-wp.log(r)))

@wp.kernel(enable_backward=False)
def direction_bound(direction:wp.array[wp.vec3d],bounds:wp.array[float],free:wp.array[int],fraction:wp.array[wp.float64],descent:wp.array[wp.float64],rhs:wp.array[wp.vec3d]):
 i=wp.tid()
 if free[i]!=0:
  length=wp.length(direction[i])
  if length>wp.float64(0.):wp.atomic_min(fraction,0,wp.min(wp.float64(1.),wp.float64(bounds[i])/length))
  wp.atomic_add(descent,0,wp.dot(rhs[i],direction[i]))
 else:direction[i]=wp.vec3d(0.)

@wp.kernel(enable_backward=False)
def trial_position(x:wp.array[wp.vec3d],direction:wp.array[wp.vec3d],fraction:wp.float64,trial:wp.array[wp.vec3d]):
 i=wp.tid();trial[i]=x[i]+fraction*direction[i]

@wp.kernel(enable_backward=False)
def global_volume_path(x:wp.array[wp.vec3d],trial:wp.array[wp.vec3d],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],invalid:wp.array[int]):
 i=wp.tid();ids=cells[i];a=x[ids[1]]-x[ids[0]];b=x[ids[2]]-x[ids[0]];c=x[ids[3]]-x[ids[0]];da=(trial[ids[1]]-trial[ids[0]])-a;db=(trial[ids[2]]-trial[ids[0]])-b;dc=(trial[ids[3]]-trial[ids[0]])-c;scale=wp.float64(1.)/(wp.float64(6.)*volumes[i]);j=wp.dot(a,wp.cross(b,c))*scale;c1=(wp.dot(da,wp.cross(b,c))+wp.dot(a,wp.cross(db,c))+wp.dot(a,wp.cross(b,dc)))*scale;c2=(wp.dot(da,wp.cross(db,c))+wp.dot(da,wp.cross(b,dc))+wp.dot(a,wp.cross(db,dc)))*scale;c3=wp.dot(da,wp.cross(db,dc))*scale
 if j-wp.abs(c1)-wp.abs(c2)-wp.abs(c3)<=wp.float64(.1):wp.atomic_add(invalid,0,1)

@wp.kernel(enable_backward=False)
def finalize_velocity(x:wp.array[wp.vec3d],previous:wp.array[wp.vec3d],dt:wp.float64,v:wp.array[wp.vec3d]):
 i=wp.tid();v[i]=(x[i]-previous[i])/dt

class GlobalImplicitCandidate:
 def __init__(self,holder,data,fixed,*,maximum_outer=40,maximum_cg=500,local_budget_ns=.0001,declared_duration_s=.1,gravity=(0.,0.,-9.81)):
  self.holder=holder;self.model=holder.model;self.data=data;self.n=len(data['x']);self.assembly=GlobalGNAssembly(holder,data,fixed);self.maximum_outer=maximum_outer;self.maximum_cg=maximum_cg;self.local_budget_ns=local_budget_ns;self.declared_duration_s=declared_duration_s;self.gravity=wp.vec3d(*gravity);self.x=wp.empty(self.n,dtype=wp.vec3d);self.previous=wp.empty(self.n,dtype=wp.vec3d);self.target=wp.empty(self.n,dtype=wp.vec3d);self.trial=wp.empty(self.n,dtype=wp.vec3d);self.zero=wp.zeros(self.n,dtype=wp.vec3);self.bulk_force=wp.zeros(self.n,dtype=wp.vec3d);self.bulk_hessian=wp.zeros(self.n,dtype=wp.mat33d);self.rhs=wp.zeros(self.n,dtype=wp.vec3d);self.direction=wp.zeros(self.n,dtype=wp.vec3d);self.product=wp.zeros(self.n,dtype=wp.vec3d);self.norm_sum=wp.zeros(1,dtype=wp.float64);self.energy_parts=wp.zeros(2,dtype=wp.float64);self.patch_energy=wp.zeros(holder.pairs.shape[0],dtype=wp.float64);self.invalid=wp.zeros(1,dtype=int);self.trial_invalid=wp.zeros(1,dtype=int);self.fraction=wp.ones(1,dtype=wp.float64);self.descent=wp.zeros(1,dtype=wp.float64);self.last_trace=[]
 def state(self):return SimpleNamespace(particle_q=wp.array(self.data['x'],dtype=wp.vec3d),particle_qd=wp.zeros(self.n,dtype=wp.vec3d))
 def reset(self,state):
  state.particle_q.assign(self.data['x']);state.particle_qd.zero_();self.holder.reset_material();self.holder.surface_contact.invalid.zero_();self.last_trace=[]
 def force(self,x,dt):
  s=self.holder;e=s.surface_contact;e.reference=x;e.invalid.zero_();s.volume_invalid.zero_();s.objective_invalid.zero_();self.invalid.zero_();e.detect(self.zero);e.evaluate(self.zero,dt);wp.launch(double_bulk,dim=self.n,inputs=[-1,s.model.particle_colors,x,s.spring_offsets,s.spring_ids,s.model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[self.invalid,self.bulk_force,self.bulk_hessian],block_dim=64);s.objective_force.zero_();wp.launch(validate_frames,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.objective_anchors],outputs=[s.objective_invalid]);wp.launch(objective_force,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[s.objective_force]);self.norm_sum.zero_();wp.launch(global_rhs,dim=self.n,inputs=[x,self.target,self.assembly.mass,self.assembly.free,wp.float64(dt),self.bulk_force,s.objective_force,e.physical_force,s.board_stiffness,wp.float64(s.board_height)],outputs=[self.rhs,self.norm_sum],block_dim=64)
  if self.invalid.numpy()[0] or s.objective_invalid.numpy()[0] or e.invalid.numpy()[0]:raise ValueError('Invalid current geometry in global implicit candidate')
  value=float(self.norm_sum.numpy()[0])
  if not np.isfinite(value):raise ValueError('Nonfinite global force residual')
  return value
 def energy(self,x,dt,*,trial=False):
  s=self.holder;e=s.surface_contact;old_reference=e.reference;old_invalid=e.invalid;bad=self.trial_invalid if trial else self.invalid;bad.zero_();self.energy_parts.zero_();e.reference=x;e.invalid=bad
  try:
   wp.launch(validate_frames,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.objective_anchors],outputs=[bad]);wp.launch(node_energy,dim=self.n,inputs=[x,self.target,self.assembly.mass,self.assembly.free,wp.float64(dt),s.board_stiffness,wp.float64(s.board_height)],outputs=[self.energy_parts],block_dim=64);wp.launch(spring_energy,dim=len(self.data['springs']),inputs=[x,self.assembly.springs,s.relative_spring_rest,s.relative_spring_k],outputs=[self.energy_parts,bad],block_dim=64);wp.launch(volume_energy,dim=len(self.data['cells']),inputs=[x,s.cells,s.volumes64],outputs=[self.energy_parts,bad],block_dim=64);wp.launch(incremental_objective_energy,dim=s.pairs.shape[0],inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[self.patch_energy]);e.evaluate(self.zero,dt);parts=self.energy_parts.numpy();cohesion=float(self.patch_energy.numpy().sum());contact=float(e.contact_energy.numpy()[0]);value=float(parts.sum()+cohesion+contact)
   if bad.numpy()[0] or not np.isfinite(value):return float('inf')
   return value
  finally:e.reference=old_reference;e.invalid=old_invalid
 def step(self,state_in,state_out,control,contacts,dt):
  if contacts is not None or control is not None or self.model.body_count:raise ValueError('Global implicit candidate has no robot/body-contact adapter')
  if state_in.particle_q.dtype!=wp.vec3d or state_in.particle_qd.dtype!=wp.vec3d:raise ValueError('Explicit float64 candidate state required; stock float32 states are not interchangeable')
  wp.copy(self.previous,state_in.particle_q);wp.copy(self.x,state_in.particle_q);wp.launch(inertial_target,dim=self.n,inputs=[self.previous,state_in.particle_qd,self.assembly.free,self.gravity,wp.float64(dt)],outputs=[self.target]);self.last_trace=[];step_budget=self.local_budget_ns*dt/self.declared_duration_s;converged=False
  for outer in range(self.maximum_outer):
   residual=self.force(self.x,dt)*dt;G=self.energy(self.x,dt);row=dict(outer=outer,absolute_nodal_impulse_residual_ns=residual,incremental_energy_j=G)
   if not np.isfinite(G):raise ValueError('Current global state has an invalid incremental potential')
   if residual<=step_budget:row['converged']=True;self.last_trace.append(row);converged=True;break
   counts=self.assembly.assemble(self.x,dt);self.direction.zero_();iterations,recursive,tolerance=cg(self.assembly.matrix,self.rhs,self.direction,tol=1e-5,atol=1e-12,maxiter=self.maximum_cg,M=preconditioner(self.assembly.matrix,'diag'),check_every=10,use_cuda_graph=True);sparse.bsr_mv(self.assembly.matrix,self.direction,self.product);b=self.rhs.numpy();true=float(np.linalg.norm(self.product.numpy()-b));scale=float(np.linalg.norm(b));row.update(**counts,cg_iterations=int(iterations),cg_true_residual_n=true,cg_rhs_norm_n=scale)
   if true>max(5e-5*scale,1e-10):self.last_trace.append(row);raise ValueError('Global coupled linear system did not converge to its declared true-residual budget')
   self.fraction.fill_(1.);self.descent.zero_()
   wp.launch(direction_bound,dim=self.n,inputs=[self.direction,self.holder.surface_contact.bounds,self.assembly.free,self.fraction,self.descent,self.rhs],block_dim=64);fraction=float(self.fraction.numpy()[0]);descent=float(self.descent.numpy()[0]);accepted=False
   if not np.isfinite(descent) or descent<=0:raise ValueError('Global coupled direction is not a descent direction')
   for line in range(40):
    wp.launch(trial_position,dim=self.n,inputs=[self.x,self.direction,wp.float64(fraction)],outputs=[self.trial],block_dim=64);self.trial_invalid.zero_();wp.launch(global_volume_path,dim=len(self.data['cells']),inputs=[self.x,self.trial,self.holder.cells,self.holder.volumes64],outputs=[self.trial_invalid],block_dim=64)
    if not self.trial_invalid.numpy()[0]:
     trial_energy=self.energy(self.trial,dt,trial=True);roundoff=64*np.finfo(float).eps*max(abs(G),1e-8)
     if np.isfinite(trial_energy) and trial_energy<=G-1e-4*fraction*descent+roundoff:accepted=True;break
    fraction*=.5
   row.update(line_search_halvings=line,step_fraction=fraction,descent=descent,line_accepted=accepted);self.last_trace.append(row)
   if not accepted:raise ValueError('No admissible descending global step found; state/history not committed')
   wp.copy(self.x,self.trial)
  if not converged:raise ValueError('Global nonlinear solve exceeded its iteration budget; state/history not committed')
  wp.copy(state_out.particle_q,self.x);wp.launch(finalize_velocity,dim=self.n,inputs=[self.x,self.previous,wp.float64(dt)],outputs=[state_out.particle_qd],block_dim=64)
