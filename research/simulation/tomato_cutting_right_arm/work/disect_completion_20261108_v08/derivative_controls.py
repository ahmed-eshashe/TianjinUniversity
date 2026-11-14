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

rng=np.random.default_rng(42); direction=rng.normal(size=x.shape); direction[fixed]=0;direction/=np.linalg.norm(direction)
results=[]
for compression in [0.,1e-5]:
 q=x.copy();q[np.unique(m['tets'][m['tet_side']==1]),0]-=compression
 e,f=c.energy_force_precise(q); analytic=-float((f*direction).sum()); errors=[]
 for eps in [1e-7,1e-8,1e-9]:
  ep=c.energy_force_precise(q+eps*direction)[0];em=c.energy_force_precise(q-eps*direction)[0];fd=(ep-em)/(2*eps);errors.append(dict(eps=eps,finite_difference=fd,relative_error=abs(fd-analytic)/max(abs(fd),abs(analytic),1e-12)))
 results.append(dict(compression=compression,energy=e,analytic=analytic,checks=errors))
b.geometry();u=tensor(direction);v=tensor(rng.normal(size=x.shape));cu=b.damping(u).clone();cv=b.damping(v).clone();sym=abs(float((u*cv).sum()-(v*cu).sum()))/max(abs(float((u*cv).sum())),1e-12)
out=dict(closure=results,damping_symmetry_relative=sym,damping_quadratic=float((u*cu).sum()))
Path(__file__).with_name('derivative_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
