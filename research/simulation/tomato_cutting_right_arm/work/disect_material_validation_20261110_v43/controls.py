"""Independent stress/energy and actual GPU-force checks plus rest bulk CFL bound.
The bound is local to the undeformed bulk, not a nonlinear cutting guarantee.
"""
from pathlib import Path
import sys,json,hashlib,time,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W));from assembly import z,m
from numerics import Bulk,numpy_force,tensor,torch
from scipy.spatial.transform import Rotation
start=time.perf_counter();mu=float(z['tet_mu'][0]);la=float(z['tet_lambda'][0]);alpha=1+.75*mu/la
assert json.loads((W/'approval.json').read_text())['approved']
def stress(F):
 J=np.linalg.det(F);return mu*(1-1/(np.sum(F*F)+1))*F+la*(J-alpha)*J*np.linalg.inv(F).T
def energy(F):
 I=np.sum(F*F);J=np.linalg.det(F);return .5*mu*(I-np.log(I+1))+.5*la*(J-alpha)**2
rng=np.random.default_rng(43);rot=Rotation.from_rotvec([.31,-.17,.27]).as_matrix();rows=[];b=Bulk(z)
for k in range(10):
 F=np.eye(3) if k==0 else np.eye(3)+rng.normal(0,.04,(3,3));assert np.linalg.det(F)>0
 P=stress(F);eps=1e-6;num=np.zeros((3,3))
 for i in range(3):
  for j in range(3):
   d=np.zeros((3,3));d[i,j]=eps;num[i,j]=(energy(F+d)-energy(F-d))/(2*eps)
 gradient=float(np.linalg.norm(num-P)/max(np.linalg.norm(P),1.))
 obj=float(np.linalg.norm(stress(rot@F)-rot@P)/max(np.linalg.norm(P),1.));enerr=abs(energy(rot@F)-energy(F))/max(abs(energy(F)),1.)
 q=z['x']@F.T;b.x.copy_(tensor(q));b.v.zero_();gpu=b.geometry().cpu().numpy().copy();cpu=numpy_force(z,q,np.zeros_like(q));diff=float(np.linalg.norm(gpu-cpu)/max(np.linalg.norm(cpu),1e-6))
 resultant=float(np.linalg.norm(cpu.sum(0)));torque=float(np.linalg.norm(np.cross(q,cpu).sum(0)))
 rows.append(dict(case=k,energy_gradient_relative=gradient,objectivity_relative=obj,energy_objectivity_relative=enerr,gpu_cpu_relative=diff,force_resultant_N=resultant,moment_resultant_Nm=torque))
 assert gradient<1e-4 and obj<1e-8 and enerr<1e-12 and np.linalg.norm(gpu-cpu)<=1e-10+1e-7*np.linalg.norm(cpu) and resultant<1e-7 and torque<1e-8,rows[-1]
# Absolute local row sums bound assembled M^-1/2 K M^-1/2 by triangle inequality.
# Explicit symplectic Euler undamped bulk stability: h < 2/sqrt(bound).
t=z['tet_indices'];dm=z['tet_poses'];G=np.concatenate([-dm.sum(1)[:,None],dm],axis=1);V=1/(6*np.linalg.det(dm));ml=.75*mu;ll=la-.625*mu;mass=z['physical_mass'];free=z['particle_inv_mass']>0
boundrows=np.zeros((len(mass),3))
for i in range(4):
 for j in range(4):
  gi=G[:,i];gj=G[:,j];K=V[:,None,None]*(ll*gi[:,:,None]*gj[:,None,:]+ml*np.einsum('ei,ei->e',gi,gj)[:,None,None]*np.eye(3)+ml*gj[:,:,None]*gi[:,None,:])
  scale=(free[t[:,i]]*free[t[:,j]])/np.sqrt(mass[t[:,i]]*mass[t[:,j]])
  np.add.at(boundrows,t[:,i],np.abs(K*scale[:,None,None]).sum(2))
B=float(boundrows.max());limit=2/np.sqrt(B)
# Also scale previously qualified hold step by worst elastic tangent ratio,
# retaining an additional factor of two below the conservative rest bulk bound.
oldmu=9000.;oldla=4500.;ratio=max(ml/oldmu,(ll+2*ml)/(oldla+2*oldmu));target=min(12.5e-6/np.sqrt(ratio),.5*limit);sub=int(np.ceil(.001/target));h=.001/sub
out=dict(passed=True,scope='Constitutive and rest bulk timestep controls only; no settling/contact/fracture pass',kernel_mu_Pa=mu,kernel_lambda_Pa=la,effective_Young_Pa=400000.,effective_Poisson=.3,rows=rows,rest_stiffness_mass_normalized_upper_bound_s2=B,rest_undamped_bulk_dt_limit_s=limit,old_to_new_tangent_ratio=ratio,selected_hold_dt_s=h,hold_steps_per_ms=sub,half_step_s=h/2,stability_limitations='Rest bulk bound only; nonlinear material/cohesive/contact stability and accuracy require fresh hold/contact and half-step qualification. No bound claimed for compressed cutting states.',wall_s=time.perf_counter()-start)
(W/'constitutive_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
# Isolated blade packet must change only two arrays and survive reset.
from candidate_blade import CandidateBlade
c=CandidateBlade();from assembly import old
for key in ['tet_mu','tet_lambda']:
 assert np.all(c.z[key]==z[key][0])
assert np.all(old['tet_mu']==12000.) and np.all(old['tet_lambda']==12000.)
from candidate_blade import baseline_packet as original_packet
changed=[key for key in c.z if not np.array_equal(c.z[key],original_packet[key])]
assert sorted(changed)==['tet_lambda','tet_mu'],changed
c.reset();assert np.all(c.mu.cpu().numpy()==mu) and np.all(c.la.cpu().numpy()==la)
(W/'packet_isolation.json').write_text(json.dumps({'passed':True,'changed_arrays':changed,'fresh_rest_state':True,'original_unchanged':True,'reset_retains_new_material':True},indent=2))
