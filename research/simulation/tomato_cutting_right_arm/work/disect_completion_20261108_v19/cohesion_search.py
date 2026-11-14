"""Positive search curvature with current material frames held fixed.
Physical forces always retain their full moving-frame derivatives.
"""
import torch
class FrozenCohesion:
 def __init__(self,s,q):
  self.s=s
  with torch.no_grad():
   y=(q-s.offsett)@s.Qt;anchor=.5*((y[s.ai]+y[s.bi])*s.aw[:,:,:,None]).sum(2)
   u=anchor[:,1]-anchor[:,0];v=anchor[:,2]-anchor[:,0]
   n=s.sign[:,None]*torch.linalg.cross(u,v)/torch.linalg.vector_norm(torch.linalg.cross(u,v),dim=1)[:,None]
   t=u/torch.linalg.vector_norm(u,dim=1)[:,None];frame=torch.stack([n,t,torch.linalg.cross(n,t)],dim=2)
   gap=((y[s.ri]-y[s.li])*s.bary[:,:,None]).sum(1);local=torch.einsum('ni,nij->nj',gap,frame[s.group]);D=torch.ones_like(local);D[:,0]=(local[:,0]>=0)
   K=s.K[s.group]*D[:,:,None]*D[:,None,:];R=(s.Qt@frame)[s.group]
   self.K=s.weight[:,None,None]*(R@K@R.transpose(1,2))
 def action(self,u):
  s=self.s;gap=((u[s.ri]-u[s.li])*s.bary[:,:,None]).sum(1);f=torch.einsum('nij,nj->ni',self.K,gap)
  out=torch.zeros_like(u);nodal=(s.bary[:,:,None]*f[:,None,:]).reshape(-1,3)
  out.index_add_(0,s.ri.reshape(-1),nodal);out.index_add_(0,s.li.reshape(-1),-nodal);return out
