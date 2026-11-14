"""Bounded 4M-sample allocation; inherited exact query and force evaluation.
Only the allocation limit differs from the original cached pressure packet.
"""
import numpy as np
import warp as wp
from tomato_cached_cad_pressure import CachedCADPressurePacket
from tomato_global_pressure import FrozenPressurePacket
class CapacityCADPressurePacket(CachedCADPressurePacket):
 def set_cad(self,*,vertices,triangles,indices,barycentric,areas,rotation,translation,com_local,source_scope):
  v=np.asarray(vertices,dtype=float);f=np.asarray(triangles,dtype=np.int32);n=len(areas)
  if v.shape!=(74,3)or f.shape!=(144,3)or not np.isfinite(v).all()or np.any(f<0)or np.any(f>=len(v))or n>4194304:raise ValueError('Qualified closed authored CAD/capacity required')
  # Reuse validation/allocation; feature arrays are overwritten by every query.
  FrozenPressurePacket.set(self,indices=indices,barycentric=barycentric,areas=areas,closest_local=np.zeros((n,3)),normals_local=np.tile([1.,0,0],(n,1)),rotation=rotation,translation=translation,com_local=com_local,source_scope=source_scope)
  self.vertices=wp.array(v,dtype=wp.vec3d);self.faces=wp.array(f,dtype=wp.vec3i);self.local=wp.empty(n,dtype=wp.vec3d);self.phi=wp.zeros(n,dtype=wp.float64);self.face=wp.empty(n,dtype=int);self.winding=wp.empty(n,dtype=wp.float64)
  self._valid=False
  if not hasattr(self,'_saved_x'):self._saved_x=wp.empty(self.n,dtype=wp.vec3d);self._flag=wp.zeros(1,dtype=int)
