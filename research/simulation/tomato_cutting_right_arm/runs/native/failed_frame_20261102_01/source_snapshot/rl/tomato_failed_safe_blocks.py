"""Exact objective force plus the same positive GN blocks, only for one VBD color.

Force = -(1-D) sum_q w_q J_qi.T K e_q. Frame derivatives in J
include the three anchor midpoints. This is algebraically the previous explicit
frame force; it is not a change to the material law or fracture budget.
"""
import warp as wp
from tomato_objective_gn_compact import skew3

@wp.kernel(enable_backward=False)
def failed_safe_cohesive_blocks(color:int,colors:wp.array[int],x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],force:wp.array[wp.vec3d],hessian:wp.array[wp.mat33d]):
 patch,slot=wp.tid()
 if history[patch][1]>=wp.float64(1.):return
 if slot<2*counts[patch]:
  node=pairs[patch,slot//2][slot%2]
  if color<0 or colors[node]==color:
   anchor_ids=anchors[patch];pair_a=pairs[patch,anchor_ids[0]];pair_b=pairs[patch,anchor_ids[1]];pair_c=pairs[patch,anchor_ids[2]];half=wp.float64(.5);zero=wp.float64(0.);one=wp.float64(1.);origin=half*(x[pair_a[0]]+x[pair_a[1]]);u=half*(x[pair_b[0]]+x[pair_b[1]])-origin;v=half*(x[pair_c[0]]+x[pair_c[1]])-origin;length=wp.length(u);cross=wp.cross(u,v);cross_length=wp.length(cross);t=u/length;n=sign[patch]*cross/cross_length;b=wp.cross(n,t);damage=history[patch][1]
   if eligible[patch]!=0:
    total=zero
    for q in range(counts[patch]):
     pair=pairs[patch,q];gap=x[pair[1]]-x[pair[0]];e=wp.vec3d(wp.max(wp.dot(gap,n),zero),wp.dot(gap,t),wp.dot(gap,b));total+=half*weights[patch,q]*wp.dot(e,stiffness[patch]*e)
    separation=wp.sqrt(wp.max(wp.float64(2.)*total/law[patch][0],wp.float64(1.e-40)));maximum=wp.max(separation,history[patch][0]);onset=law[patch][1];failure=law[patch][2]
    if maximum>=failure:damage=one
    elif maximum>onset:damage=wp.max(damage,failure*(maximum-onset)/(maximum*(failure-onset)))
   factor=one-damage;au=zero;av=zero
   for side in range(2):
    if pair_a[side]==node:au-=half;av-=half
    if pair_b[side]==node:au+=half
    if pair_c[side]==node:av+=half
   identity=wp.identity(n=3,dtype=wp.float64);T=(au/length)*(identity-wp.outer(t,t));C=av*skew3(u)-au*skew3(v);N=(sign[patch]/cross_length)*(identity-wp.outer(n,n))*C;B=-skew3(t)*N+skew3(n)*T;f=wp.vec3d(0.);H=wp.mat33d(0.);anchor_node=bool(au!=zero or av!=zero)
   for q in range(counts[patch]):
    if anchor_node or q==slot//2:
     pair=pairs[patch,q];gap=x[pair[1]]-x[pair[0]];gn=wp.dot(gap,n);beta=zero
     if pair[0]==node:beta-=one
     if pair[1]==node:beta+=one
     jn=wp.vec3d(0.)
     if gn>=zero:jn=beta*n+wp.transpose(N)*gap
     jt=beta*t+wp.transpose(T)*gap;jb=beta*b+wp.transpose(B)*gap;J=wp.mat33d(jn[0],jn[1],jn[2],jt[0],jt[1],jt[2],jb[0],jb[1],jb[2]);e=wp.vec3d(wp.max(gn,zero),wp.dot(gap,t),wp.dot(gap,b));f-=factor*weights[patch,q]*(wp.transpose(J)*(stiffness[patch]*e));H+=factor*weights[patch,q]*(wp.transpose(J)*stiffness[patch]*J)
   wp.atomic_add(force,node,f);wp.atomic_add(hessian,node,H)
