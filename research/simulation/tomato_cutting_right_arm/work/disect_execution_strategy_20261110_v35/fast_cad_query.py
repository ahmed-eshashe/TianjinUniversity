"""Candidate allocation-free version of the same closest-point/winding query.

Float64, no fastmath, all triangles in the original order, same 1e-30 geometry
and 1e-6 winding tests. Independent points may run in parallel. No distance
truncation, approximate sign, triangle pruning, geometry or physics change.
An exact-content cache avoids recomputing constant triangle geometry.
"""
import math,hashlib,numpy as np
from numba import njit,prange
_cache={}
@njit(cache=True,parallel=True)
def _kernel(tri,edge,coeff,points):
 n=len(points);phi=np.zeros(n);normal=np.zeros((n,3));closest=np.zeros((n,3));face=np.zeros(n,np.int64);winding=np.zeros(n);errors=np.zeros(n,np.int64)
 for i in prange(n):
  px,py,pz=points[i];best=math.inf;total=0.;bx=0.;by=0.;bz=0.;which=0
  for j in range(len(tri)):
   ax,ay,az=tri[j,0];cx0,cy0,cz0=tri[j,1];cx1,cy1,cz1=tri[j,2]
   e0x,e0y,e0z=edge[j,0];e1x,e1y,e1z=edge[j,1];aa,ab,bb,det=coeff[j]
   rx=px-ax;ry=py-ay;rz=pz-az;ra=rx*e0x+ry*e0y+rz*e0z;rb=rx*e1x+ry*e1y+rz*e1z
   u=(ra*bb-rb*ab)/det;w=(rb*aa-ra*ab)/det
   qx=ax+u*e0x+w*e1x;qy=ay+u*e0y+w*e1y;qz=az+u*e0z+w*e1z
   dx=px-qx;dy=py-qy;dz=pz-qz;dist=dx*dx+dy*dy+dz*dz
   if u<0 or w<0 or u+w>1:dist=math.inf
   for k in range(3):
    k1=(k+1)%3;fx,fy,fz=tri[j,k];gx,gy,gz=tri[j,k1];ex=gx-fx;ey=gy-fy;ez=gz-fz
    t=min(1.,max(0.,((px-fx)*ex+(py-fy)*ey+(pz-fz)*ez)/(ex*ex+ey*ey+ez*ez)))
    xx=fx+t*ex;yy=fy+t*ey;zz=fz+t*ez;dx=px-xx;dy=py-yy;dz=pz-zz;dd=dx*dx+dy*dy+dz*dz
    if dd<dist:dist=dd;qx=xx;qy=yy;qz=zz
   if dist<best:best=dist;bx=qx;by=qy;bz=qz;which=j
   rax=ax-px;ray=ay-py;raz=az-pz;rbx=cx0-px;rby=cy0-py;rbz=cz0-pz;rcx=cx1-px;rcy=cy1-py;rcz=cz1-pz
   la=math.sqrt(rax*rax+ray*ray+raz*raz);lb=math.sqrt(rbx*rbx+rby*rby+rbz*rbz);lc=math.sqrt(rcx*rcx+rcy*rcy+rcz*rcz)
   numerator=rax*(rby*rcz-rbz*rcy)+ray*(rbz*rcx-rbx*rcz)+raz*(rbx*rcy-rby*rcx)
   denominator=la*lb*lc+(rax*rbx+ray*rby+raz*rbz)*lc+(rbx*rcx+rby*rcy+rbz*rcz)*la+(rcx*rax+rcy*ray+rcz*raz)*lb
   total+=2*math.atan2(numerator,denominator)
  wind=total/(4*math.pi);winding[i]=wind
  if min(abs(wind),abs(abs(wind)-1))>1e-6:errors[i]=1
  sign=-1. if abs(wind)>.5 else 1.;distance=math.sqrt(best);phi[i]=sign*distance;closest[i,0]=bx;closest[i,1]=by;closest[i,2]=bz;face[i]=which
  if distance>1e-15:normal[i,0]=sign*(px-bx)/distance;normal[i,1]=sign*(py-by)/distance;normal[i,2]=sign*(pz-bz)/distance
 return phi,normal,closest,face,winding,errors

def fast_query(vertices,faces,points):
 v=np.ascontiguousarray(vertices,dtype=np.float64);f=np.ascontiguousarray(faces,dtype=np.int64);p=np.ascontiguousarray(points,dtype=np.float64).reshape(-1,3)
 if not len(p):return np.zeros(0),np.zeros((0,3)),np.zeros((0,3)),np.zeros(0,np.int64),np.zeros(0)
 # Content hash, not object identity: in-place vertex/face edits invalidate it.
 key=(v.shape,f.shape,hashlib.sha256(v.tobytes()+f.tobytes()).digest())
 if _cache.get('key')!=key:
  tri=v[f].copy();edge=tri[:,1:]-tri[:,0,None];e0,e1=edge[:,0],edge[:,1];aa=np.einsum('ij,ij->i',e0,e0);ab=np.einsum('ij,ij->i',e0,e1);bb=np.einsum('ij,ij->i',e1,e1);det=aa*bb-ab*ab
  if (det<=1e-30).any():raise ValueError('Degenerate CAD triangle')
  _cache.clear();_cache.update(key=key,tri=tri,edge=edge,coeff=np.column_stack((aa,ab,bb,det)))
 values=_kernel(_cache['tri'],_cache['edge'],_cache['coeff'],p)
 if values[-1].any():raise ValueError('Uncertain solid-angle sign')
 return values[:-1]
