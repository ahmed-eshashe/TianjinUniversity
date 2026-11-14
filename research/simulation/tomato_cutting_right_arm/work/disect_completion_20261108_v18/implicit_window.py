import argparse
p=argparse.ArgumentParser();p.add_argument('--dt',type=float,required=True);p.add_argument('--duration',type=float,default=.02);p.add_argument('--name',required=True);args=p.parse_args()
from bulk_cache import BulkCache
from contact_energy import ContactGraph
import sys

from full_surface import FullSurface
from cohesive_transfer import W
from closure_runtime import Closure
from pathlib import Path
import sys,time,json,numpy as np
sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06/backend'))
from numerics import Bulk,load_arrays,tensor,torch
from torch.autograd import Function
torch.set_num_threads(1);s=FullSurface(device='cuda');c=Closure(s);m=s.mesh;x=m['x'];t=m['tets'];old=load_arrays();fixed=m['fixed'];mass=m['mass'];inv=1/mass;inv[fixed]=0
z=dict(x=x,tet_indices=t,tet_poses=np.linalg.inv((x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1)),physical_mass=mass,particle_inv_mass=inv,gravity=old['gravity'],contact_mask=np.ones(len(x)),fixed=fixed)
for key in ['tet_mu','tet_lambda','tet_damping','tet_activations']:
 assert np.all(old[key]==old[key][0]), 'Nonuniform material requires spatial transfer'
 z[key]=np.full(len(t),old[key][0])
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
# Constant deviatoric FEM block used only as a preconditioner.
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu
dm=z['tet_poses'];G=np.concatenate([-dm.sum(1)[:,None],dm],axis=1);weight=z['tet_damping']/(6*np.linalg.det(dm));local=weight[:,None,None]*(G@G.transpose(0,2,1));L=coo_matrix((local.ravel(),(np.broadcast_to(t[:,:,None],local.shape).ravel(),np.broadcast_to(t[:,None,:],local.shape).ravel())),shape=(len(x),len(x))).tocsc()
ff=np.flatnonzero(inv>0);ph=args.dt;factor=splu((diags(mass)+(ph+1200*ph*ph)*L)[ff][:,ff].tocsc())
h=args.dt;rows=[];snap=[];start=time.perf_counter();stop='completed';initial=np.linalg.det(x[t[:,1:]]-x[t[:,0]][:,None]);maxres=0.;free=b.free;mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'));A=tensor(mapping['rotation']);T=tensor(mapping['translation']);H=tensor(mapping['halfspaces'])
def sample(k):
 q,v=b.arrays();b.geometry();f=(b.f-b.damping(b.v)).cpu().numpy().copy()+s.evaluate(q)['force']+c.energy_force_precise(q)[1];ratio=np.linalg.det(q[t[:,1:]]-q[t[:,0]][:,None])/initial;row=dict(sim_s=k*h,volume_ratio_min=float(ratio.min()),speed_max_m_s=float(np.linalg.norm(v,axis=1).max()),force_residual_N=maxres,wall_s=time.perf_counter()-start);rows.append(row);snap.append((q,v,f));return bool(np.isfinite(q).all() and ratio.min()>.1 and q[:,1].min()>=-.0001 and np.max(abs(q[fixed]-x[fixed]))<=1e-7)
