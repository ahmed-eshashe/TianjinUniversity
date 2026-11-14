"""Compiled bookkeeping and accounting; float64, no fast-math or cutoffs."""
import numpy as np
from numba import njit

@njit(cache=True,nogil=True)
def compatible(a,b):
 for k in range(4):
  if (a%3)*(b%3)==2:return False
  a//=3;b//=3
 return True

@njit(cache=True,nogil=True)
def labels(oldids,codes,nold):
 active=np.zeros((nold,81),np.uint8)
 for p in range(len(codes)):
  for k in range(4):active[oldids[p,k],codes[p]]=1
 mapping=np.full((nold,81),-1,np.int64);parents=np.empty(nold*81,np.int64);nn=0
 for a in range(nold):
  found=False
  for c in range(81):
   if active[a,c] and mapping[a,c]<0:
    found=True;stack=np.empty(81,np.int64);stack[0]=c;top=1;mapping[a,c]=nn;parents[nn]=a
    while top:
     top-=1;i=stack[top]
     for j in range(81):
      if active[a,j] and mapping[a,j]<0 and compatible(i,j):mapping[a,j]=nn;stack[top]=j;top+=1
    nn+=1
  if not found:raise ValueError('orphaned reference node')
 out=np.empty_like(oldids)
 for p in range(len(codes)):
  for k in range(4):out[p,k]=mapping[oldids[p,k],codes[p]]
 return out,parents[:nn]

@njit(cache=True,nogil=True)
def fields(ids,G,N,X,u,v):
 x=X.copy();velocity=np.zeros_like(x);F=np.zeros((len(ids),3,3))
 for p in range(len(ids)):
  for i in range(3):
   F[p,i,i]=1.
   for k in range(4):x[p,i]+=N[p,k]*u[ids[p,k],i];velocity[p,i]+=N[p,k]*v[ids[p,k],i]
   for j in range(3):
    for k in range(1,4):F[p,i,j]+=(u[ids[p,k],i]-u[ids[p,0],i])*G[p,k,j]
 return x,velocity,F

@njit(inline='always')
def F_values(ids,G,u,p):
 f00=1.;f01=0.;f02=0.;f10=0.;f11=1.;f12=0.;f20=0.;f21=0.;f22=1.
 a0=ids[p,0]
 for k in range(1,4):
  a=ids[p,k];dx=u[a,0]-u[a0,0];dy=u[a,1]-u[a0,1];dz=u[a,2]-u[a0,2]
  gx=G[p,k,0];gy=G[p,k,1];gz=G[p,k,2]
  f00+=dx*gx;f01+=dx*gy;f02+=dx*gz;f10+=dy*gx;f11+=dy*gy;f12+=dy*gz;f20+=dz*gx;f21+=dz*gy;f22+=dz*gz
 return f00,f01,f02,f10,f11,f12,f20,f21,f22

@njit(cache=True,nogil=True)
def metrics(ids,G,V,grid,mass,u,v,mu,lam):
 U=0.;T=0.;px=0.;py=0.;pz=0.;lx=0.;ly=0.;lz=0.
 for p in range(len(ids)):
  a,b,c,d,e,f,g,h,i=F_values(ids,G,u,p)
  J=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
  if not np.isfinite(J) or J<=.1 or J>=10:raise ValueError('inadmissible material volume')
  norm=a*a+b*b+c*c+d*d+e*e+f*f+g*g+h*h+i*i
  l=np.log(J);U+=V[p]*(.5*mu*(norm-3)-mu*l+.5*lam*l*l)
 for a in range(len(mass)):
  x=grid[a,0]+u[a,0];y=grid[a,1]+u[a,1];z=grid[a,2]+u[a,2];vx=v[a,0];vy=v[a,1];vz=v[a,2]
  mx=mass[a]*vx;my=mass[a]*vy;mz=mass[a]*vz
  px+=mx;py+=my;pz+=mz;T+=.5*mass[a]*(vx*vx+vy*vy+vz*vz)
  lx+=y*mz-z*my;ly+=z*mx-x*mz;lz+=x*my-y*mx
 return U,T,np.array([px,py,pz]),np.array([lx,ly,lz])

@njit(cache=True,nogil=True)
def volume_valid(ids,G,u):
 for p in range(len(ids)):
  a,b,c,d,e,f,g,h,i=F_values(ids,G,u,p);J=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
  if not np.isfinite(J) or J<=.1 or J>=10:return False
 return True

@njit(cache=True,nogil=True)
def full_flags(ptr,vertices,grid,ids):
 full=np.zeros(len(ids),np.bool_)
 for p in range(len(ids)):
  if ptr[p+1]-ptr[p]!=4:continue
  maximum=0.
  for i in range(ptr[p],ptr[p+1]):
   minimum=1e300
   for k in range(4):
    a=ids[p,k];dx=vertices[i,0]-grid[a,0];dy=vertices[i,1]-grid[a,1];dz=vertices[i,2]-grid[a,2]
    minimum=min(minimum,np.sqrt(dx*dx+dy*dy+dz*dz))
   maximum=max(maximum,minimum)
  full[p]=maximum<1e-14
 return full

@njit(cache=True,nogil=True)
def vertex_values(ptr,vertices,inv,ids,u,v):
 x=vertices.copy();vel=np.zeros_like(x)
 for p in range(len(ids)):
  for t in range(ptr[p],ptr[p+1]):
   for k in range(4):
    w=inv[p,0,k]
    for j in range(3):w+=vertices[t,j]*inv[p,j+1,k]
    for j in range(3):x[t,j]+=w*u[ids[p,k],j];vel[t,j]+=w*v[ids[p,k],j]
 return x,vel

@njit(cache=True,nogil=True)
def select_roots(ids,codes,grid,X,full,pcomp,ncomp,stable,maxdistance):
 incident=np.zeros((len(grid),81),np.uint8)
 for p in range(len(ids)):
  for k in range(4):incident[ids[p,k],codes[p]]=1
 chosen=np.full(len(grid),-1,np.int64);distances=np.zeros(len(grid))
 for a in range(len(grid)):
  if stable[a]:continue
  best=1e300;root=-1
  for p in range(len(ids)):
   if not full[p] or pcomp[p]!=ncomp[a]:continue
   good=True
   for c in range(81):
    if incident[a,c] and not compatible(c,codes[p]):good=False;break
   if not good:continue
   dx=X[p,0]-grid[a,0];dy=X[p,1]-grid[a,1];dz=X[p,2]-grid[a,2];d=np.sqrt(dx*dx+dy*dy+dz*dz)
   if d<best:best=d;root=p
  if best<=maxdistance:chosen[a]=root;distances[a]=best
 return chosen,distances
