import torch
class BulkCache:
 def __init__(self,b,q,V,alpha):
  self.t=b.t
  with torch.enable_grad():
   local=q.detach()[b.t].requires_grad_(True);D=(local[:,1:]-local[:,0,None]).transpose(1,2);F=D@b.dm;I=(F*F).sum((1,2));J=torch.linalg.det(F)
   e=(V*(.5*b.mu*(I-3-torch.log((I+1)/4))+.5*b.la*((J-alpha)**2-(1-alpha)**2))).sum()
   g=torch.autograd.grad(e,local,create_graph=True)[0].reshape(-1,12)
   self.h=torch.stack([torch.autograd.grad(g[:,j].sum(),local,retain_graph=True)[0].reshape(-1,12).detach() for j in range(12)],1)
 def action(self,u):
  local=u[self.t].reshape(-1,12);out=torch.einsum('nij,nj->ni',self.h,local).reshape(-1,3);r=torch.zeros_like(u);r.index_add_(0,self.t.reshape(-1),out);return r
