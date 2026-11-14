"""Exact nearest original CAD triangle within a verified solid cell.

Only domain-interior quadrature may use this function. It is not a substitute
for signed queries on arbitrary material points or the penetration guard.
"""
import warp as wp
from exact_cad_gpu import Signed
from contact_gpu_precise import closest
@wp.func
def signed_inside(tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),cell:int,p:wp.vec3d):
 best=wp.float64(1e30);face=int(-1);q=wp.vec3d(wp.float64(0.))
 for j in range(ptr[cell],ptr[cell+1]):
  k=ids[j];c=closest(p,tri[k,0],tri[k,1],tri[k,2]);d=wp.length_sq(p-c)
  if d<best:best=d;face=k;q=c
 r=Signed();length=wp.sqrt(best);r.phi=-length
 if length>wp.float64(1e-15):r.normal=-(p-q)/length
 else:r.normal=wp.normalize(wp.cross(tri[face,1]-tri[face,0],tri[face,2]-tri[face,0]))
 return r

@wp.kernel
def query_inside(tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),cells:wp.array(dtype=int),points:wp.array(dtype=wp.vec3d),phi:wp.array(dtype=wp.float64),normal:wp.array(dtype=wp.vec3d)):
 i=wp.tid();r=signed_inside(tri,ptr,ids,cells[i],points[i]);phi[i]=r.phi;normal[i]=r.normal
