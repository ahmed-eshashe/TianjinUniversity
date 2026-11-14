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


from contact_energy import ContactGraph

xx=np.load(Path(__file__).with_name('failed_iterate.npz'))['q'];er,fr=c.energy_force_precise(xx)
with torch.enable_grad():
 q=tensor(xx).requires_grad_(True);graph=ContactGraph(c,q);e=graph.energy(q);g=torch.autograd.grad(e,q)[0]
rng=np.random.default_rng(55);directions=[fr/max(abs(fr).max(),1e-30),rng.normal(size=xx.shape)];rows=[]
for u in directions:
 u/=max(abs(u).max(),1e-30);exact=-float((fr*u).sum());values=[]
 for eps in [1e-8,1e-9,1e-10,1e-11,1e-12]:
  ep,fp=c.energy_force_precise(xx+eps*u);np_=int(c.engine.stencil_count.numpy()[0]);em,fm=c.energy_force_precise(xx-eps*u);nm=int(c.engine.stencil_count.numpy()[0]);fd=(ep-em)/(2*eps)
  values.append(dict(eps=eps,energy_derivative=fd,expected=exact,relative_error=abs(fd-exact)/max(abs(fd),abs(exact),1e-20),force_jump=float(np.linalg.norm(fp-fm)),counts=[np_,nm]))
 rows.append(values)
out=dict(force_relative=float(np.linalg.norm(g.cpu().numpy()+fr)/max(np.linalg.norm(fr),1e-30)),energy_error=abs(float(e)-er),directions=rows)
Path(__file__).with_name('failed_contact_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
