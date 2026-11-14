import sys
sys.path.insert(0,'/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_completion_20261108_v07')
from full_surface import FullSurface
from cohesive_transfer import W
from closure_runtime import Closure
from pathlib import Path
import sys,time,json,numpy as np
sys.path.insert(0,str(W/'backend'))
from numerics import Bulk,load_arrays,tensor,torch
from torch.autograd import Function
torch.set_num_threads(1);s=FullSurface(device='cuda');c=Closure(s);m=s.mesh;x=m['x'];t=m['tets'];old=load_arrays();parent=m['parent_tet'];fixed=m['fixed'];mass=m['mass'];inv=1/mass;inv[fixed]=0
z=dict(x=x,tet_indices=t,tet_poses=np.linalg.inv((x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1)),physical_mass=mass,particle_inv_mass=inv,gravity=old['gravity'],contact_mask=np.ones(len(x)),fixed=fixed)
for key in ['tet_mu','tet_lambda','tet_damping','tet_activations']:z[key]=old[key][parent]
b=Bulk(z);V=1/(6*torch.linalg.det(b.dm));alpha=1+.75*b.mu/b.la
# Stable Neo-Hookean energy corresponding exactly to the corrected CUDA force.
def bulk_energy(q):
 D=(q[b.t[:,1:]]-q[b.t[:,0]][:,None]).transpose(1,2);F=D@b.dm;I=(F*F).sum((1,2));J=torch.linalg.det(F)
 return (V*(.5*b.mu*(I-3-torch.log((I+1)/4))+.5*b.la*((J-alpha)**2-(1-alpha)**2))).sum()
class ContactEnergy(Function):
 @staticmethod
 def forward(ctx,q):
  e,f=c.energy_force_precise(q.detach().cpu().numpy());ctx.save_for_backward(-tensor(f));return q.new_tensor(e)
 @staticmethod
 def backward(ctx,g):return g*ctx.saved_tensors[0]
class ViscousEnergy(Function):
 @staticmethod
 def forward(ctx,delta,h):
  cd=b.damping(delta).clone();ctx.save_for_backward(cd/h);return .5*(delta*cd).sum()/h
 @staticmethod
 def backward(ctx,g):return g*ctx.saved_tensors[0],None


rng=np.random.default_rng(73);q=x.copy();q[np.unique(m['tets'][m['tet_side']==1]),0]-=1e-5
u=rng.normal(size=x.shape);v=rng.normal(size=x.shape);u[fixed]=0;v[fixed]=0;u/=np.max(abs(u));v/=np.max(abs(v))
def action(d,eps):return -(c.energy_force_precise(q+eps*d)[1]-c.energy_force_precise(q-eps*d)[1])/(2*eps)
values=[action(u,e) for e in [2e-10,1e-10,5e-11]];hv=action(v,1e-10);hu=values[1]
errors=[float(np.linalg.norm(a-values[-1])/max(np.linalg.norm(values[-1]),1e-30)) for a in values[:-1]]
a=float((u*hv).sum());bb=float((v*hu).sum());sym=abs(a-bb)/max(abs(a),abs(bb),1e-30)
out=dict(method='Central differences of complete contact force, including geometry, embedding and mollifier; approximate Hessian action',refinement_relative_errors=errors,symmetry_relative_error=sym,passed=bool(max(errors)<.01 and sym<.01))
Path(__file__).with_name('contact_action_fine_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
