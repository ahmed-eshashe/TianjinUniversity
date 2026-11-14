"""Reference-coordinate Galerkin mechanics with particle quadrature and full mass.
Intact mechanics probe only: cut topology is deliberately unsupported here.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from reference import stencil,energy_stress
class ConsistentReference:
 def __init__(self,X,spacing=.0015,h=.003,E=1e5,nu=.4,fixed=None):
  self.X=np.array(X,float);self.h=h;self.spacing=spacing;self.mass=1000*spacing**3;self.vol=spacing**3;self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu));self.ids,self.weights,self.grads,self.grid=stencil(self.X,h);self.n=len(X);self.ng=len(self.grid);self.q=self.grid.copy();self.vg=np.zeros_like(self.grid);self.fixed=np.zeros(self.n,bool) if fixed is None else np.asarray(fixed,bool);r=np.repeat(np.arange(self.n),27);c=self.ids.ravel()
  self.W=coo_matrix((self.weights.ravel(),(r,c)),shape=(self.n,self.ng)).tocsr();self.G=[coo_matrix((self.grads[:,:,j].ravel(),(r,c)),shape=self.W.shape).tocsr() for j in range(3)];self.M=(self.mass*(self.W.T@self.W)).tocsc();self.factor=splu(self.M)
  self.S=self.W[self.fixed];self.Z=self.factor.solve(self.S.T.toarray()) if self.S.shape[0] else None
  if self.Z is not None:
   H=self.S@self.Z;d,U=np.linalg.eigh(H);iv=np.zeros_like(d);np.divide(1,d,out=iv,where=d>max(d.max()*1e-12,1e-30));self.Hinv=(U*iv)@U.T
  self.time=0.;self.steps=0;self.initial_filter_loss=0.;self.support_impulse=np.zeros(3);self.support_moment=np.zeros(3);self.update_state()
 def update_state(self):
  self.x=self.W@self.q;self.v=self.W@self.vg;self.F=np.stack([g@self.q for g in self.G],axis=2)
  if not np.isfinite(self.F).all() or np.linalg.det(self.F).min()<=.1 or np.linalg.det(self.F).max()>=10:raise RuntimeError('inadmissible material volume')
 def initialize(self,F=None,velocity=None,affine_velocity=None):
  if F is not None:self.q=self.grid@np.asarray(F).T
  if affine_velocity is not None:self.vg=self.q@np.asarray(affine_velocity).T
  if velocity is not None:
   v=np.asarray(velocity);self.vg=self.factor.solve(self.mass*(self.W.T@v));pv=self.W@self.vg;self.initial_filter_loss=float(.5*self.mass*(np.sum(v*v)-np.sum(pv*pv)))
  self.update_state()
 def energy_force(self,q):
  F=np.stack([g@q for g in self.G],axis=2);J=np.linalg.det(F)
  if J.min()<=.1 or J.max()>=10:raise RuntimeError('inadmissible trial volume')
  e,P=energy_stress(F,self.mu,self.lam);f=-self.vol*sum(g.T@P[:,:,j] for j,g in enumerate(self.G));return float(self.vol*e.sum()),f
 def acceleration(self,q,external=None):
  _,f=self.energy_force(q)
  if external is not None:f+=self.W.T@external
  a=self.factor.solve(f);reaction=np.zeros_like(f)
  if self.Z is not None:
   lam=-self.Hinv@(self.S@a);a+=self.Z@lam;reaction=self.S.T@lam
   if abs(self.S@a).max()>1e-6:raise RuntimeError('support acceleration residual')
  residual=np.linalg.norm(self.M@a-f-reaction)/max(np.linalg.norm(f+reaction),1e-12)
  if residual>1e-7:raise RuntimeError(f'consistent mass residual {residual}')
  return a,reaction
 def step(self,dt,force0=None,force1=None):
  a,r0=self.acceleration(self.q,force0);vh=self.vg+.5*dt*a;qn=self.q+dt*vh;a1,r1=self.acceleration(qn,force1 if force1 is not None else force0);self.support_impulse+=.5*dt*(r0+r1).sum(0);self.support_moment+=.5*dt*(np.cross(self.q,r0).sum(0)+np.cross(qn,r1).sum(0));self.q=qn;self.vg=vh+.5*dt*a1;self.time+=dt;self.steps+=1;self.update_state()
 def metrics(self):
  U,_=self.energy_force(self.q);T=float(.5*self.mass*np.sum(self.v*self.v));return {'energy':T+U,'strain_energy':U,'kinetic_energy':T,'momentum':self.mass*self.v.sum(0),'angular':self.mass*np.cross(self.x,self.v).sum(0)}
 def save(self,path):np.savez_compressed(path,X=self.X,x=self.x,v=self.v,F=self.F,q=self.q,vg=self.vg,grid=self.grid,sim_time=self.time,steps=self.steps,initial_filter_loss=self.initial_filter_loss)
