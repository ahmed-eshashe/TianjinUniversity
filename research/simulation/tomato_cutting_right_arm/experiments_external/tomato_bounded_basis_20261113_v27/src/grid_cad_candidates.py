"""Exact nearest-triangle candidate index; NOT an interpolated distance field.

For voxel center c and covering radius r, retain all triangles with
 d_triangle(c) <= min_j d_j(c) + 2r.
The distance to a closed triangle is 1-Lipschitz, so a discarded triangle
cannot be closest anywhere inside that voxel. Queries evaluate retained
original triangles in float64; outside-index queries evaluate all faces.
"""
from pathlib import Path
import hashlib,json,time,numpy as np,warp as wp
from contact_gpu_precise import closest
from exact_cad_gpu import Signed

@wp.kernel
def build_candidates(tri:wp.array2d(dtype=wp.vec3d),origin:wp.vec3d,shape:wp.vec3i,h:wp.float64,counts:wp.array(dtype=int),ids:wp.array2d(dtype=int),overflow:wp.array(dtype=int)):
 index=wp.tid();i=index//(shape[1]*shape[2]);j=(index//shape[2])%shape[1];k=index%shape[2];center=origin+h*(wp.vec3d(wp.float64(i),wp.float64(j),wp.float64(k))+wp.vec3d(wp.float64(.5)));best=wp.float64(1e30)
 for f in range(tri.shape[0]):best=wp.min(best,wp.length(center-closest(center,tri[f,0],tri[f,1],tri[f,2])))
 threshold=best+wp.sqrt(wp.float64(3.))*h+wp.float64(2e-10);n=int(0)
 for f in range(tri.shape[0]):
  if wp.length(center-closest(center,tri[f,0],tri[f,1],tri[f,2]))<=threshold:
   if n<ids.shape[1]:ids[index,n]=f
   else:wp.atomic_max(overflow,0,1)
   n+=1
 counts[index]=n

@wp.func
def signed_grid(tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),origin:wp.vec3d,shape:wp.vec3i,h:wp.float64,p:wp.vec3d):
 index=wp.vec3i(int(wp.floor((p[0]-origin[0])/h)),int(wp.floor((p[1]-origin[1])/h)),int(wp.floor((p[2]-origin[2])/h)));within=True
 for a in range(3):
  if index[a]<0 or index[a]>=shape[a]:within=False
 lo=int(0);hi=tri.shape[0]
 if within:
  cell=(index[0]*shape[1]+index[1])*shape[2]+index[2];lo=ptr[cell];hi=ptr[cell+1]
 best=wp.float64(1e30);face=int(-1);q=wp.vec3d(wp.float64(0.))
 for z in range(lo,hi):
  f=z
  if within:f=ids[z]
  c=closest(p,tri[f,0],tri[f,1],tri[f,2]);d=wp.length_sq(p-c)
  if d<best:best=d;face=f;q=c
 r=Signed();length=wp.sqrt(best);r.phi=-length
 if length>wp.float64(1e-15):r.normal=-(p-q)/length
 else:r.normal=wp.normalize(wp.cross(tri[face,1]-tri[face,0],tri[face,2]-tri[face,0]))
 return r

@wp.kernel
def query_grid(tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),origin:wp.vec3d,shape:wp.vec3i,h:wp.float64,points:wp.array(dtype=wp.vec3d),phi:wp.array(dtype=wp.float64),normal:wp.array(dtype=wp.vec3d)):
 i=wp.tid();r=signed_grid(tri,ptr,ids,origin,shape,h,points[i]);phi[i]=r.phi;normal[i]=r.normal

class GridCandidates:
 def __init__(self,cad,path=None,h=.001):
  path=path or Path(__file__).resolve().parents[1]/'assets/cad_grid_candidates_1mm.npz';digest=hashlib.sha256(cad.vertices.tobytes()+cad.faces.tobytes()).hexdigest();start=time.perf_counter()
  if path.exists():
   z=np.load(path,allow_pickle=False)
   if str(z['cad_sha256'])!=digest or float(z['h'])!=h:raise ValueError('knife candidate index does not match CAD')
   origin=z['origin'];shape=z['shape'];ptr=z['ptr'];ids=z['ids']
  else:
   origin=np.floor(cad.vertices.min(0)/h)*h-h;shape=np.ceil((cad.vertices.max(0)-origin)/h).astype(np.int32)+1;n=int(np.prod(shape));counts=wp.empty(n,dtype=int,device='cuda:0');dense=wp.empty((n,64),dtype=int,device='cuda:0');overflow=wp.zeros(1,dtype=int,device='cuda:0');tri=wp.array(cad.vertices[cad.faces],dtype=wp.vec3d,device='cuda:0');wp.launch(build_candidates,n,[tri,wp.vec3d(origin),wp.vec3i(shape),h,counts,dense,overflow]);count=counts.numpy()
   if overflow.numpy()[0] or count.min()==0:raise ValueError('candidate grid capacity/coverage failure')
   ptr=np.r_[0,np.cumsum(count)].astype(np.int32);x=dense.numpy();ids=x[np.arange(64)[None,:]<count[:,None]];np.savez_compressed(path,cad_sha256=digest,h=h,origin=origin,shape=shape,ptr=ptr,ids=ids)
  self.origin=origin;self.shape=shape;self.h=h;self.ptr=wp.array(ptr,dtype=int,device='cuda:0');self.ids=wp.array(ids,dtype=int,device='cuda:0');count=np.diff(ptr);self.report=dict(voxels=len(count),candidate_mean=float(count.mean()),candidate_max=int(count.max()),bytes=int(ptr.nbytes+ids.nbytes),wall_s=time.perf_counter()-start,cad_sha256=digest)
