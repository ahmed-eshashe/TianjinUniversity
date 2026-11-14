"""Experimental conservative exterior rejection for solver pressure only.
Every support plane contains every CAD vertex. Points beyond a support plane
are certainly outside every CAD triangle and have exactly zero contact energy,
force and Hessian. Interior and uncertain points use the original full query.
Positive exterior distances are support-plane bounds, not nearest distances;
face -1 denotes this rejection. Quadrature construction keeps the original
nearest-feature evaluator. No use is authorized by this module alone.
"""
import numpy as np
import warp as wp
from tomato_exact_blade_queries import closest
from tomato_fast_exact_cad import FastExactCADPressurePacket
from tomato_cached_cad_pressure import changed,validate
from tomato_cad_pressure import local_points
from tomato_global_pressure import scatter_double
from tomato_physical_pressure import pressure_packet
@wp.kernel(enable_backward=False)
def culled_query(planes:wp.array[wp.vec4d],v:wp.array[wp.vec3d],faces:wp.array[wp.vec3i],p:wp.array[wp.vec3d],phi:wp.array[wp.float64],normal:wp.array[wp.vec3d],qout:wp.array[wp.vec3d],face_out:wp.array[int],classification:wp.array[wp.float64]):
 i=wp.tid();point=p[i];best=wp.float64(1.e30);q=wp.vec3d(wp.float64(0.));chosen=int(-1);hits=int(0);ambiguous=int(0);ray=wp.vec3d(wp.float64(.137123793),wp.float64(.271867193),wp.float64(.953719271))
 for j in range(planes.shape[0]):
  plane=planes[j];n=wp.vec3d(plane[0],plane[1],plane[2]);distance=wp.dot(n,point)-plane[3]
  if distance>wp.float64(1.e-12):
   phi[i]=distance;normal[i]=n;qout[i]=point-distance*n;face_out[i]=-1;classification[i]=wp.float64(0.);return
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

class ExteriorCulledCADPressurePacket(FastExactCADPressurePacket):
 def set_cad(self,**kwargs):
  super().set_cad(**kwargs);self._valid=False
  key=np.asarray(kwargs['vertices'],dtype=float).tobytes()
  if not hasattr(self,'_plane_key') or self._plane_key!=key:
   from scipy.spatial import ConvexHull
   vertices=np.asarray(kwargs['vertices'],dtype=float);normals=ConvexHull(vertices).equations[:,:3]
   _,ids=np.unique(np.round(normals*10),axis=0,return_index=True);normals=normals[ids];normals=normals[np.argsort(-abs(normals[:,2]))]
   supports=np.max(vertices@normals.T,axis=0);self._planes=wp.array(np.c_[normals,supports],dtype=wp.vec4d);self._plane_key=key
  if not hasattr(self,'_saved_x'):self._saved_x=wp.empty(self.n,dtype=wp.vec3d);self._flag=wp.zeros(1,dtype=int)
 def pose(self,rotation,translation):
  super().pose(rotation,translation);self._valid=False
 def evaluate(self,x):
  if not self.count:self.force.zero_();return 0.
  if self._valid:
   self._flag.zero_();wp.launch(changed,dim=self.n,inputs=[x,self._saved_x],outputs=[self._flag],block_dim=64)
   if not self._flag.numpy()[0]:return self._energy
  self.normals.zero_();wp.launch(local_points,dim=self.count,inputs=[x,self.indices,self.bary,self.rotation,self.translation],outputs=[self.local],block_dim=64)
  wp.launch(culled_query,dim=self.count,inputs=[self._planes,self.vertices,self.faces,self.local],outputs=[self.phi,self.normals,self.points,self.face,self.winding],block_dim=64)
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
