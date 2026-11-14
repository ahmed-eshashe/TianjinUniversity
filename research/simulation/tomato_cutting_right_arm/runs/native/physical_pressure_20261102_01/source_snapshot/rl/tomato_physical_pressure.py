"""Physical-coordinate pressure packet operator, separate from native Contacts.

No collision detection or integration here. Input quadrature and planar feature
frames are frozen per evaluation; generated CAD contact needs separate gates.
"""
import warp as wp

@wp.kernel(enable_backward=False)
def pressure_packet(x:wp.array[wp.vec3d],indices:wp.array[wp.vec3i],bary:wp.array[wp.vec3d],area:wp.array[wp.float64],point_local:wp.array[wp.vec3d],normal_local:wp.array[wp.vec3d],rotation:wp.array[wp.mat33d],translation:wp.array[wp.vec3d],com_local:wp.array[wp.vec3d],sample_force:wp.array[wp.vec3d],sample_hessian:wp.array[wp.mat33d],body_force:wp.array[wp.vec3d],body_torque:wp.array[wp.vec3d],energy:wp.array[wp.float64]):
 i=wp.tid();ids=indices[i];w=bary[i];p=w[0]*x[ids[0]]+w[1]*x[ids[1]]+w[2]*x[ids[2]];R=rotation[0];q=R*point_local[i]+translation[0];n=R*normal_local[i];gap=wp.dot(p-q,n);k=wp.float64(1750000000.)*area[i];f=-k*wp.min(gap,wp.float64(0.))*n;h=wp.mat33d(0.)
 if gap<wp.float64(0.):h=k*wp.outer(n,n)
 sample_force[i]=f;sample_hessian[i]=h;body_force[i]=-f;body_torque[i]=wp.cross(p-(translation[0]+R*com_local[0]),-f);energy[i]=wp.float64(.5)*k*wp.min(gap,wp.float64(0.))*wp.min(gap,wp.float64(0.))

@wp.kernel(enable_backward=False)
def scatter_packet(color:int,colors:wp.array[int],indices:wp.array[wp.vec3i],bary:wp.array[wp.vec3d],sample_force:wp.array[wp.vec3d],sample_hessian:wp.array[wp.mat33d],force:wp.array[wp.vec3],hessian:wp.array[wp.mat33]):
 i,corner=wp.tid();node=indices[i][corner]
 if color<0 or colors[node]==color:
  w=bary[i][corner];f=w*sample_force[i];h=w*w*sample_hessian[i];wp.atomic_add(force,node,wp.vec3(float(f[0]),float(f[1]),float(f[2])));wp.atomic_add(hessian,node,wp.mat33(float(h[0,0]),float(h[0,1]),float(h[0,2]),float(h[1,0]),float(h[1,1]),float(h[1,2]),float(h[2,0]),float(h[2,1]),float(h[2,2])))
