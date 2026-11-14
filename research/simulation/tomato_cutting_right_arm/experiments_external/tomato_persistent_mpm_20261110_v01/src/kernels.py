"""New CUDA kernels; no existing simulator code is modified."""
import warp as wp
@wp.func
def stress(F:wp.mat33,mu:float,lam:float):
 J=wp.determinant(F)
 return mu*F+(lam*wp.log(J)-mu)*wp.transpose(wp.inverse(F))

@wp.kernel
def constitutive(F:wp.array(dtype=wp.mat33),mu:float,lam:float,P:wp.array(dtype=wp.mat33),W:wp.array(dtype=float)):
 p=wp.tid();f=F[p];j=wp.determinant(f);P[p]=stress(f,mu,lam)
 norm= float(0.0)
 for a in range(3):
  for b in range(3):norm+=f[a,b]*f[a,b]
 lj=wp.log(j);W[p]=mu*.5*(norm-3.0)-mu*lj+lam*.5*lj*lj

@wp.func
def compatible(a:int,b:int):
 good=True
 for k in range(4):
  x=a%3;y=b%3
  if x*y==2:good=False
  a=a//3;b=b//3
 return good

@wp.kernel
def clear_grid(m:wp.array2d(dtype=float),p:wp.array2d(dtype=wp.vec3),q:wp.array2d(dtype=wp.vec3),r:wp.array2d(dtype=wp.vec3)):
 a,i=wp.tid();m[a,i]=0.0;p[a,i]=wp.vec3(0.0);q[a,i]=wp.vec3(0.0);r[a,i]=wp.vec3(0.0)

@wp.kernel
def p2g(v:wp.array(dtype=wp.vec3),F:wp.array(dtype=wp.mat33),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),g:wp.array2d(dtype=wp.vec3),mass:float,vol:float,mu:float,lam:float,dt:float,m:wp.array2d(dtype=float),p:wp.array2d(dtype=wp.vec3),q:wp.array2d(dtype=wp.vec3),bad:wp.array(dtype=int)):
 k=wp.tid();a=lookup[codes[k]];j=wp.determinant(F[k])
 if j<0.1 or j>10.0 or not wp.isfinite(j):
  wp.atomic_add(bad,0,1)
 else:
  P=stress(F[k],mu,lam)
  for s in range(27):
   i=ids[k,s];wm=mass*w[k,s]
   wp.atomic_add(m,a,i,wm);wp.atomic_add(p,a,i,wm*v[k]);wp.atomic_add(q,a,i,-dt*vol*(P*g[k,s]))

@wp.kernel
def grid_update(m:wp.array2d(dtype=float),p:wp.array2d(dtype=wp.vec3),q:wp.array2d(dtype=wp.vec3),active:wp.array(dtype=int),count:int,v0:wp.array2d(dtype=wp.vec3),v1:wp.array2d(dtype=wp.vec3)):
 a,i=wp.tid();ma=m[a,i];pa=p[a,i];qa=q[a,i];M=float(0.0)
 for b in range(count):M+=m[b,i]
 v0[a,i]=wp.vec3(0.0);v1[a,i]=wp.vec3(0.0)
 if ma>0.0:
  dp=wp.vec3(0.0);dq=wp.vec3(0.0)
  for b in range(count):
   if b!=a and compatible(active[a],active[b]):
    dp+=ma*p[b,i]-m[b,i]*pa;dq+=ma*q[b,i]-m[b,i]*qa
  v0[a,i]=pa/ma;v1[a,i]=(pa+qa+(dp+dq)/M)/ma

@wp.kernel
def g2p(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),v0:wp.array2d(dtype=wp.vec3),v1:wp.array2d(dtype=wp.vec3),dt:float):
 p=wp.tid();a=lookup[codes[p]];dv=wp.vec3(0.0)
 for k in range(27):
  i=ids[p,k];dv+=w[p,k]*(v1[a,i]-v0[a,i])
 v[p]=v[p]+dv;x[p]=x[p]+dt*v[p]

@wp.kernel
def remap(v:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),mass:float,r:wp.array2d(dtype=wp.vec3)):
 p=wp.tid();a=lookup[codes[p]]
 for k in range(27):wp.atomic_add(r,a,ids[p,k],mass*w[p,k]*v[p])

@wp.kernel
def remap_couple(m:wp.array2d(dtype=float),r:wp.array2d(dtype=wp.vec3),active:wp.array(dtype=int),count:int,vr:wp.array2d(dtype=wp.vec3)):
 a,i=wp.tid();ma=m[a,i];ra=r[a,i];M=float(0.0)
 for b in range(count):M+=m[b,i]
 vr[a,i]=wp.vec3(0.0)
 if ma>0.0:
  dp=wp.vec3(0.0)
  for b in range(count):
   if b!=a and compatible(active[a],active[b]):dp+=ma*r[b,i]-m[b,i]*ra
  vr[a,i]=(ra+dp/M)/ma

@wp.kernel
def deform(F:wp.array(dtype=wp.mat33),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),g:wp.array2d(dtype=wp.vec3),vr:wp.array2d(dtype=wp.vec3),dt:float):
 p=wp.tid();a=lookup[codes[p]];L=wp.mat33(0.0)
 for k in range(27):L+=wp.outer(vr[a,ids[p,k]],g[p,k])
 F[p]=F[p]+dt*L

@wp.kernel
def assign_sweep(x:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),old:wp.vec3,new:wp.vec3,normal:wp.vec3,edge:wp.vec3,half_length:float,band:float,power:int):
 p=wp.tid();advance=new-old;dist=wp.length(advance)
 if dist>0.0 and (codes[p]//power)%3==0:
  r=x[p]-old;d=advance/dist;s=wp.dot(r,normal);ell=wp.dot(r,edge);t=wp.dot(r,d)
  if wp.abs(s)<=band and wp.abs(ell)<=half_length and t>=-1e-8 and t<=dist+1e-8:
   digit=int(2)
   if s<0.0:digit=1
   codes[p]=codes[p]+digit*power
