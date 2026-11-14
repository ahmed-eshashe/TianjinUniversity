"""Independent double-precision reference: fixed reference-grid TLMPM."""
import numpy as np
from itertools import product

def block(n=20,spacing=.003,offset=(0,0,0)):
 a=(np.arange(n)-(n-1)/2)*spacing
 return np.stack(np.meshgrid(a,a,a,indexing='ij'),axis=-1).reshape(-1,3)+offset

def stencil(X,h=.006):
 # Unbounded reference lattice, compacted without changing its coordinates.
 r=X/h;base=np.floor(r-.5).astype(int);f=r-base
 w=np.stack((.5*(1.5-f)**2,.75-(f-1)**2,.5*(f-.5)**2),axis=1)
 dw=np.stack((f-1.5,-2*(f-1),f-.5),axis=1)/h
 offsets=np.array(list(product(range(3),repeat=3)))
 nodes=base[:,None,:]+offsets[None,:,:]
 coords,inv=np.unique(nodes.reshape(-1,3),axis=0,return_inverse=True)
 weights=[];grads=[]
 for i,j,k in offsets:
  weights.append(w[:,i,0]*w[:,j,1]*w[:,k,2])
  grads.append(np.stack((dw[:,i,0]*w[:,j,1]*w[:,k,2],w[:,i,0]*dw[:,j,1]*w[:,k,2],w[:,i,0]*w[:,j,1]*dw[:,k,2]),axis=1))
 return inv.reshape(len(X),27),np.stack(weights,axis=1),np.stack(grads,axis=1),coords*h

def energy_stress(F,mu,lam):
 J=np.linalg.det(F)
 if np.any(J<=0):raise ValueError('inadmissible material volume')
 lj=np.log(J);invT=np.swapaxes(np.linalg.inv(F),-1,-2)
 P=mu*F+(lam*lj-mu)[...,None,None]*invT
 W=mu/2*((F*F).sum(axis=(-1,-2))-3)-mu*lj+lam/2*lj**2
 return W,P

def compatible(a,b):
 for k in range(4):
  x=(a//3**k)%3;y=(b//3**k)%3
  if x*y==2:return False
 return True

def couple(m,p,q,codes):
 # Direct independent pair exchange, antisymmetric additions.
 pp=p.copy();qq=q.copy();M=m.sum(axis=0);M=np.where(M>0,M,1.)
 for a in range(len(codes)):
  for b in range(a+1,len(codes)):
   if compatible(int(codes[a]),int(codes[b])):
    ex=(m[a,:,None]*p[b]-m[b,:,None]*p[a])/M[:,None]
    ei=(m[a,:,None]*q[b]-m[b,:,None]*q[a])/M[:,None]
    pp[a]+=ex;pp[b]-=ex;qq[a]+=ei;qq[b]-=ei
 return pp,qq

class Reference:
 def __init__(self,X,spacing=.003,h=.006,E=1e5,nu=.4):
  self.X=X.copy();self.x=X.copy();self.v=np.zeros_like(X);self.F=np.tile(np.eye(3),(len(X),1,1));self.codes=np.zeros(len(X),int)
  self.ids,self.w,self.g,self.grid=stencil(X,h);self.mass=1000*spacing**3;self.vol=spacing**3
  self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu))
 def step(self,dt):
  codes,slots=np.unique(self.codes,return_inverse=True);K=len(codes);N=len(self.grid)
  shape=(K,N);m=np.zeros(shape);p=np.zeros((*shape,3));q=p.copy();W,P=energy_stress(self.F,self.mu,self.lam)
  a=np.repeat(slots,27);i=self.ids.ravel();weighted=(self.mass*self.w).ravel()
  np.add.at(m,(a,i),weighted)
  np.add.at(p,(a,i),(self.mass*self.w[:,:,None]*self.v[:,None,:]).reshape(-1,3))
  np.add.at(q,(a,i),(-dt*self.vol*np.einsum('pij,pkj->pki',P,self.g)).reshape(-1,3))
  pp,qq=couple(m,p,q,codes);safe=np.where(m>0,m,1.)[:,:,None]
  v0=p/safe;v1=(pp+qq)/safe
  self.v+=(self.w[:,:,None]*(v1[slots[:,None],self.ids]-v0[slots[:,None],self.ids])).sum(axis=1)
  self.x+=dt*self.v
  remap=np.zeros_like(p);np.add.at(remap,(a,i),(self.mass*self.w[:,:,None]*self.v[:,None,:]).reshape(-1,3))
  rr,_=couple(m,remap,np.zeros_like(p),codes);vr=rr/safe
  self.F+=dt*np.einsum('pki,pkj->pij',vr[slots[:,None],self.ids],self.g)


def swept_codes(x,codes,cut,old,new,normal,edge,half_length,band):
 # Finite current swept rectangle, no path beyond the supplied endpoints.
 advance=np.asarray(new)-old;distance=np.linalg.norm(advance)
 if distance==0:return codes.copy()
 d=advance/distance;r=x-np.asarray(old);s=r@normal;ell=r@edge;t=r@d
 touched=(abs(s)<=band)&(abs(ell)<=half_length)&(t>=-1e-8)&(t<=distance+1e-8)&(((codes//3**cut)%3)==0)
 result=codes.copy();result[touched]+=np.where(s[touched]<0,1,2)*3**cut
 return result
