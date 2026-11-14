import warp as wp
@wp.func
def basis(i:int,x:wp.float64):
 r=wp.float64(0.0)
 if i==0:r=wp.float64(.5)*(wp.float64(1.5)-x)*(wp.float64(1.5)-x)
 elif i==1:r=wp.float64(.75)-(x-wp.float64(1.0))*(x-wp.float64(1.0))
 else:r=wp.float64(.5)*(x-wp.float64(.5))*(x-wp.float64(.5))
 return r
@wp.func
def dbasis(i:int,x:wp.float64):
 r=wp.float64(0.0)
 if i==0:r=x-wp.float64(1.5)
 elif i==1:r=-wp.float64(2.0)*(x-wp.float64(1.0))
 else:r=x-wp.float64(.5)
 return r
@wp.func
def compatible(a:int,b:int):
 good=a//81==b//81
 a=a%81;b=b%81
 for j in range(4):
  x=a%3;y=b%3
  if x*y==2:good=False
  a=a//3;b=b//3
 return good
@wp.kernel
def stencil_current(x:wp.array(dtype=wp.vec3d),h:wp.float64,origin:wp.vec3i,dims:wp.vec3i,ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),r:wp.array2d(dtype=wp.vec3d),bad:wp.array(dtype=int)):
 p=wp.tid();z=x[p]/h;base=wp.vec3i(int(wp.floor(z[0]-wp.float64(.5))),int(wp.floor(z[1]-wp.float64(.5))),int(wp.floor(z[2]-wp.float64(.5))));f=z-wp.vec3d(wp.float64(base[0]),wp.float64(base[1]),wp.float64(base[2]))
 for a in range(3):
  for b in range(3):
   for c in range(3):
    s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin
    if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))
    else:
     ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]
@wp.kernel
def clear(m:wp.array2d(dtype=wp.float64),p:wp.array2d(dtype=wp.vec3d),f:wp.array2d(dtype=wp.vec3d)):
 a,i=wp.tid();m[a,i]=wp.float64(0.0);p[a,i]=wp.vec3d(wp.float64(0.0));f[a,i]=wp.vec3d(wp.float64(0.0))
@wp.kernel
def p2g(v:wp.array(dtype=wp.vec3d),C:wp.array(dtype=wp.mat33d),F:wp.array(dtype=wp.mat33d),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),r:wp.array2d(dtype=wp.vec3d),external:wp.array(dtype=wp.vec3d),mass:wp.float64,vol:wp.float64,mu:wp.float64,lam:wp.float64,h:wp.float64,m:wp.array2d(dtype=wp.float64),p:wp.array2d(dtype=wp.vec3d),force:wp.array2d(dtype=wp.vec3d),stats:wp.array(dtype=wp.float64),bad:wp.array(dtype=int)):
 k=wp.tid();a=lookup[codes[k]];J=wp.determinant(F[k]);cn=wp.float64(0.0)
 for i in range(3):
  for j in range(3):cn+=C[k][i,j]*C[k][i,j]
 wp.atomic_add(stats,0,wp.float64(.5)*mass*(wp.dot(v[k],v[k])+h*h/wp.float64(4.0)*cn))
 if J<=wp.float64(.1) or J>=wp.float64(10.0) or not wp.isfinite(J):wp.atomic_add(bad,0,1)
 else:
  P=mu*F[k]+(lam*wp.log(J)-mu)*wp.transpose(wp.inverse(F[k]));tau=P*wp.transpose(F[k])
  for s in range(27):
   i=ids[k,s];wm=mass*w[k,s];wp.atomic_add(m,a,i,wm);wp.atomic_add(p,a,i,wm*(v[k]+C[k]*r[k,s]));wp.atomic_add(force,a,i,-vol*(tau*g[k,s])+w[k,s]*external[k])
@wp.kernel
def grid_update(m:wp.array2d(dtype=wp.float64),p:wp.array2d(dtype=wp.vec3d),f:wp.array2d(dtype=wp.vec3d),active:wp.array(dtype=int),count:int,dt:wp.float64,vg:wp.array2d(dtype=wp.vec3d),stats:wp.array(dtype=wp.float64)):
 a,i=wp.tid();ma=m[a,i];pa=p[a,i];M=wp.float64(0.0);vg[a,i]=wp.vec3d(wp.float64(0.0))
 for b in range(count):M+=m[b,i]
 if ma>wp.float64(0.0):
  dp=wp.vec3d(wp.float64(0.0))
  for b in range(count):
   if b!=a and compatible(active[a],active[b]):dp+=ma*p[b,i]-m[b,i]*pa
  coupled=pa+dp/M;v=(coupled+dt*f[a,i])/ma;vg[a,i]=v;wp.atomic_add(stats,1,wp.float64(.5)*wp.dot(pa,pa)/ma);wp.atomic_add(stats,2,wp.float64(.5)*wp.dot(coupled,coupled)/ma);wp.atomic_add(stats,3,wp.float64(.5)*ma*wp.dot(v,v))
@wp.kernel
def grid_energy(m:wp.array2d(dtype=wp.float64),vg:wp.array2d(dtype=wp.vec3d),stats:wp.array(dtype=wp.float64)):
 a,i=wp.tid();wp.atomic_add(stats,4,wp.float64(.5)*m[a,i]*wp.dot(vg[a,i],vg[a,i]))
@wp.kernel
def g2p(x:wp.array(dtype=wp.vec3d),v:wp.array(dtype=wp.vec3d),C:wp.array(dtype=wp.mat33d),F:wp.array(dtype=wp.mat33d),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),r:wp.array2d(dtype=wp.vec3d),vg:wp.array2d(dtype=wp.vec3d),dt:wp.float64,h:wp.float64,mass:wp.float64,stats:wp.array(dtype=wp.float64)):
 p=wp.tid();a=lookup[codes[p]];vv=wp.vec3d(wp.float64(0.0));cc=wp.mat33d(wp.float64(0.0));L=wp.mat33d(wp.float64(0.0))
 for s in range(27):
  z=vg[a,ids[p,s]];vv+=w[p,s]*z;cc+=wp.float64(4.0)/h/h*w[p,s]*wp.outer(z,r[p,s]);L+=wp.outer(z,g[p,s])
 I=wp.identity(n=3,dtype=wp.float64);v[p]=vv;C[p]=cc;x[p]=x[p]+dt*vv;F[p]=(I+dt*L)*F[p];cn=wp.float64(0.0)
 for i in range(3):
  for j in range(3):cn+=cc[i,j]*cc[i,j]
 wp.atomic_add(stats,5,wp.float64(.5)*mass*(wp.dot(vv,vv)+h*h/wp.float64(4.0)*cn))
@wp.kernel
def tally(stats:wp.array(dtype=wp.float64),totals:wp.array(dtype=wp.float64)):
 totals[0]+=stats[0]-stats[2]+stats[4]-stats[5];totals[1]+=stats[3]-stats[4]