sample(0)
try:
 for step in range(1,round(args.duration/h)+1):
  b.geometry();xold=b.x.clone();vold=b.v.clone();world=xold@A.T+T;mask=torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1).to(torch.float64);limit=.2*(.001-xold[:,1]).clamp_min(0)*1000*mask;active=(xold[:,1]<.001).to(torch.float64)*mask;kf=1000*active;scale=free/torch.sqrt(b.mass/h**2+b.diag/h+b.diag*1200+1e-20);inertial=xold+h*vold+h*h*b.gravity
  def energy(q):
   delta=q-xold;ground=.5*1000*((.001-q[:,1]).clamp_min(0)**2*mask).sum();d=delta[:,[0,2]].abs();k=kf[:,None];lim=limit[:,None];friction=torch.where(k*d/h<=lim,.5*k*d*d/h,lim*d-.5*h*lim*lim/k.clamp_min(1)).sum()
   return (.5*b.mass*(q-inertial)**2/h**2).sum()+bulk_energy(q)+s.energies(q).sum()+ContactEnergy.apply(q)+ViscousEnergy.apply(delta,h)+ground+friction
  with torch.enable_grad():
   y=((h*vold)/scale.clamp_min(1e-20)).detach().requires_grad_(True);optimizer=torch.optim.LBFGS([y],lr=1.,max_iter=100,max_eval=150,tolerance_grad=1e-13,tolerance_change=1e-18,line_search_fn='strong_wolfe')
   def closure():
    optimizer.zero_grad();e=energy(xold+scale*y);e.backward();return e
   q=(xold+scale*y).detach().requires_grad_(True);g=torch.autograd.grad(energy(q),q)[0]*free;res=g.norm().item();maxres=max(maxres,res)
  from scipy.sparse.linalg import LinearOperator, gmres
  newton_log=[]
  for ni in range(12):
   with torch.enable_grad():
    q=q.detach().requires_grad_(True)
    delta=q-xold;d=delta[:,[0,2]].abs();k=kf[:,None];lim=limit[:,None]
    smooth=(.5*b.mass*(q-inertial)**2/h**2).sum()+s.energies(q).sum()+.5*1000*((.001-q[:,1]).clamp_min(0)**2*mask).sum()+torch.where(k*d/h<=lim,.5*k*d*d/h,lim*d-.5*h*lim*lim/k.clamp_min(1)).sum()
    gs=torch.autograd.grad(smooth,q,create_graph=True)[0]
    gc=torch.autograd.grad(energy(q),q)[0];res=(gc*free).norm().item()
   newton_log.append(dict(iteration=ni,residual=res))
   if res<=1e-6:break
   material_cache=BulkCache(b,q,V,alpha)
   ce,cf=c.energy_force_precise(q.detach().cpu().numpy())
   contact_diag=np.maximum(np.diagonal(c.engine.physical_hessian.numpy(),axis1=1,axis2=2),0.)
   contact_factors=[splu((diags(mass+h*h*contact_diag[:,axis])+(h+1200*h*h)*L)[ff][:,ff].tocsc()) for axis in range(3)]
   with torch.enable_grad():
    graph=ContactGraph(c,q);graph.cache_hessian(q)
   base=q.detach().cpu().numpy().copy()
   def mv(v):
    u=tensor(v.reshape(x.shape))*scale
    with torch.enable_grad(): hv=torch.autograd.grad(gs,q,grad_outputs=u,retain_graph=True)[0]+material_cache.action(u)
    hc=graph.action(u)
    return ((hv+b.damping(u).clone()/h+hc)*scale).detach().cpu().numpy().ravel()
   rhs=-(gc*scale).detach().cpu().numpy().ravel();counter=[0]
   def counted(v):counter[0]+=1;return mv(v)
   sn=scale.detach().cpu().numpy();safe=np.where(sn!=0,sn,1.)
   def precondition(v):
    rhs0=v.reshape(x.shape)/safe;ans=np.zeros_like(rhs0);
    for axis in range(3):ans[ff,axis]=h*h*contact_factors[axis].solve(rhs0[ff,axis])
    return (ans/safe).ravel()
   pre=LinearOperator((rhs.size,rhs.size),matvec=precondition,dtype=np.float64)
   stepvec,info=gmres(LinearOperator((rhs.size,rhs.size),matvec=counted,dtype=np.float64),rhs,M=pre,rtol=1e-3,atol=1e-14,restart=80,maxiter=4)
   newton_log[-1].update(cg_info=int(info),matvecs=counter[0])
   Path(__file__).with_name(args.name+'_linear_progress.json').write_text(json.dumps(dict(step=step,iterations=newton_log),indent=2))
   actual_linear=float(np.linalg.norm(mv(stepvec)-rhs)/max(np.linalg.norm(rhs),1e-30))
   newton_log[-1]['true_linear_relative_residual']=actual_linear
   if not np.isfinite(actual_linear) or actual_linear>.1 or float(np.dot(stepvec,rhs))<=0:raise RuntimeError(f'Inexact Newton direction rejected: {actual_linear}')
   dq=tensor(stepvec.reshape(x.shape))*scale;oldenergy=float(energy(q));slope=float((gc*dq).sum());rate=1.
   for ls in range(20):
    candidate=q.detach()+rate*dq
    if float(energy(candidate))<=oldenergy+1e-4*rate*slope:break
    rate*=.5
   else:raise RuntimeError('Newton line search failed')
   q=candidate.detach()
  print('NEWTON',json.dumps(newton_log),flush=True)
  Path(__file__).with_name(args.name+'_iterations.json').write_text(json.dumps(newton_log,indent=2))
  maxres=max([res]+[r["force_residual_N"] for r in rows])
  if not np.isfinite(res) or res>1e-6:stop=f'nonlinear_force_residual {res}';break
  b.x.copy_(q.detach());b.v.copy_((b.x-xold)/h)
  if not sample(step):stop='physical_stop';break
  if time.perf_counter()-start>600:stop='wall_cap';break
except Exception as e:stop=repr(e)
np.savez_compressed(Path(__file__).with_name(args.name+'_trajectory.npz'),t=np.array([r['sim_s'] for r in rows]),x=np.array([a[0] for a in snap]),v=np.array([a[1] for a in snap]),force=np.array([a[2] for a in snap]))
out=dict(scope='Bounded coupled implicit numerical candidate; unchanged material laws, lagged viscous geometry and friction normal',bulk_energy_force_max_error_N=bulkerr,stop=stop,dt_s=h,wall_s=time.perf_counter()-start,max_force_residual_N=maxres,rows=rows,component_passed=bool(stop=='completed'))
Path(__file__).with_name(args.name+'_result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
