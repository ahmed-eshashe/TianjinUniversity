"""Unchanged bulk gradient and declared block approximation, retained in float64."""
import warp as wp

@wp.kernel(enable_backward=False)
def double_bulk(color:int,colors:wp.array[int],x:wp.array[wp.vec3d],spring_offsets:wp.array[int],spring_ids:wp.array[int],spring_pairs:wp.array[int],spring_rest:wp.array[wp.float64],spring_k:wp.array[wp.float64],cell_offsets:wp.array[int],cell_ids:wp.array[int],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],invalid:wp.array[int],forces:wp.array[wp.vec3d],hessians:wp.array[wp.mat33d]):
 node=wp.tid()
 if color<0 or colors[node]==color:
  f=wp.vec3d(0.);h=wp.mat33d(0.);identity=wp.identity(n=3,dtype=wp.float64)
  for index in range(spring_offsets[node],spring_offsets[node+1]):
   spring=spring_ids[index];sv0=spring_pairs[2*spring];sv1=spring_pairs[2*spring+1];diff=x[sv0]-x[sv1];length=wp.max(wp.length(diff),wp.float64(1e-8));l0=spring_rest[spring];k=spring_k[spring];sgn=wp.float64(1.)
   if node!=sv0:sgn=wp.float64(-1.)
   f+=sgn*k*(l0-length)/length*diff;h+=k*(identity-(l0/length)*(identity-wp.outer(diff,diff)/(length*length)))
  for index in range(cell_offsets[node],cell_offsets[node+1]):
   i=cell_ids[index];ids=cells[i];a=x[ids[1]]-x[ids[0]];b=x[ids[2]]-x[ids[0]];c=x[ids[3]]-x[ids[0]];V=volumes[i];j=wp.dot(a,wp.cross(b,c))/(wp.float64(6.)*V)
   if j<=wp.float64(.1):wp.atomic_add(invalid,0,1)
   elif j<wp.float64(.5):
    r=(j-wp.float64(.1))/wp.float64(.4);first=(wp.float64(1.)-wp.float64(1.)/r)/wp.float64(.4);second=wp.float64(1.)/(r*r*wp.float64(.16));g1=wp.cross(b,c)/(wp.float64(6.)*V);g2=wp.cross(c,a)/(wp.float64(6.)*V);g3=wp.cross(a,b)/(wp.float64(6.)*V);g=-g1-g2-g3
    if node==ids[1]:g=g1
    elif node==ids[2]:g=g2
    elif node==ids[3]:g=g3
    f-=wp.float64(10000.)*V*first*g;h+=wp.float64(10000.)*V*second*wp.outer(g,g)
  forces[node]=f;hessians[node]=h

@wp.kernel(enable_backward=False)
def determinant_diagnosis(blocks:wp.array[wp.mat33d],mass:wp.array[wp.float64],nodes:wp.array[int],dt:wp.float64,single:wp.array[float],double:wp.array[wp.float64]):
 i=wp.tid();node=nodes[i];h=blocks[node]+mass[node]/(dt*dt)*wp.identity(n=3,dtype=wp.float64);h32=wp.mat33(float(h[0,0]),float(h[0,1]),float(h[0,2]),float(h[1,0]),float(h[1,1]),float(h[1,2]),float(h[2,0]),float(h[2,1]),float(h[2,2]));single[i]=wp.determinant(h32);double[i]=wp.determinant(h)
