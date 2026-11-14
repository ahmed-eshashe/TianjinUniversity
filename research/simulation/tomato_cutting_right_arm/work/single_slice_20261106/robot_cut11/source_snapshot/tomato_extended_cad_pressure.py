"""Larger bounded CAD quadrature capacity; original geometry and force law unchanged."""
import numpy as np
import warp as wp
from tomato_exact_blade_queries import query
from tomato_global_pressure import FrozenPressurePacket,GlobalPressureCandidate

@wp.kernel(enable_backward=False)
def local_points(x:wp.array[wp.vec3d],ids:wp.array[wp.vec3i],bary:wp.array[wp.vec3d],R:wp.array[wp.mat33d],t:wp.array[wp.vec3d],points:wp.array[wp.vec3d]):
 i=wp.tid();a=ids[i];w=bary[i];p=w[0]*x[a[0]]+w[1]*x[a[1]]+w[2]*x[a[2]];points[i]=wp.transpose(R[0])*(p-t[0])

class ExtendedCADPressurePacket(FrozenPressurePacket):
 def set_cad(self,*,vertices,triangles,indices,barycentric,areas,rotation,translation,com_local,source_scope):
  v=np.asarray(vertices,dtype=float);f=np.asarray(triangles,dtype=np.int32);n=len(areas)
  if v.shape!=(74,3)or f.shape!=(144,3)or not np.isfinite(v).all()or np.any(f<0)or np.any(f>=len(v))or n>2097152:raise ValueError('Qualified closed authored CAD/capacity required')
  # Reuse validation/allocation; feature arrays are overwritten by every query.
  super().set(indices=indices,barycentric=barycentric,areas=areas,closest_local=np.zeros((n,3)),normals_local=np.tile([1.,0,0],(n,1)),rotation=rotation,translation=translation,com_local=com_local,source_scope=source_scope)
  self.vertices=wp.array(v,dtype=wp.vec3d);self.faces=wp.array(f,dtype=wp.vec3i);self.local=wp.empty(n,dtype=wp.vec3d);self.phi=wp.zeros(n,dtype=wp.float64);self.face=wp.empty(n,dtype=int);self.winding=wp.empty(n,dtype=wp.float64)
 def pose(self,rotation,translation):
  R=np.asarray(rotation,dtype=float);t=np.asarray(translation,dtype=float)
  if R.shape!=(3,3)or t.shape!=(3,)or not np.isfinite(R).all()or not np.isfinite(t).all()or np.max(abs(R.T@R-np.eye(3)))>1e-10 or abs(np.linalg.det(R)-1)>1e-10:raise ValueError('Proper finite rigid pose required')
  self.rotation.assign(R[None]);self.translation.assign(t[None])
 def evaluate(self,x):
  if not self.count:return super().evaluate(x)
  self.normals.zero_()
  wp.launch(local_points,dim=self.count,inputs=[x,self.indices,self.bary,self.rotation,self.translation],outputs=[self.local],block_dim=64)
  wp.launch(query,dim=self.count,inputs=[self.vertices,self.faces,self.local],outputs=[self.phi,self.normals,self.points,self.face,self.winding],block_dim=64)
  # Fail closed on ambiguous solid signs; use actual double closest features.
  phi=self.phi.numpy();w=self.winding.numpy();normals=self.normals.numpy()
  if not np.isfinite(phi).all()or not np.isfinite(normals).all()or not np.isfinite(w).all()or np.max(np.minimum(abs(w),abs(abs(w)-1)),initial=0)>1e-6 or np.any((phi<0)&(abs(np.linalg.norm(normals,axis=1)-1)>1e-9)):raise ValueError('Uncertain actual-CAD pressure query')
  return super().evaluate(x)

