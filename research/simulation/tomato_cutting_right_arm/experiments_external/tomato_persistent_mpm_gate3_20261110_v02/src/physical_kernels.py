import warp as wp
@wp.kernel
def contact_advance(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),v0:wp.array2d(dtype=wp.vec3),v1:wp.array2d(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:float,fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float):
 p=wp.tid();a=lookup[codes[p]];dv=wp.vec3(0.0)
 for s in range(27):
  i=ids[p,s];dv+=w[p,s]*(v1[a,i]-v0[a,i])
 vv=v[p]+dv+dt*force[p]/mass;support[p]=wp.vec3(0.0)
 if fixed[p]!=0:support[p]=-mass*vv;vv=wp.vec3(0.0)
 v[p]=vv;x[p]=x[p]+dt*vv

@wp.kernel
def predict_velocity(v:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),v0:wp.array2d(dtype=wp.vec3),v1:wp.array2d(dtype=wp.vec3),out:wp.array(dtype=wp.vec3)):
 p=wp.tid();a=lookup[codes[p]];dv=wp.vec3(0.0)
 for s in range(27):
  i=ids[p,s];dv+=w[p,s]*(v1[a,i]-v0[a,i])
 out[p]=v[p]+dv

@wp.kernel
def finish_velocity(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),new:wp.array(dtype=wp.vec3),dt:float):
 p=wp.tid();v[p]=new[p];x[p]=x[p]+dt*new[p]
