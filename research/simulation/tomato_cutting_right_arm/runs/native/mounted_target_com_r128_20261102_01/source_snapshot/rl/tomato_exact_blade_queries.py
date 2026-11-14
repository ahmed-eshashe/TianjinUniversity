"""Native all-exterior-facet float64 distances and solid-angle signs."""
import warp as wp
from tomato_mesh_double_query import make_closest_function
closest=make_closest_function()

@wp.kernel
def query(v:wp.array[wp.vec3d],faces:wp.array[wp.vec3i],p:wp.array[wp.vec3d],phi:wp.array[wp.float64],normal:wp.array[wp.vec3d],qout:wp.array[wp.vec3d],face_out:wp.array[int],winding:wp.array[wp.float64]):
 i=wp.tid();best=wp.float64(1.e30);q=wp.vec3d(wp.float64(0.));chosen=int(-1);angle=wp.float64(0.)
 for f in range(faces.shape[0]):
  ids=faces[f];a=v[ids[0]];b=v[ids[1]];c=v[ids[2]];point=closest(a,b,c,p[i]);delta=p[i]-point;d=wp.dot(delta,delta)
  if d<best:best=d;q=point;chosen=f
  aa=a-p[i];bb=b-p[i];cc=c-p[i];la=wp.length(aa);lb=wp.length(bb);lc=wp.length(cc)
  numerator=wp.dot(aa,wp.cross(bb,cc));denominator=la*lb*lc+wp.dot(aa,bb)*lc+wp.dot(bb,cc)*la+wp.dot(cc,aa)*lb
  angle+=wp.float64(2.)*wp.atan2(numerator,denominator)
 w=angle/wp.float64(12.566370614359172);winding[i]=w;sign=wp.float64(1.)
 if wp.abs(w)>wp.float64(.5):sign=wp.float64(-1.)
 length=wp.sqrt(best);phi[i]=sign*length;qout[i]=q;face_out[i]=chosen
 if length>wp.float64(1.e-15):normal[i]=sign*(p[i]-q)/length

def sample(vertices,faces,points):
 import numpy as np
 p=wp.array(points,dtype=wp.vec3d);n=len(points);phi=wp.empty(n,dtype=wp.float64);normal=wp.empty(n,dtype=wp.vec3d);q=wp.empty(n,dtype=wp.vec3d);f=wp.empty(n,dtype=int);w=wp.empty(n,dtype=wp.float64)
 wp.launch(query,dim=n,inputs=[wp.array(vertices,dtype=wp.vec3d),wp.array(faces,dtype=wp.vec3i),p],outputs=[phi,normal,q,f,w]);wp.synchronize()
 result=dict(phi=phi.numpy(),normal=normal.numpy(),closest=q.numpy(),face=f.numpy(),winding=w.numpy())
 if not all(np.isfinite(v).all() for v in result.values()) or np.any(np.minimum(abs(result['winding']),abs(abs(result['winding'])-1))>1e-6):raise ValueError('Uncertain float64 winding query')
 return result
