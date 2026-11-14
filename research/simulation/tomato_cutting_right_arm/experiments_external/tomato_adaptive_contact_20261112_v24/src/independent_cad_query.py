"""Compiled independent host CAD query, same distance/solid-angle formulas.

No fastmath, distance truncation, geometry approximation or changed sign rule.
Validated against the original NumPy query before use in contact remapping.
"""
import numpy as np
from numba import njit
import math

@njit(cache=True)
def _query(v,faces,points):
 n=len(points);phi=np.zeros(n);normal=np.zeros((n,3));closest=np.zeros((n,3));face=np.zeros(n,np.int64);winding=np.zeros(n)
 for i in range(n):
  p=points[i];best=math.inf;total=0.
  for j in range(len(faces)):
   a=v[faces[j,0]];b=v[faces[j,1]];c=v[faces[j,2]];e0=b-a;e1=c-a;r=p-a
   aa=np.dot(e0,e0);ab=np.dot(e0,e1);bb=np.dot(e1,e1);det=aa*bb-ab*ab
   if det<=1e-30:raise ValueError('Degenerate CAD triangle')
   u=(np.dot(r,e0)*bb-np.dot(r,e1)*ab)/det;w=(np.dot(r,e1)*aa-np.dot(r,e0)*ab)/det
   q=a+u*e0+w*e1;dist=np.dot(p-q,p-q)
   if u<0 or w<0 or u+w>1:dist=math.inf
   for edge_id in range(3):
    f=a;g=b
    if edge_id==1:f=b;g=c
    elif edge_id==2:f=c;g=a
    edge=g-f;t=min(1.,max(0.,np.dot(p-f,edge)/np.dot(edge,edge)));candidate=f+t*edge;dd=np.dot(p-candidate,p-candidate)
    if dd<dist:dist=dd;q=candidate
   if dist<best:best=dist;closest[i]=q;face[i]=j
   ra=a-p;rb=b-p;rc=c-p;la=np.sqrt(np.dot(ra,ra));lb=np.sqrt(np.dot(rb,rb));lc=np.sqrt(np.dot(rc,rc))
   numerator=np.dot(ra,np.cross(rb,rc));denominator=la*lb*lc+np.dot(ra,rb)*lc+np.dot(rb,rc)*la+np.dot(rc,ra)*lb
   total+=2*math.atan2(numerator,denominator)
  wind=total/(4*math.pi);winding[i]=wind
  if min(abs(wind),abs(abs(wind)-1))>1e-6:raise ValueError('Uncertain solid-angle sign')
  sign=-1. if abs(wind)>.5 else 1.;distance=math.sqrt(best);phi[i]=sign*distance
  if distance>1e-15:normal[i]=sign*(p-closest[i])/distance
 return phi,normal,closest,face,winding

def query_mesh(vertices,faces,points):
 p=np.asarray(points,dtype=float).reshape(-1,3)
 if not np.isfinite(p).all():raise ValueError('Finite query points required')
 values=_query(np.asarray(vertices,dtype=float),np.asarray(faces,dtype=np.int64),p)
 return dict(zip(['phi','normal','closest','face','winding'],values))
