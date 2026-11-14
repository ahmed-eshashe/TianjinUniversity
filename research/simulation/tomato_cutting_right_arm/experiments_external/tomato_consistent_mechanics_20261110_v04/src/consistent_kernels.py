import warp as wp
@wp.kernel
def internal(q:wp.array(dtype=wp.vec3d),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),external:wp.array(dtype=wp.vec3d),vol:wp.float64,mu:wp.float64,lam:wp.float64,force:wp.array(dtype=wp.vec3d),bad:wp.array(dtype=int)):
 p=wp.tid();F=wp.mat33d(wp.float64(0.0))
 for s in range(27):F+=wp.outer(q[ids[p,s]],g[p,s])
 J=wp.determinant(F)
 if J<=wp.float64(.1) or J>=wp.float64(10.0) or not wp.isfinite(J):wp.atomic_add(bad,0,1)
 else:
  P=mu*F+(lam*wp.log(J)-mu)*wp.transpose(wp.inverse(F))
  for s in range(27):wp.atomic_add(force,ids[p,s],-vol*(P*g[p,s])+w[p,s]*external[p])
@wp.kernel
def solve_axis(src:wp.array(dtype=wp.vec3d),dest:wp.array(dtype=wp.vec3d),inverse:wp.array2d(dtype=wp.float64),dims:wp.vec3i,axis:int,scale:wp.float64):
 n=wp.tid();i=n//(dims[1]*dims[2]);j=(n//dims[2])%dims[1];k=n%dims[2];out=wp.vec3d(wp.float64(0.0))
 if axis==0:
  for z in range(dims[0]):out+=inverse[i,z]*src[(z*dims[1]+j)*dims[2]+k]
 elif axis==1:
  for z in range(dims[1]):out+=inverse[j,z]*src[(i*dims[1]+z)*dims[2]+k]
 else:
  for z in range(dims[2]):out+=inverse[k,z]*src[(i*dims[1]+j)*dims[2]+z]
 dest[n]=scale*out
@wp.kernel
def drift(q:wp.array(dtype=wp.vec3d),vg:wp.array(dtype=wp.vec3d),a:wp.array(dtype=wp.vec3d),dt:wp.float64):
 i=wp.tid();vh=vg[i]+wp.float64(.5)*dt*a[i];q[i]+=dt*vh;vg[i]=vh
@wp.kernel
def kick(vg:wp.array(dtype=wp.vec3d),a:wp.array(dtype=wp.vec3d),dt:wp.float64):
 i=wp.tid();vg[i]+=wp.float64(.5)*dt*a[i]
@wp.kernel
def reconstruct(q:wp.array(dtype=wp.vec3d),vg:wp.array(dtype=wp.vec3d),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),x:wp.array(dtype=wp.vec3d),v:wp.array(dtype=wp.vec3d),F:wp.array(dtype=wp.mat33d)):
 p=wp.tid();xx=wp.vec3d(wp.float64(0.0));vv=wp.vec3d(wp.float64(0.0));ff=wp.mat33d(wp.float64(0.0))
 for s in range(27):
  i=ids[p,s];xx+=w[p,s]*q[i];vv+=w[p,s]*vg[i];ff+=wp.outer(q[i],g[p,s])
 x[p]=xx;v[p]=vv;F[p]=ff
