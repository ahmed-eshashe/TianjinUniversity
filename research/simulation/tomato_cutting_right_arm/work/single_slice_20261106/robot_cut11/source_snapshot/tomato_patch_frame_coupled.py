"""Complete weighted-patch frame GN blocks; unchanged traction law."""
import warp as wp
from tomato_global_gn_assembly import gap_jac,put_block,skew3

from tomato_patch_frame_objective import patch_vectors

@wp.func
def patch_differentials(node:int,p:int,pairs:wp.array2d[wp.vec2i],coeff:wp.array3d[wp.float64],u:wp.vec3d,v:wp.vec3d,t:wp.vec3d,n:wp.vec3d,sign:wp.float64):
 au=wp.float64(0.);av=wp.float64(0.)
 for j in range(8):
  for side in range(2):
   if pairs[p,j][side]==node:au+=wp.float64(.5)*coeff[p,j,0];av+=wp.float64(.5)*coeff[p,j,1]
 identity=wp.identity(n=3,dtype=wp.float64);T=(au/wp.length(u))*(identity-wp.outer(t,t));C=av*skew3(u)-au*skew3(v);N=(sign/wp.length(wp.cross(u,v)))*(identity-wp.outer(n,n))*C;B=-skew3(t)*N+skew3(n)*T;return N,T,B

@wp.kernel(enable_backward=False)
def failed_safe_coupled_blocks(offset:int,x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array3d[wp.float64],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 p,sa,sb=wp.tid();at=offset+256*p+16*sa+sb;rows[at]=0;cols[at]=0;values[at]=wp.mat33d(0.)
 if sa<2*counts[p] and sb<2*counts[p] and history[p][1]<wp.float64(1.):
  na=pairs[p,sa//2][sa%2];nb=pairs[p,sb//2][sb%2];half=wp.float64(.5);zero=wp.float64(0.);one=wp.float64(1.);u,v=patch_vectors(x,pairs,anchors,p);t=wp.normalize(u);n=sign[p]*wp.normalize(wp.cross(u,v));b=wp.cross(n,t);damage=history[p][1]
  if eligible[p]!=0:
   total=zero
   for q in range(counts[p]):
    pair=pairs[p,q];gap=x[pair[1]]-x[pair[0]];e=wp.vec3d(wp.max(wp.dot(gap,n),zero),wp.dot(gap,t),wp.dot(gap,b));total+=half*weights[p,q]*wp.dot(e,stiffness[p]*e)
   separation=wp.sqrt(wp.max(wp.float64(2.)*total/law[p][0],wp.float64(1.e-40)));maximum=wp.max(separation,history[p][0]);onset=law[p][1];failure=law[p][2]
   if maximum>=failure:damage=one
   elif maximum>onset:damage=wp.max(damage,failure*(maximum-onset)/(maximum*(failure-onset)))
  Na,Ta,Ba=patch_differentials(na,p,pairs,anchors,u,v,t,n,sign[p]);Nb,Tb,Bb=patch_differentials(nb,p,pairs,anchors,u,v,t,n,sign[p]);H=wp.mat33d(0.)
  for q in range(counts[p]):
   pair=pairs[p,q];gap=x[pair[1]]-x[pair[0]];Ja=gap_jac(na,pair,gap,n,t,b,Na,Ta,Ba);Jb=gap_jac(nb,pair,gap,n,t,b,Nb,Tb,Bb);H+=(one-damage)*weights[p,q]*(wp.transpose(Ja)*stiffness[p]*Jb)
  put_block(at,na,nb,H,free,rows,cols,values)

