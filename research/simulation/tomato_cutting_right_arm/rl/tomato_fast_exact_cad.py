"""Float64 exterior distance with ray parity and solid-angle fallback.

Triangle AABBs cull only impossible nearest features. Ambiguous ray edge,
vertex or on-surface hits fall back to the original solid-angle sign.
This changes query execution, not blade geometry or the pressure law.
"""
import numpy as np
import warp as wp
from tomato_exact_blade_queries import closest
from tomato_extended_cad_pressure import ExtendedCADPressurePacket
from tomato_global_pressure import FrozenPressurePacket
from tomato_cad_pressure import local_points

@wp.kernel(enable_backward=False)
def fast_query(v:wp.array[wp.vec3d],faces:wp.array[wp.vec3i],p:wp.array[wp.vec3d],phi:wp.array[wp.float64],normal:wp.array[wp.vec3d],qout:wp.array[wp.vec3d],face_out:wp.array[int],classification:wp.array[wp.float64]):
 i=wp.tid();point=p[i];best=wp.float64(1.e30);q=wp.vec3d(wp.float64(0.));chosen=int(-1);hits=int(0);ambiguous=int(0);ray=wp.vec3d(wp.float64(.137123793),wp.float64(.271867193),wp.float64(.953719271))
 for f in range(faces.shape[0]):
  ids=faces[f];a=v[ids[0]];b=v[ids[1]];c=v[ids[2]];lower=wp.float64(0.)
  for axis in range(3):
   lo=wp.min(a[axis],wp.min(b[axis],c[axis]));hi=wp.max(a[axis],wp.max(b[axis],c[axis]));gap=wp.max(wp.float64(0.),wp.max(lo-point[axis],point[axis]-hi));lower+=gap*gap
  if lower<=best+wp.float64(1.e-28):
   near=closest(a,b,c,point);delta=point-near;dd=wp.dot(delta,delta)
   if dd<best:best=dd;q=near;chosen=f
  e1=b-a;e2=c-a;h=wp.cross(ray,e2);det=wp.dot(e1,h)
  if wp.abs(det)>wp.float64(1.e-25):
   s=point-a;u=wp.dot(s,h)/det
   if u>=wp.float64(-1.e-10) and u<=wp.float64(1.+1.e-10):
    cross=wp.cross(s,e1);vv=wp.dot(ray,cross)/det
    if vv>=wp.float64(-1.e-10) and u+vv<=wp.float64(1.+1.e-10):
     along=wp.dot(e2,cross)/det
     if along>=wp.float64(-1.e-12):
      if u<wp.float64(1.e-10) or vv<wp.float64(1.e-10) or wp.float64(1.)-u-vv<wp.float64(1.e-10) or along<wp.float64(1.e-12):ambiguous=1
      elif along>wp.float64(0.):hits+=1
  else:ambiguous=1
 inside=wp.float64(hits%2)
 if ambiguous!=0:
  angle=wp.float64(0.)
  for f in range(faces.shape[0]):
   ids=faces[f];aa=v[ids[0]]-point;bb=v[ids[1]]-point;cc=v[ids[2]]-point;la=wp.length(aa);lb=wp.length(bb);lc=wp.length(cc)
   angle+=wp.float64(2.)*wp.atan2(wp.dot(aa,wp.cross(bb,cc)),la*lb*lc+wp.dot(aa,bb)*lc+wp.dot(bb,cc)*la+wp.dot(cc,aa)*lb)
  inside=angle/wp.float64(12.566370614359172)
 classification[i]=inside;sign=wp.float64(1.)
 if wp.abs(inside)>wp.float64(.5):sign=wp.float64(-1.)
 length=wp.sqrt(best);phi[i]=sign*length;qout[i]=q;face_out[i]=chosen
 if length>wp.float64(1.e-15):normal[i]=sign*(point-q)/length
 else:phi[i]=wp.float64(0.);classification[i]=wp.float64(0.) # Existing zero-normal roundoff band: boundary pressure is exactly zero.

class FastExactCADPressurePacket(ExtendedCADPressurePacket):
 def evaluate(self,x):
  if not self.count:return FrozenPressurePacket.evaluate(self,x)
  self.normals.zero_();wp.launch(local_points,dim=self.count,inputs=[x,self.indices,self.bary,self.rotation,self.translation],outputs=[self.local],block_dim=64)
  wp.launch(fast_query,dim=self.count,inputs=[self.vertices,self.faces,self.local],outputs=[self.phi,self.normals,self.points,self.face,self.winding],block_dim=64)
  phi=self.phi.numpy();classification=self.winding.numpy();normals=self.normals.numpy()
  if not np.isfinite(phi).all() or not np.isfinite(normals).all() or not np.isfinite(classification).all() or np.max(np.minimum(abs(classification),abs(abs(classification)-1)),initial=0)>1e-6 or np.any((phi<0)&(abs(np.linalg.norm(normals,axis=1)-1)>1e-9)):raise ValueError('Uncertain exact CAD sign/distance')
  return FrozenPressurePacket.evaluate(self,x)
