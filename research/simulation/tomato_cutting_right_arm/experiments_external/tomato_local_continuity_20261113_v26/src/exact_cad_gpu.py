import warp as wp
from contact_gpu_precise import closest

@wp.struct
class Signed:
 phi:wp.float64
 normal:wp.vec3d

@wp.func
def signed(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),p:wp.vec3d):
 r=Signed();r.phi=wp.float64(100.);r.normal=wp.vec3d(wp.float64(0.));q=wp.mesh_query_point_sign_winding_number(mesh,wp.vec3(p),10.)
 if q.result:
  c=closest(p,tri[q.face,0],tri[q.face,1],tri[q.face,2]);best=wp.length_sq(p-c);bestface=q.face
  # The float nearest-face routine is unreliable for thin CAD triangles.
  # Its candidate still supplies an upper bound. Expand for float BVH rounding,
  # then evaluate every intersecting original triangle in double precision.
  radius=wp.sqrt(best)+wp.float64(2e-7)
  candidates=wp.mesh_query_aabb(mesh,wp.vec3(p-wp.vec3d(radius)),wp.vec3(p+wp.vec3d(radius)))
  for face in candidates:
   candidate=closest(p,tri[face,0],tri[face,1],tri[face,2]);dist=wp.length_sq(p-candidate)
   if dist<best or (dist==best and face<bestface):best=dist;c=candidate;bestface=face
  d=p-c;l=wp.sqrt(best);r.phi=wp.float64(q.sign)*l
  if l>wp.float64(1e-15):r.normal=wp.float64(q.sign)*d/l
  else:r.normal=wp.normalize(wp.cross(tri[bestface,1]-tri[bestface,0],tri[bestface,2]-tri[bestface,0]))
 return r

@wp.kernel
def query_precise(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),points:wp.array(dtype=wp.vec3d),phi:wp.array(dtype=wp.float64),normal:wp.array(dtype=wp.vec3d)):
 i=wp.tid();r=signed(mesh,tri,points[i]);phi[i]=r.phi;normal[i]=r.normal
