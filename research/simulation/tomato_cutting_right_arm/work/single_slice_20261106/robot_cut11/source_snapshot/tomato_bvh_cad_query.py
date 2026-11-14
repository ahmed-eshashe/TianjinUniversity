"""Candidate exact-double blade BVH; not adopted in active cutting run.
Bounds only reject triangles that cannot be nearest or hit by the reference
ray. The original triangle distance, parity tolerances and winding fallback
are retained. Tree bounds include the reference ray barycentric tolerance.
"""
import numpy as np
import warp as wp
from tomato_exact_blade_queries import closest

def build_tree(vertices,faces):
 v=np.asarray(vertices,float);f=np.asarray(faces,int);tri=v[f];lo=[];hi=[];skip=[];leaf=[]
 # Envelope for u,v >= -1e-10 and u+v <=1+1e-10, plus ray origin band.
 pad=4e-10*np.max(np.ptp(tri,axis=1),axis=0)+1e-12
 centers=tri.mean(1)
 def build(ids):
  n=len(leaf);lo.append(tri[ids].min((0,1))-pad);hi.append(tri[ids].max((0,1))+pad);skip.append(-1);leaf.append(int(ids[0]) if len(ids)==1 else -1)
  if len(ids)>1:
   axis=int(np.argmax(np.ptp(centers[ids],axis=0)));ids=ids[np.argsort(centers[ids,axis],kind='stable')];m=len(ids)//2;build(ids[:m]);build(ids[m:])
  skip[n]=len(leaf)
 build(np.arange(len(f)))
 ray=np.array([.137123793,.271867193,.953719271]);det=np.einsum('ij,ij->i',tri[:,1]-tri[:,0],np.cross(ray,tri[:,2]-tri[:,0]));ambiguous=int(np.any(abs(det)<=1e-25))
 return np.array(lo),np.array(hi),np.array(skip,np.int32),np.array(leaf,np.int32),ambiguous

@wp.kernel(enable_backward=False)
def bvh_query(lower_bounds:wp.array[wp.vec3d],upper_bounds:wp.array[wp.vec3d],skip:wp.array[int],leaf:wp.array[int],global_ambiguous:int,v:wp.array[wp.vec3d],faces:wp.array[wp.vec3i],p:wp.array[wp.vec3d],phi:wp.array[wp.float64],normal:wp.array[wp.vec3d],qout:wp.array[wp.vec3d],face_out:wp.array[int],classification:wp.array[wp.float64]):
 i=wp.tid();point=p[i];best=wp.float64(1.e30);q=wp.vec3d(wp.float64(0.));chosen=int(-1);hits=int(0);ambiguous=global_ambiguous;ray=wp.vec3d(wp.float64(.137123793),wp.float64(.271867193),wp.float64(.953719271))
 node=int(0)
 while node<leaf.shape[0]:
  bound=wp.float64(0.);near_t=wp.float64(-1.e-12);far_t=wp.float64(1.e30)
  for axis in range(3):
   lo=lower_bounds[node][axis];hi=upper_bounds[node][axis];gap=wp.max(wp.float64(0.),wp.max(lo-point[axis],point[axis]-hi));bound+=gap*gap
   near_t=wp.max(near_t,(lo-point[axis])/ray[axis]);far_t=wp.min(far_t,(hi-point[axis])/ray[axis])
  if bound>best+wp.float64(1.e-28) and near_t>far_t:
   node=skip[node];continue
  f=leaf[node];node+=1
  if f<0:continue
  ids=faces[f];a=v[ids[0]];b=v[ids[1]];c=v[ids[2]];lower=wp.float64(0.)
  for axis in range(3):
   lo=wp.min(a[axis],wp.min(b[axis],c[axis]));hi=wp.max(a[axis],wp.max(b[axis],c[axis]));gap=wp.max(wp.float64(0.),wp.max(lo-point[axis],point[axis]-hi));lower+=gap*gap
  if lower<=best+wp.float64(1.e-28):
   near=closest(a,b,c,point);delta=point-near;dd=wp.dot(delta,delta)
   if dd<best or (dd==best and f<chosen):best=dd;q=near;chosen=f
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
