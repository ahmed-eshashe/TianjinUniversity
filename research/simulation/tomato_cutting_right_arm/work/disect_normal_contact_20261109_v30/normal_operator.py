"""One-sided, embedded normal penalty solved in the velocity potential.

At frozen material coordinates and CAD normals, g(v)=phi+h*n.(Bv-vtool).
Psi(v)=sum(w*ke*min(g,0)^2)/(2h). Its velocity gradient is the
negative contact force; Hessian is positive semidefinite. No history.
"""
import torch

class NormalContact:
    def __init__(self, ids, u, normal, weights, phi, tool, h, ke, *, device='cuda'):
        self.ids=torch.as_tensor(ids,dtype=torch.long,device=device)
        cast=lambda x:torch.as_tensor(x,dtype=torch.float64,device=device)
        self.u=cast(u)[:,None];self.n=cast(normal);self.weights=cast(weights)
        self.phi=cast(phi);self.tool=cast(tool);self.h=float(h);self.ke=float(ke)
    def relative(self,v):
        return (((1-self.u)*v[self.ids[:,0]]+self.u*v[self.ids[:,1]]-self.tool)*self.n).sum(1)
    def gap(self,v):return self.phi+self.h*self.relative(v)
    def pull(self,f,v):
        out=torch.zeros_like(v)
        out.index_add_(0,self.ids[:,0],(1-self.u)*f)
        out.index_add_(0,self.ids[:,1],self.u*f)
        return out
    def apply(self,v):
        return self.pull((self.ke*self.weights*self.gap(v).clamp_max(0))[:,None]*self.n,v)
    def energy(self,v):return .5*self.ke/self.h*(self.weights*self.gap(v).clamp_max(0).square()).sum()
    def hessian(self,p,v):
        bp=(1-self.u)*p[self.ids[:,0]]+self.u*p[self.ids[:,1]]
        slope=self.ke*self.h*self.weights*(self.gap(v)<=0)
        return self.pull((slope*(bp*self.n).sum(1))[:,None]*self.n,p)
    def diagonal(self,v):
        slope=(self.ke*self.h*self.weights*(self.gap(v)<=0))[:,None]*self.n.square()
        out=torch.zeros_like(v)
        out.index_add_(0,self.ids[:,0],(1-self.u).square()*slope)
        out.index_add_(0,self.ids[:,1],self.u.square()*slope)
        same=self.ids[:,0]==self.ids[:,1]
        out.index_add_(0,self.ids[same,0],2*self.u[same]*(1-self.u[same])*slope[same])
        return out

class CombinedContact:
    def __init__(self,*operators):self.operators=[o for o in operators if o is not None]
    def apply(self,v):return sum((o.apply(v) for o in self.operators),torch.zeros_like(v))
    def energy(self,v):return sum((o.energy(v) for o in self.operators),v.new_tensor(0.))
    def hessian(self,p,v):return sum((o.hessian(p,v) for o in self.operators),torch.zeros_like(p))
    def diagonal(self,v):return sum((o.diagonal(v) for o in self.operators),torch.zeros_like(v))
