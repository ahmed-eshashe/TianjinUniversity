"""Reuse CAD pressure only for bit-identical coordinates and unchanged packet/pose.

GPU validation retains the original finite/sign/normal checks. Coordinates are
compared, not merely pointers, so nonlinear trial buffer reuse cannot hit stale
forces. Energy uses a double GPU reduction instead of a full host copy.
"""
import warp as wp
import numpy as np
from tomato_fast_exact_cad import FastExactCADPressurePacket,fast_query
from tomato_cad_pressure import local_points
from tomato_global_pressure import scatter_double
from tomato_physical_pressure import pressure_packet

@wp.kernel(enable_backward=False)
def changed(x:wp.array[wp.vec3d],old:wp.array[wp.vec3d],flag:wp.array[int]):
 i=wp.tid()
 if x[i][0]!=old[i][0] or x[i][1]!=old[i][1] or x[i][2]!=old[i][2]:wp.atomic_add(flag,0,1)

@wp.kernel(enable_backward=False)
def validate(phi:wp.array[wp.float64],normal:wp.array[wp.vec3d],classification:wp.array[wp.float64],bad:wp.array[int]):
 i=wp.tid();v=classification[i];invalid=not wp.isfinite(phi[i]) or not wp.isfinite(v)
 for j in range(3):
  if not wp.isfinite(normal[i][j]):invalid=True
 if wp.min(wp.abs(v),wp.abs(wp.abs(v)-wp.float64(1.)))>wp.float64(1e-6):invalid=True
 if phi[i]<wp.float64(0.) and wp.abs(wp.length(normal[i])-wp.float64(1.))>wp.float64(1e-9):invalid=True
 if invalid:wp.atomic_add(bad,0,1)

class CachedCADPressurePacket(FastExactCADPressurePacket):
 def set_cad(self,**kwargs):
  super().set_cad(**kwargs);self._valid=False
  if not hasattr(self,'_saved_x'):self._saved_x=wp.empty(self.n,dtype=wp.vec3d);self._flag=wp.zeros(1,dtype=int)
 def pose(self,rotation,translation):
  super().pose(rotation,translation);self._valid=False
 def evaluate(self,x):
  if not self.count:self.force.zero_();return 0.
  if self._valid:
   self._flag.zero_();wp.launch(changed,dim=self.n,inputs=[x,self._saved_x],outputs=[self._flag],block_dim=64)
   if not self._flag.numpy()[0]:return self._energy
  self.normals.zero_();wp.launch(local_points,dim=self.count,inputs=[x,self.indices,self.bary,self.rotation,self.translation],outputs=[self.local],block_dim=64)
  wp.launch(fast_query,dim=self.count,inputs=[self.vertices,self.faces,self.local],outputs=[self.phi,self.normals,self.points,self.face,self.winding],block_dim=64)
  self._flag.zero_();wp.launch(validate,dim=self.count,inputs=[self.phi,self.normals,self.winding],outputs=[self._flag],block_dim=64)
  if self._flag.numpy()[0]:
   phi=self.phi.numpy();cl=self.winding.numpy();normals=self.normals.numpy()
   if not(np.isfinite(phi).all() and np.isfinite(cl).all() and np.isfinite(normals).all()) or np.any((phi<0)&(abs(np.linalg.norm(normals,axis=1)-1)>1e-9)):raise ValueError('Nonfinite CAD query or invalid unit normal')
   uncertain=np.flatnonzero(np.minimum(abs(cl),abs(abs(cl)-1))>1e-6)
   from tomato_rational_cad_sign import classify
   vertices=self.vertices.numpy();faces=self.faces.numpy();points=self.local.numpy()
   for index in uncertain:
    sign=classify(vertices,faces,points[index]);distance=abs(phi[index]);oldsign=-1 if phi[index]<0 else 1
    if sign==0:phi[index]=0.;normals[index]=0.;cl[index]=0.
    else:phi[index]=sign*distance;normals[index]*=sign/oldsign;cl[index]=1. if sign<0 else 0.
   self.phi.assign(phi);self.normals.assign(normals);self.winding.assign(cl)
   self.exact_sign_fallback_count=getattr(self,'exact_sign_fallback_count',0)+len(uncertain)
   self._flag.zero_();wp.launch(validate,dim=self.count,inputs=[self.phi,self.normals,self.winding],outputs=[self._flag],block_dim=64)
   if self._flag.numpy()[0]:raise ValueError('Exact sign fallback did not satisfy original CAD validation')
  self.force.zero_();wp.launch(pressure_packet,dim=self.count,inputs=[x,self.indices,self.bary,self.area,self.points,self.normals,self.rotation,self.translation,self.com],outputs=[self.sample_force,self.sample_hessian,self.body_force,self.body_torque,self.energy],block_dim=64);wp.launch(scatter_double,dim=(self.count,3),inputs=[self.indices,self.bary,self.sample_force],outputs=[self.force],block_dim=64)
  self._energy=float(wp.utils.array_sum(self.energy));wp.copy(self._saved_x,x);self._valid=True
  return self._energy
