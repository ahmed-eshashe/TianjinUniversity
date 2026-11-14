"""Implicit one-sided normal damping with exact material embedding pullback."""
import torch

class EmbeddedDashpot:
    def __init__(self, ids, u, normal, coefficient, tool_velocity, tensor):
        self.ids=torch.as_tensor(ids,dtype=torch.long,device='cuda')
        self.u=tensor(u)[:,None];self.n=tensor(normal)
        self.k=tensor(coefficient);self.tool=tensor(tool_velocity)

    def project(self,v):
        vv=(1-self.u)*v[self.ids[:,0]]+self.u*v[self.ids[:,1]]
        return ((vv-self.tool)*self.n).sum(1)

    def pull(self,f,n):
        out=torch.zeros((n,3),dtype=f.dtype,device=f.device)
        out.index_add_(0,self.ids[:,0],(1-self.u)*f)
        out.index_add_(0,self.ids[:,1],self.u*f)
        return out

    def apply(self,v):
        return self.pull((self.k*torch.minimum(self.project(v),torch.zeros_like(self.k)))[:,None]*self.n,len(v))

    def energy(self,v):
        vn=torch.minimum(self.project(v),torch.zeros_like(self.k))
        return .5*(self.k*vn*vn).sum()

    def hessian(self,p,v):
        vv=(1-self.u)*p[self.ids[:,0]]+self.u*p[self.ids[:,1]]
        slope=self.k*(self.project(v)<=0)
        return self.pull((slope*(vv*self.n).sum(1))[:,None]*self.n,len(p))

    def diagonal(self,v):
        slope=(self.k*(self.project(v)<=0))[:,None]*self.n.square()
        out=torch.zeros_like(v)
        out.index_add_(0,self.ids[:,0],(1-self.u).square()*slope)
        out.index_add_(0,self.ids[:,1],self.u.square()*slope)
        # i=j is a genuine nodal sample: include the two cross terms.
        same=self.ids[:,0]==self.ids[:,1]
        out.index_add_(0,self.ids[same,0],2*self.u[same]*(1-self.u[same])*slope[same])
        return out
