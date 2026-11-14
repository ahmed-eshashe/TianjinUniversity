"""Independent double-precision current-grid APIC reference.
Compatible state exchange mixes momentum only; stress and contact are then
applied by the adjoint of the same spatial interpolation used to move material.
"""
import numpy as np
from scipy.sparse import coo_matrix
from reference import stencil,energy_stress,couple
from material_connectivity import fragments

def kinetic(v,C,m,h):return float(.5*m*(np.sum(v*v)+h*h/4*np.sum(C*C)))
def momentum(x,v,C,m,h):
 spin=np.stack([C[:,2,1]-C[:,1,2],C[:,0,2]-C[:,2,0],C[:,1,0]-C[:,0,1]],axis=1)*h*h/4
 return m*v.sum(0),m*(np.cross(x,v)+spin).sum(0)
class APICReference:
 def __init__(self,X,spacing=.0015,h=.003,E=1e5,nu=.4,fixed=None):
  self.X=np.array(X,float);self.x=self.X.copy();self.v=np.zeros_like(X);self.C=np.zeros((len(X),3,3));self.F=np.tile(np.eye(3),(len(X),1,1));self.codes=np.zeros(len(X),int);self.h=h;self.spacing=spacing;self.mass=1000*spacing**3;self.vol=spacing**3;self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu));self.fixed=np.zeros(len(X),bool) if fixed is None else np.array(fixed,bool);self.sim_time=0.;self.steps=0
 def prepare(self,dt,force=None):
  self.dt=dt;self.oldx=self.x.copy();self.ids,self.w,self.g,self.grid=stencil(self.x,self.h);self.fragments,self.keys=fragments(self.X,self.codes,self.spacing);self.active,self.slot=np.unique(self.keys,return_inverse=True);self.K=len(self.active);self.N=len(self.grid);shape=(self.K,self.N);self.m=np.zeros(shape);p=np.zeros((*shape,3));f=np.zeros_like(p);r=self.grid[self.ids]-self.x[:,None,:];pv=self.v[:,None,:]+np.einsum('pij,pkj->pki',self.C,r);_,P=energy_stress(self.F,self.mu,self.lam);tau=P@self.F.transpose(0,2,1);a=np.repeat(self.slot,27);ids=self.ids.ravel();weighted=(self.mass*self.w).ravel()
  np.add.at(self.m,(a,ids),weighted);np.add.at(p,(a,ids),(self.mass*self.w[:,:,None]*pv).reshape(-1,3));np.add.at(f,(a,ids),(-self.vol*np.einsum('pij,pkj->pki',tau,self.g)).reshape(-1,3));self.E_particle_in=kinetic(self.v,self.C,self.mass,self.h);safe=np.where(self.m>0,self.m,1.)[:,:,None];self.E_p2g=float(.5*np.sum(p*p/safe));p,_=couple(self.m,p,np.zeros_like(p),self.active);self.E_coupled=float(.5*np.sum(p*p/safe));self.vg=(p+dt*f)/safe;self.inv=np.where(self.m.ravel()>0,1/np.maximum(self.m.ravel(),1e-300),0.)
  self.W=coo_matrix((self.w.ravel(),(np.repeat(np.arange(len(self.x)),27),(self.slot[:,None]*self.N+self.ids).ravel())),shape=(len(self.x),self.K*self.N)).tocsr();self.support_impulse=np.zeros(3);self.support_moment=np.zeros(3);self.support_loss=0.
  if force is not None:self.add_particle_impulse(dt*np.asarray(force))
  self.S=self.W[self.fixed];self.project_support()
  return self.W@self.vg.reshape(-1,3)
 def add_particle_impulse(self,J):
  self.vg+=((self.W.T@J)*self.inv[:,None]).reshape(self.vg.shape)
 def project_support(self):
  if not np.any(self.fixed):return
  H=self.S.multiply(self.inv)@self.S.T;H=H.toarray();val,vec=np.linalg.eigh(H);cut=max(val.max()*1e-12,1e-30);iv=np.zeros_like(val);np.divide(1.,val,out=iv,where=val>cut);self.Hpinv=(vec*iv)@vec.T;vv=self.vg.reshape(-1,3);old=vv.copy();lam=-self.Hpinv@(self.S@vv);J=self.S.T@lam;vv+=self.inv[:,None]*J;self.support_impulse+=J.sum(0);xx=np.tile(self.grid,(self.K,1));self.support_moment+=np.cross(xx,J).sum(0);self.support_loss+=float(.5*np.sum(self.m.ravel()[:,None]*(old*old-vv*vv)));self.support_residual=float(np.max(abs(self.S@vv)))
  if self.support_residual>1e-7:raise RuntimeError('support projection did not converge')
 def finish(self):
  z=self.vg[self.slot[:,None],self.ids];r=self.grid[self.ids]-self.oldx[:,None,:];self.v=np.sum(self.w[:,:,None]*z,axis=1);self.C=4/self.h**2*np.einsum('pk,pki,pkj->pij',self.w,z,r);L=np.einsum('pki,pkj->pij',z,self.g);self.x=self.oldx+self.dt*self.v;self.F=(np.eye(3)+self.dt*L)@self.F;self.sim_time+=self.dt;self.steps+=1
  self.E_grid_end=float(.5*np.sum(self.m[:,:,None]*self.vg**2));self.transfer_loss=(self.E_particle_in-self.E_p2g)+(self.E_p2g-self.E_coupled)+(self.E_grid_end-kinetic(self.v,self.C,self.mass,self.h));return self.state()
 def step(self,dt,force=None):self.prepare(dt,force);return self.finish()
 def state(self):return {k:getattr(self,k).copy() for k in ['X','x','v','C','F','codes']}
