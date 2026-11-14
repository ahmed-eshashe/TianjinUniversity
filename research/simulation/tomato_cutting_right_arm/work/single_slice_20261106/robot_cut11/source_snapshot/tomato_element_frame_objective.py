"""Weighted affine patch frame; original bilinear cohesive law. Versioned model extension."""
import warp as wp

@wp.func
def patch_vectors(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],coeff:wp.array3d[wp.float64],p:int):
 u=wp.vec3d(0.);v=wp.vec3d(0.)
 for j in range(16):
  pair=pairs[p,j];mid=wp.float64(.5)*(x[pair[0]]+x[pair[1]])
  u+=coeff[p,j,0]*mid;v+=coeff[p,j,1]*mid
 return u,v


@wp.kernel
def incremental_objective_energy(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array3d[wp.float64],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],energy:wp.array[wp.float64]):
 p=wp.tid()
 if history[p][1]>=wp.float64(1.):energy[p]=wp.float64(0.);return
 u,v=patch_vectors(x,pairs,anchors,p)
 tangent=wp.normalize(u);normal=sign[p]*wp.normalize(wp.cross(u,v));other=wp.cross(normal,tangent);total=wp.float64(0.)
 # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
 for j in range(16):
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
def objective_force(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array3d[wp.float64],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],force:wp.array[wp.vec3d]):
 p=wp.tid()
 if history[p][1]>=wp.float64(1.):return
 u,v=patch_vectors(x,pairs,anchors,p)
 length=wp.length(u);cross=wp.cross(u,v);cross_length=wp.length(cross);tangent=u/length;normal=sign[p]*cross/cross_length;other=wp.cross(normal,tangent);total=wp.float64(0.)
 # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
 for j in range(16):
  if j<counts[p]:
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];local=wp.vec3d(wp.max(wp.dot(g,normal),wp.float64(0.)),wp.dot(g,tangent),wp.dot(g,other));total+=wp.float64(.5)*weights[p,j]*wp.dot(local,stiffness[p]*local)
 damage=history[p][1]
 if eligible[p]!=0:
  q=wp.sqrt(wp.max(wp.float64(2.)*total/law[p][0],wp.float64(1.e-40)));maximum=wp.max(q,history[p][0]);onset=law[p][1];failure=law[p][2]
  if maximum>=failure:damage=wp.float64(1.)
  elif maximum>onset:damage=wp.max(damage,failure*(maximum-onset)/(maximum*(failure-onset)))
 factor=wp.float64(1.)-damage;grad_n=wp.vec3d(0.);grad_t=wp.vec3d(0.);grad_b=wp.vec3d(0.)
 # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
 for j in range(16):
  if j<counts[p]:
   pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];gn=wp.dot(g,normal);local=wp.vec3d(wp.max(gn,wp.float64(0.)),wp.dot(g,tangent),wp.dot(g,other));traction=weights[p,j]*(stiffness[p]*local)
   if gn<wp.float64(0.):traction[0]=wp.float64(0.)
   world=traction[0]*normal+traction[1]*tangent+traction[2]*other
   wp.atomic_add(force,pair[0],factor*world);wp.atomic_add(force,pair[1],-factor*world)
   grad_n+=traction[0]*g;grad_t+=traction[1]*g;grad_b+=traction[2]*g
 grad_n+=wp.cross(tangent,grad_b);grad_t+=wp.cross(grad_b,normal)
 grad_cross=sign[p]*(grad_n-normal*wp.dot(normal,grad_n))/cross_length
 grad_u=(grad_t-tangent*wp.dot(tangent,grad_t))/length+wp.cross(v,grad_cross);grad_v=wp.cross(grad_cross,u)
 for j in range(16):
  if j<counts[p]:
   pair=pairs[p,j];grad=anchors[p,j,0]*grad_u+anchors[p,j,1]*grad_v
   wp.atomic_add(force,pair[0],-wp.float64(.5)*factor*grad);wp.atomic_add(force,pair[1],-wp.float64(.5)*factor*grad)



@wp.kernel(enable_backward=False)
def validate_active_frames(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],anchors:wp.array3d[wp.float64],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],invalid:wp.array[int]):
 p=wp.tid();old=history[p];expected=wp.float64(0.)
 if old[0]>=law[p][2]:expected=wp.float64(1.)
 elif old[0]>law[p][1]:expected=law[p][2]*(old[0]-law[p][1])/(old[0]*(law[p][2]-law[p][1]))
 if not wp.isfinite(old[0]) or not wp.isfinite(old[1]) or old[0]<wp.float64(0.) or old[1]<wp.float64(0.) or old[1]>wp.float64(1.) or wp.abs(old[1]-expected)>wp.float64(1.e-10):wp.atomic_add(invalid,0,1)
 elif old[1]<wp.float64(1.):
  u,v=patch_vectors(x,pairs,anchors,p)
  if wp.length(u)<=wp.float64(1.e-8) or wp.length(wp.cross(u,v))<=wp.float64(1.e-8):wp.atomic_add(invalid,0,1)


@wp.kernel
def commit_objective_history(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array3d[wp.float64],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],eligible:wp.array[int],history:wp.array[wp.vec2d],mirror:wp.array[wp.vec2]):
 p=wp.tid();old_committed=history[p];mirror[p]=wp.vec2(float(old_committed[0]),float(old_committed[1]))
 if old_committed[1]>=wp.float64(1.):return
 if eligible[p]!=0:
  u,v=patch_vectors(x,pairs,anchors,p);t=wp.normalize(u);n=sign[p]*wp.normalize(wp.cross(u,v));b=wp.cross(n,t);total=wp.float64(0.)
  # Bounded unrolling preserves nonlinear accumulator values in Warp reverse mode.
  for j in range(16):
   if j<counts[p]:
    pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];e=wp.vec3d(wp.max(wp.dot(g,n),wp.float64(0.)),wp.dot(g,t),wp.dot(g,b));total+=wp.float64(.5)*weights[p,j]*wp.dot(e,stiffness[p]*e)
  q=wp.sqrt(wp.max(wp.float64(2.)*total/law[p][0],wp.float64(0.)));old=history[p];maximum=wp.max(old[0],q);d=old[1];a0=law[p][1];bf=law[p][2]
  if maximum>=bf:d=wp.float64(1.)
  elif maximum>a0:d=wp.max(d,bf*(maximum-a0)/(maximum*(bf-a0)))
  history[p]=wp.vec2d(maximum,d);mirror[p]=wp.vec2(float(maximum),float(d))
