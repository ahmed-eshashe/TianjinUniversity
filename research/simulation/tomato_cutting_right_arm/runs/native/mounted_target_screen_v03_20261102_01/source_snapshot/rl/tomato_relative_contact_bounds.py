"""Float64 candidate distances plus an explicit 0.1 micrometre safety reserve."""
import warp as wp
from newton._src.geometry.tri_mesh_collision import TriMeshCollisionInfo
from tomato_canonical_self_contact import barycentric_closest
from tomato_mollified_self_contact import closest_segments

@wp.kernel(enable_backward=False)
def precise_contact_bounds(x:wp.array[wp.vec3d],triangles:wp.array2d[int],edges:wp.array2d[int],info_array:wp.array[TriMeshCollisionInfo],relaxation:float,bounds:wp.array[float],invalid:wp.array[int]):
 source=wp.tid();info=info_array[0];reserve=wp.float64(1.e-7)
 if source<info.vertex_colliding_triangles_count.shape[0]:
  count=info.vertex_colliding_triangles_count[source];capacity=info.vertex_colliding_triangles_buffer_sizes[source];offset=info.vertex_colliding_triangles_offsets[source]
  if capacity>0 and count>=capacity:wp.atomic_add(invalid,0,1)
  for j in range(wp.min(count,capacity)):
   v=info.vertex_colliding_triangles[2*(offset+j)];t=info.vertex_colliding_triangles[2*(offset+j)+1];a=triangles[t,0];b=triangles[t,1];c=triangles[t,2];cross=wp.cross(x[b]-x[a],x[c]-x[a])
   if wp.dot(cross,cross)<=wp.float64(1.e-30):wp.atomic_add(invalid,0,1)
   else:
    bary=barycentric_closest(x[a],x[b],x[c],x[v]);point=bary[0]*x[a]+bary[1]*x[b]+bary[2]*x[c];distance=wp.length(x[v]-point)
    if distance<=reserve:wp.atomic_add(invalid,0,1)
    bound=float(wp.float64(relaxation)*wp.max(distance-reserve,wp.float64(0.)));wp.atomic_min(bounds,v,bound);wp.atomic_min(bounds,a,bound);wp.atomic_min(bounds,b,bound);wp.atomic_min(bounds,c,bound)
 if source<info.edge_colliding_edges_count.shape[0]:
  count=info.edge_colliding_edges_count[source];capacity=info.edge_colliding_edges_buffer_sizes[source];offset=info.edge_colliding_edges_offsets[source]
  if capacity>0 and count>=capacity:wp.atomic_add(invalid,0,1)
  for j in range(wp.min(count,capacity)):
   e0=info.edge_colliding_edges[2*(offset+j)];e1=info.edge_colliding_edges[2*(offset+j)+1];a=edges[e0,2];b=edges[e0,3];c=edges[e1,2];d=edges[e1,3]
   if wp.length(x[b]-x[a])<=wp.float64(1.e-12) or wp.length(x[d]-x[c])<=wp.float64(1.e-12):wp.atomic_add(invalid,0,1)
   else:
    st=closest_segments(x[a],x[b],x[c],x[d]);distance=wp.length(x[a]+st[0]*(x[b]-x[a])-x[c]-st[1]*(x[d]-x[c]))
    if distance<=reserve:wp.atomic_add(invalid,0,1)
    bound=float(wp.float64(relaxation)*wp.max(distance-reserve,wp.float64(0.)));wp.atomic_min(bounds,a,bound);wp.atomic_min(bounds,b,bound);wp.atomic_min(bounds,c,bound);wp.atomic_min(bounds,d,bound)
