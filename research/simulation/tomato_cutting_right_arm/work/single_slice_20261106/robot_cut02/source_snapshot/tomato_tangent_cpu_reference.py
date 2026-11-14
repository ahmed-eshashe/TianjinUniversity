"""Independent CPU-autograd positive tensile-spring curvature reference."""
import numpy as np
import torch
import tomato_global_gn_cpu_reference as base
radial_action=base.reference_action

def reference_action(data):
 out,count=radial_action(data);x=data['x'];pairs=data['spring_pairs'];rest=data['spring_rest'];k=data['spring_k'];length=np.linalg.norm(x[pairs[:,1]]-x[pairs[:,0]],axis=1);active=length>rest;pairs=pairs[active];rest=rest[active];k=k[active];free=data['free'].astype(bool);vectors=data['vectors'].copy();vectors[:,~free]=0;positions=torch.tensor(x[pairs],dtype=torch.float64,requires_grad=True);rest_t=torch.tensor(rest,dtype=torch.float64);k_t=torch.tensor(k,dtype=torch.float64);normal=(x[pairs[:,1]]-x[pairs[:,0]])/length[active,None]
 def tensile_energy(q):
  gap=torch.linalg.vector_norm(q[:,1]-q[:,0],dim=1)-rest_t
  return .5*torch.sum(k_t*gap*gap)
 for i,v in enumerate(vectors):
  local=torch.tensor(v[pairs],dtype=torch.float64);_,action=torch.autograd.functional.hvp(tensile_energy,positions,local);full=action.detach().numpy();difference=v[pairs[:,0]]-v[pairs[:,1]];radial=k[:,None]*np.einsum('ni,ni->n',difference,normal)[:,None]*normal;extra=full-np.stack([radial,-radial],axis=1);extra[:,0]*=free[pairs[:,0],None];extra[:,1]*=free[pairs[:,1],None];np.add.at(out[i],pairs.ravel(),extra.reshape(-1,3))
 return out,count

if __name__=='__main__':
 base.reference_action=reference_action
 raise SystemExit(base.main())
