"""Experimental objective mixed-mode interface reference, version 0.1.

CPU float64 automatic derivatives include moving-frame forces on frame nodes.
This is an additive model candidate, not the qualified native cutting solver.
No friction, unilateral closure solver or experimental parameter fit is implied.
"""
import itertools
import numpy as np
import torch

def make_patch(reference_pairs,weights,stiffness,law):
 x=np.asarray(reference_pairs,dtype=float);w=np.asarray(weights,dtype=float);k=np.asarray(stiffness,dtype=float)
 if x.ndim!=3 or x.shape[1:]!=(2,3) or not 3<=len(x)<=8 or w.shape!=(len(x),) or np.any(w<=0) or abs(w.sum()-1)>1e-10 or not np.isfinite(x).all() or np.max(np.linalg.norm(x[:,1]-x[:,0],axis=1))>1e-12:raise ValueError('Coincident, finite paired reference surface and positive normalized weights required')
 if k.shape!=(3,3) or not np.allclose(k,k.T) or np.linalg.eigvalsh(k).min()<=0 or np.any(k[0,1:]!=0):raise ValueError('SPD uncoupled normal/tangential stiffness required')
 mid=x.mean(1);triplets=list(itertools.combinations(range(len(x)),3));anchor=max(triplets,key=lambda t:np.linalg.norm(np.cross(mid[t[1]]-mid[t[0]],mid[t[2]]-mid[t[0]])))
 u=mid[anchor[1]]-mid[anchor[0]];v=mid[anchor[2]]-mid[anchor[0]];cross=np.cross(u,v)
 if np.linalg.norm(cross)<1e-12:raise ValueError('Nondegenerate material frame required')
 sign=1. if cross[0]>0 else -1.;t=u/np.linalg.norm(u);n=sign*cross/np.linalg.norm(cross);q=np.column_stack([n,t,np.cross(n,t)])
 if abs(n[0]-1)>1e-8:raise ValueError('Reference surface must align with saved X-normal interface')
 a,b,kn=law
 if not 0<a<b or kn<=0:raise ValueError('Valid bilinear law required')
 return dict(reference=x,weights=w,local_k=q.T@k@q,anchors=anchor,sign=sign,onset=a,failure=b,kn=kn)

def _energy(x,patch):
 mid=x.mean(dim=1);a,b,c=patch['anchors'];u=mid[b]-mid[a];v=mid[c]-mid[a];cross=torch.linalg.cross(u,v)
 if torch.linalg.vector_norm(cross).detach().item()<1e-12:raise ValueError('Collapsed moving material frame')
 tangent=u/torch.linalg.vector_norm(u);normal=patch['sign']*cross/torch.linalg.vector_norm(cross);q=torch.stack([normal,tangent,torch.linalg.cross(normal,tangent)],dim=1)
 gap=(x[:,1]-x[:,0])@q;eff=torch.cat([torch.clamp(gap[:,:1],min=0),gap[:,1:]],dim=1)
 w=torch.as_tensor(patch['weights'],dtype=torch.float64);k=torch.as_tensor(patch['local_k'],dtype=torch.float64)
 return .5*torch.sum(w[:,None]*eff*(eff@k))

def response(positions,patch,*,history=(0.,0.),eligible=False,tangent=False):
 if type(eligible)is not bool or len(history)!=2 or not np.isfinite(history).all() or history[0]<0 or not 0<=history[1]<=1:raise ValueError('Explicit eligibility and valid committed history required')
 expected=0. if history[0]<=patch['onset'] else 1. if history[0]>=patch['failure'] else patch['failure']*(history[0]-patch['onset'])/(history[0]*(patch['failure']-patch['onset']))
 if abs(history[1]-expected)>1e-10:raise ValueError('Committed history must lie on the same irreversible bilinear law')
 x=torch.tensor(np.asarray(positions),dtype=torch.float64,requires_grad=True)
 if x.shape!=patch['reference'].shape or not torch.isfinite(x).all():raise ValueError('Finite paired positions required')
 def force_tensor(y):
  energy=_energy(y,patch);gradient=torch.autograd.grad(energy,y,create_graph=True)[0];q=torch.sqrt(torch.clamp(2*energy/patch['kn'],min=1e-40));d=torch.tensor(history[1],dtype=torch.float64)
  if eligible and q.detach().item()>=history[0]:
   if q.detach().item()>=patch['failure']:d=d*0+1
   elif q.detach().item()>patch['onset']:
    candidate=patch['failure']*(q-patch['onset'])/(q*(patch['failure']-patch['onset']));d=torch.maximum(d,candidate)
  return -(1-d)*gradient,d,q,energy
 f,d,q,u=force_tensor(x);maximum=max(history[0],q.item()) if eligible else history[0]
 diss=lambda t:.5*patch['kn']*patch['onset']*patch['failure']/(patch['failure']-patch['onset'])*(min(patch['failure'],max(patch['onset'],t))-patch['onset'])
 result=dict(force_n=f.detach().numpy(),stored_energy_j=(1-d.item())*u.item(),incremental_potential_j=(1-d.item())*u.item()+diss(maximum)-diss(history[0]),undamaged_energy_j=u.item(),equivalent_separation_m=q.item(),trial_history=(maximum,d.item()),native_runtime_validated=False)
 if tangent:result['force_jacobian_n_m']=torch.autograd.functional.jacobian(lambda y:force_tensor(y)[0],x).detach().numpy().reshape(x.numel(),x.numel())
 return result
