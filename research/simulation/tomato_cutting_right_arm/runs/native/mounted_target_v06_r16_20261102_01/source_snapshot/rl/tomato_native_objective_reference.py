"""Float64 Warp automatic derivatives of the objective interface candidate.

Force qualification only: no production solver Hessian, stepping or closure.
"""
import warp as wp

@wp.kernel
def objective_energy(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],damage:wp.array[wp.float64],energy:wp.array[wp.float64]):
 p=wp.tid();a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]]
 origin=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-origin;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-origin
 tangent=wp.normalize(u);normal=sign[p]*wp.normalize(wp.cross(u,v));other=wp.cross(normal,tangent);total=wp.float64(0.)
 # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
 for j in range(8):
  if j<counts[p]:
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];local=wp.vec3d(wp.max(wp.dot(g,normal),wp.float64(0.)),wp.dot(g,tangent),wp.dot(g,other));total+=wp.float64(.5)*weights[p,j]*wp.dot(local,stiffness[p]*local)
 energy[p]=(wp.float64(1.)-damage[p])*total

@wp.kernel
def incremental_objective_energy(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],energy:wp.array[wp.float64]):
 p=wp.tid();a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]]
 origin=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-origin;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-origin
 tangent=wp.normalize(u);normal=sign[p]*wp.normalize(wp.cross(u,v));other=wp.cross(normal,tangent);total=wp.float64(0.)
 # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
 for j in range(8):
  if j<counts[p]:
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];local=wp.vec3d(wp.max(wp.dot(g,normal),wp.float64(0.)),wp.dot(g,tangent),wp.dot(g,other));total+=wp.float64(.5)*weights[p,j]*wp.dot(local,stiffness[p]*local)
 kn=law[p][0];onset=law[p][1];failure=law[p][2];old=history[p]
 q=wp.sqrt(wp.max(wp.float64(2.)*total/kn,wp.float64(1.e-40)));value=(wp.float64(1.)-old[1])*total
 if eligible[p]!=0 and q>=old[0]:
  previous=wp.min(failure,wp.max(onset,old[0]));old_dissipation=wp.float64(.5)*kn*onset*failure/(failure-onset)*(previous-onset)
  if q>=failure:value=wp.float64(.5)*kn*onset*failure-old_dissipation
  elif q>onset:value=wp.float64(.5)*kn*onset*onset+kn*onset/(failure-onset)*(failure*(q-onset)-wp.float64(.5)*(q*q-onset*onset))-old_dissipation
  else:value=total-old_dissipation
 energy[p]=value


@wp.kernel
def objective_force(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],force:wp.array[wp.vec3d]):
 p=wp.tid();a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]]
 origin=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-origin;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-origin
 length=wp.length(u);cross=wp.cross(u,v);cross_length=wp.length(cross);tangent=u/length;normal=sign[p]*cross/cross_length;other=wp.cross(normal,tangent);total=wp.float64(0.)
 # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
 for j in range(8):
  if j<counts[p]:
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];local=wp.vec3d(wp.max(wp.dot(g,normal),wp.float64(0.)),wp.dot(g,tangent),wp.dot(g,other));total+=wp.float64(.5)*weights[p,j]*wp.dot(local,stiffness[p]*local)
 damage=history[p][1]
 if eligible[p]!=0:
  q=wp.sqrt(wp.max(wp.float64(2.)*total/law[p][0],wp.float64(1.e-40)));maximum=wp.max(q,history[p][0]);onset=law[p][1];failure=law[p][2]
  if maximum>=failure:damage=wp.float64(1.)
  elif maximum>onset:damage=wp.max(damage,failure*(maximum-onset)/(maximum*(failure-onset)))
 factor=wp.float64(1.)-damage;grad_n=wp.vec3d(0.);grad_t=wp.vec3d(0.);grad_b=wp.vec3d(0.)
 # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
 for j in range(8):
  if j<counts[p]:
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];gn=wp.dot(g,normal);local=wp.vec3d(wp.max(gn,wp.float64(0.)),wp.dot(g,tangent),wp.dot(g,other));traction=weights[p,j]*(stiffness[p]*local)
   if gn<wp.float64(0.):traction[0]=wp.float64(0.)
   world=traction[0]*normal+traction[1]*tangent+traction[2]*other
   wp.atomic_add(force,pair[0],factor*world);wp.atomic_add(force,pair[1],-factor*world)
   grad_n+=traction[0]*g;grad_t+=traction[1]*g;grad_b+=traction[2]*g
 grad_n+=wp.cross(tangent,grad_b);grad_t+=wp.cross(grad_b,normal)
 grad_cross=sign[p]*(grad_n-normal*wp.dot(normal,grad_n))/cross_length
 grad_u=(grad_t-tangent*wp.dot(tangent,grad_t))/length+wp.cross(v,grad_cross);grad_v=wp.cross(grad_cross,u)
 ga=-grad_u-grad_v;gb=grad_u;gc=grad_v
 wp.atomic_add(force,p0[0],-wp.float64(.5)*factor*ga);wp.atomic_add(force,p0[1],-wp.float64(.5)*factor*ga)
 wp.atomic_add(force,p1[0],-wp.float64(.5)*factor*gb);wp.atomic_add(force,p1[1],-wp.float64(.5)*factor*gb)
 wp.atomic_add(force,p2[0],-wp.float64(.5)*factor*gc);wp.atomic_add(force,p2[1],-wp.float64(.5)*factor*gc)

