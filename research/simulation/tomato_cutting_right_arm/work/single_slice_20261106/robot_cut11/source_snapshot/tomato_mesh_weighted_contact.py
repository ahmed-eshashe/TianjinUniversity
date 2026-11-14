"""Area-weighted synthetic penalty quadrature for the exact-blade diagnostic."""
import warp as wp
from newton.solvers import SolverVBD

@wp.kernel
def set_penalty(weights:wp.array[float],penalty:wp.array[float],material:wp.array[float]):
 i=wp.tid();penalty[i]=1750.*weights[i];material[i]=1750.*weights[i]

class MeshContactVBD(SolverVBD):
 def _solve_particle_iteration(self,state_in,state_out,contacts,dt,iter_num):
  if iter_num==0 and contacts is not None and self.contact_weights.size:
   wp.launch(set_penalty,dim=self.contact_weights.size,inputs=[self.contact_weights],outputs=[self.body_particle_contact_penalty_k,self.body_particle_contact_material_ke],device=self.device)
  super()._solve_particle_iteration(state_in,state_out,contacts,dt,iter_num)

def publish(contacts,samples,query,*,reference_area_m2=1e-6):
 import numpy as np
 from tomato_contact_snapshot import ARRAY_FIELDS
 from tomato_blade_record_roundtrip_worker import publish_owned
 if len(samples)>=contacts.soft_contact_max:raise ValueError('Contact stream overflow')
 kept=[i for i,p in enumerate(query['phi']) if p< -1e-12];count=len(kept)
 arrays={field:[] for field in ARRAY_FIELDS};weights=[]
 for i in kept:
  s=samples[i];arrays['soft_contact_particle'].append(-1);arrays['soft_contact_indices'].append(s['corners']);arrays['soft_contact_barycentric'].append(s['barycentric']);arrays['soft_contact_shape'].append(0);arrays['soft_contact_body_pos'].append(query['closest'][i].tolist());arrays['soft_contact_body_vel'].append([0.,0.,0.]);arrays['soft_contact_normal'].append(query['normal'][i].tolist());weights.append(s['area_m2']/reference_area_m2)
 if any(query['phi'][i]>1e-10 for i in range(len(samples))):raise ValueError('Solid-cell clipping produced exterior contact sample')
 payload=dict(soft_contact_count=[count],arrays=arrays);publish_owned(contacts,payload)
 return np.asarray(weights,dtype=np.float32),payload

def implicit_reference(positions,masses,payload,weights,dt):
 import numpy as np
 x=np.asarray(positions,dtype=float).ravel();a=np.repeat(masses,3)/dt**2;B=[];target=[]
 arrays=payload['arrays']
 for ids,bary,n,q in zip(arrays['soft_contact_indices'],arrays['soft_contact_barycentric'],arrays['soft_contact_normal'],arrays['soft_contact_body_pos']):
  row=np.zeros(len(x));normal=np.asarray(n,dtype=np.float32).astype(float)
  for node,w in zip(ids,np.asarray(bary,dtype=np.float32).astype(float)):row[3*node:3*node+3]+=w*normal
  B.append(row);target.append(normal@np.asarray(q,dtype=np.float32).astype(float))
 if not B:return x.reshape(-1,3),np.zeros_like(x).reshape(-1,3)
 B=np.array(B);target=np.array(target);k=1750.*np.asarray(weights,dtype=float);active=B@x<target;before=x.copy()
 for _ in range(128):
  H=np.diag(a)+B[active].T@(k[active,None]*B[active]);rhs=a*before+B[active].T@(k[active]*target[active]);x=np.linalg.solve(H,rhs);new=B@x<target
  if np.array_equal(new,active):return x.reshape(-1,3),((x-before)/dt).reshape(-1,3)
  active=new
 raise ValueError('Independent unilateral implicit reference did not converge')
