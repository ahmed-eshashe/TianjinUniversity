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
rng=np.random.default_rng(13);u=rng.normal(size=x.shape);u/=abs(u).max();rows=[]
checkpoint=np.load(Path(__file__).parent.parent/'disect_completion_20261108_v11/window20_trajectory.npz')
compressed=x.copy();compressed[np.unique(m['tets'][m['tet_side']==1]),0]-=1e-5
for label,xx in [('compressed',compressed),('saved6ms',checkpoint['x'][-1])]:
 with torch.enable_grad():
  q=tensor(xx).requires_grad_(True);graph=ContactGraph(c,q);e=graph.energy(q);g=torch.autograd.grad(e,q,create_graph=True)[0];hv=torch.autograd.grad(g,q,grad_outputs=tensor(u))[0].detach().cpu().numpy()
 graph.cache_hessian(q);cached=graph.action(tensor(u)).cpu().numpy();assert np.linalg.norm(cached-hv)/max(np.linalg.norm(hv),1e-30)<1e-10
 er,fr=c.energy_force_precise(xx);fd=-(c.energy_force_precise(xx+1e-10*u)[1]-c.energy_force_precise(xx-1e-10*u)[1])/(2e-10)
 row=dict(state=label,energy_error=abs(float(e)-er),force_relative=float(np.linalg.norm(g.detach().cpu().numpy()+fr)/max(np.linalg.norm(fr),1e-30)),hessian_action_relative=float(np.linalg.norm(hv-fd)/max(np.linalg.norm(fd),1e-30)),finite=bool(np.isfinite(hv).all()))
 rows.append(row)
out=dict(rows=rows,passed=all(r['finite'] and r['force_relative']<1e-5 and r['hessian_action_relative']<.01 for r in rows));Path(__file__).with_name('controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