@wp.kernel
def force_seed(colors:wp.array[int],color:int,axis:int,seed:wp.array[wp.vec3d]):
 i=wp.tid();value=wp.vec3d(0.)
 if colors[i]==color:value[axis]=wp.float64(1.)
 seed[i]=value

@wp.kernel
def hessian_column(colors:wp.array[int],color:int,axis:int,gradient:wp.array[wp.vec3d],blocks:wp.array[wp.mat33d]):
 i=wp.tid()
 if colors[i]==color:
  block=blocks[i]
  for j in range(3):block[axis,j]=-gradient[i][j]
  blocks[i]=block

@wp.kernel
def cast_positions(source:wp.array[wp.vec3],target:wp.array[wp.vec3d]):
 i=wp.tid();p=source[i];target[i]=wp.vec3d(wp.float64(p[0]),wp.float64(p[1]),wp.float64(p[2]))

@wp.kernel
def add_objective_blocks(color:int,colors:wp.array[int],oforce:wp.array[wp.vec3d],ohessian:wp.array[wp.mat33d],force:wp.array[wp.vec3],hessian:wp.array[wp.mat33]):
 i=wp.tid()
 if colors[i]==color:
  f=oforce[i];h=ohessian[i];force[i]+=wp.vec3(float(f[0]),float(f[1]),float(f[2]));hessian[i]+=wp.mat33(float(h[0,0]),float(h[0,1]),float(h[0,2]),float(h[1,0]),float(h[1,1]),float(h[1,2]),float(h[2,0]),float(h[2,1]),float(h[2,2]))

@wp.kernel
def validate_frames(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],anchors:wp.array[wp.vec3i],invalid:wp.array[int]):
 p=wp.tid();a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]];m0=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-m0;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-m0
 if wp.length(u)<=wp.float64(1.e-8) or wp.length(wp.cross(u,v))<=wp.float64(1.e-12):wp.atomic_add(invalid,0,1)

@wp.kernel
def commit_objective_history(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],eligible:wp.array[int],history:wp.array[wp.vec2d],mirror:wp.array[wp.vec2]):
 p=wp.tid()
 if eligible[p]!=0:
  a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]];origin=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-origin;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-origin;t=wp.normalize(u);n=sign[p]*wp.normalize(wp.cross(u,v));b=wp.cross(n,t);total=wp.float64(0.)
  # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
  for j in range(8):
   if j<counts[p]:
    pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];e=wp.vec3d(wp.max(wp.dot(g,n),wp.float64(0.)),wp.dot(g,t),wp.dot(g,b));total+=wp.float64(.5)*weights[p,j]*wp.dot(e,stiffness[p]*e)
  q=wp.sqrt(wp.max(wp.float64(2.)*total/law[p][0],wp.float64(0.)));old=history[p];maximum=wp.max(old[0],q);d=old[1];a0=law[p][1];bf=law[p][2]
  if maximum>=bf:d=wp.float64(1.)
  elif maximum>a0:d=wp.max(d,bf*(maximum-a0)/(maximum*(bf-a0)))
  history[p]=wp.vec2d(maximum,d);mirror[p]=wp.vec2(float(maximum),float(d))
