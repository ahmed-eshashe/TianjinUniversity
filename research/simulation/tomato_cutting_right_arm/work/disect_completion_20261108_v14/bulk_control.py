from contact_energy import ContactGraph
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
# Independent same-state force comparison before any trial dynamics.
with torch.enable_grad():
 q=tensor(x).detach().requires_grad_(True);f=-torch.autograd.grad(bulk_energy(q),q)[0]
b.geometry();reference=b.f.clone();bulkerr=(f-reference).abs().max().item()
qtest=x.copy();qtest[:,0]+=.002*(x[:,1]-x[:,1].mean());b.x.copy_(tensor(qtest));b.geometry();reference=b.f.clone()
with torch.enable_grad():
 q=tensor(qtest).detach().requires_grad_(True);f=-torch.autograd.grad(bulk_energy(q),q)[0]
bulkerr=max(bulkerr,(f-reference).abs().max().item());b.x.copy_(tensor(x));assert bulkerr<1e-8,bulkerr

from bulk_cache import BulkCache
with torch.enable_grad():
 q=tensor(qtest).requires_grad_(True);g=torch.autograd.grad(bulk_energy(q),q,create_graph=True)[0];u=torch.sin(torch.arange(q.numel(),device=q.device,dtype=q.dtype)).reshape(q.shape);expected=torch.autograd.grad(g,q,grad_outputs=u)[0]
cache=BulkCache(b,q,V,alpha);actual=cache.action(u);error=float((actual-expected).norm()/expected.norm());assert error<1e-10,error
Path(__file__).with_name('bulk_cache_control.json').write_text(json.dumps(dict(relative_error=error,passed=True)));print(error)
