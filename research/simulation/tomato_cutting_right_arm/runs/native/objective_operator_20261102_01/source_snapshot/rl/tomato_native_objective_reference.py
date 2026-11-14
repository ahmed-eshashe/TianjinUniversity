"""Float64 Warp automatic derivatives of the objective interface candidate.

Force qualification only: no production solver Hessian, stepping or closure.
"""
import warp as wp

@wp.kernel
def objective_energy(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],damage:wp.array[wp.float64],energy:wp.array[wp.float64]):
 p=wp.tid();a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]]
 origin=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-origin;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-origin
 tangent=wp.normalize(u);normal=sign[p]*wp.normalize(wp.cross(u,v));other=wp.cross(normal,tangent);total=wp.float64(0.)
 for j in range(counts[p]):
  pair=pairs[p,j];g=x[pair[1]]-x[pair[0]];local=wp.vec3d(wp.max(wp.dot(g,normal),wp.float64(0.)),wp.dot(g,tangent),wp.dot(g,other));total+=wp.float64(.5)*weights[p,j]*wp.dot(local,stiffness[p]*local)
 energy[p]=(wp.float64(1.)-damage[p])*total
