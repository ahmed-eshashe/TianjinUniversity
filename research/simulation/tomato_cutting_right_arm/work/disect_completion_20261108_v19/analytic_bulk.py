"""Analytic Hessian of the unchanged corrected Stable Neo-Hookean energy."""
import torch
class BulkCache:
 def __init__(self,b,q,V,alpha):
  self.t=b.t
  with torch.no_grad():
   D=(q[b.t[:,1:]]-q[b.t[:,0,None]]).transpose(1,2);F=D@b.dm
   I=(F*F).sum((1,2));J=torch.linalg.det(F)
   cof=torch.stack([torch.linalg.cross(F[:,:,1],F[:,:,2]),torch.linalg.cross(F[:,:,2],F[:,:,0]),torch.linalg.cross(F[:,:,0],F[:,:,1])],dim=2)
   g=torch.cat([-b.dm.sum(1)[:,None],b.dm],dim=1)
   fg=torch.einsum('eab,eib->eia',F,g);cg=torch.einsum('eab,eib->eia',cof,g)
   dot=torch.einsum('eia,eja->eij',g,g)
   h=(b.mu*(1-1/(I+1)))[:,None,None,None,None]*dot[:,:,:,None,None]*torch.eye(3,device=q.device,dtype=q.dtype)
   h=h+(2*b.mu/(I+1)**2)[:,None,None,None,None]*fg[:,:,None,:,None]*fg[:,None,:,None,:]
   h=h+b.la[:,None,None,None,None]*cg[:,:,None,:,None]*cg[:,None,:,None,:]
   cross=torch.linalg.cross(g[:,:,None,:].expand(-1,-1,4,-1),g[:,None,:,:].expand(-1,4,-1,-1))
   v=torch.einsum('eab,eijb->eija',F,cross);zero=torch.zeros_like(v[...,0]);a,c,d=v.unbind(-1)
   skew=torch.stack([zero,-d,c,d,zero,-a,-c,a,zero],-1).reshape(-1,4,4,3,3)
   h=h-(b.la*(J-alpha))[:,None,None,None,None]*skew
   self.h=(V[:,None,None,None,None]*h).permute(0,1,3,2,4).reshape(-1,12,12)
 def action(self,u):
  local=u[self.t].reshape(-1,12);out=torch.einsum('nij,nj->ni',self.h,local).reshape(-1,3);r=torch.zeros_like(u);r.index_add_(0,self.t.reshape(-1),out);return r
