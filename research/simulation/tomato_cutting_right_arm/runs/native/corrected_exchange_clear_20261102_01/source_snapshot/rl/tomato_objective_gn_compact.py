"""Positive Gauss-Newton preconditioner for exact objective cohesive forces.

J_i differentiates every local opening/shear gap including the moving frame.
H_i = (1-D) sum_q w_q J_qi^T K J_qi. This is NOT the exact
force Jacobian in deformed/loading states; constitutive force is unchanged.
"""
import warp as wp

@wp.func
def skew3(v:wp.vec3d):
 z=wp.float64(0.);return wp.mat33d(z,-v[2],v[1],v[2],z,-v[0],-v[1],v[0],z)

@wp.kernel(enable_backward=False)
def objective_gn(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],hessian:wp.array[wp.mat33d]):
 p,slot=wp.tid();a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]];half=wp.float64(.5);zero=wp.float64(0.);one=wp.float64(1.)
 origin=half*(x[p0[0]]+x[p0[1]]);u=half*(x[p1[0]]+x[p1[1]])-origin;v=half*(x[p2[0]]+x[p2[1]])-origin;length=wp.length(u);cross=wp.cross(u,v);cross_length=wp.length(cross);t=u/length;n=sign[p]*cross/cross_length;b=wp.cross(n,t);identity=wp.identity(n=3,dtype=wp.float64);total=zero
 for j in range(counts[p]):
  if j<counts[p]:
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];local=wp.vec3d(wp.max(wp.dot(g,n),zero),wp.dot(g,t),wp.dot(g,b));total+=half*weights[p,j]*wp.dot(local,stiffness[p]*local)
 damage=history[p][1]
 if eligible[p]!=0:
  q=wp.sqrt(wp.max(wp.float64(2.)*total/law[p][0],wp.float64(1.e-40)));maximum=wp.max(q,history[p][0]);onset=law[p][1];failure=law[p][2]
  if maximum>=failure:damage=one
  elif maximum>onset:damage=wp.max(damage,failure*(maximum-onset)/(maximum*(failure-onset)))
 factor=one-damage
 if slot<2*counts[p]:
  node=pairs[p,slot//2][slot%2];duplicate=bool(False)
  for before in range(slot):
   if pairs[p,before//2][before%2]==node:duplicate=True
  if not duplicate:
   au=zero;av=zero
   for side in range(2):
    if p0[side]==node:au-=half;av-=half
    if p1[side]==node:au+=half
    if p2[side]==node:av+=half
   T=(au/length)*(identity-wp.outer(t,t));C=av*skew3(u)-au*skew3(v);N=(sign[p]/cross_length)*(identity-wp.outer(n,n))*C;B=-skew3(t)*N+skew3(n)*T;H=wp.mat33d(0.)
   for j in range(counts[p]):
    if j<counts[p]:
     pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];beta=zero
     if pair[0]==node:beta-=one
     if pair[1]==node:beta+=one
     jn=wp.vec3d(0.)
     if wp.dot(g,n)>=zero:jn=beta*n+wp.transpose(N)*g
     jt=beta*t+wp.transpose(T)*g;jb=beta*b+wp.transpose(B)*g
     J=wp.mat33d(jn[0],jn[1],jn[2],jt[0],jt[1],jt[2],jb[0],jb[1],jb[2]);H+=factor*weights[p,j]*(wp.transpose(J)*stiffness[p]*J)
   wp.atomic_add(hessian,node,H)
