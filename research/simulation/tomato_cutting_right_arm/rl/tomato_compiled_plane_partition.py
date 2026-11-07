"""Compiled quadrature-only plane partition; preserves reference implementation."""
import numpy as np
from numba import njit
from tomato_contact_plane_partition import uv_area

@njit(cache=True)
def area(p):
 total=0.
 for j in range(1,len(p)-1):
  a=p[j]-p[0];b=p[j+1]-p[0];total+=a[1]*b[2]-a[2]*b[1]
 return abs(.5*total)

@njit(cache=True)
def clip(p,soft,n,d):
 out=np.empty((2*len(p)+2,3));count=0;prev=p[-1];dp=n@(prev@soft-n*d)
 for curr in p:
  dc=n@(curr@soft-n*d);ip=dp<=0.;ic=dc<=0.
  if ip!=ic:
   out[count]=prev+(dp/(dp-dc))*(curr-prev);count+=1
  if ic:out[count]=curr;count+=1
  prev=curr;dp=dc
 return out[:count].copy()

@njit(cache=True)
def compute(ids,leaves,areas,x,rotation,translation,normals,offsets):
 new_ids=[];new_cells=[];new_areas=[];fallbacks=0
 for z in range(len(leaves)):
  index=ids[z];leaf=leaves[z];A=areas[z];soft=(x[index]-translation)@rotation;pieces=[leaf.copy()]
  for h in range(len(normals)):
   normal=normals[h];d=offsets[h];next_pieces=[]
   for poly in pieces:
    distances=(poly@soft)@normal-d
    if distances.min()>=-1e-13 or distances.max()<=1e-13:
     next_pieces.append(poly);continue
    for sign in (1.,-1.):
     clipped=clip(poly,soft,sign*normal,sign*d)
     if len(clipped)>=3 and area(clipped)>1e-28:next_pieces.append(clipped)
   pieces=next_pieces
   if len(pieces)>4096:raise ValueError('Material plane partition capacity exceeded')
  cells=[];weights=[]
  for poly in pieces:
   for j in range(1,len(poly)-1):
    c=np.empty((3,3));c[0]=poly[0];c[1]=poly[j];c[2]=poly[j+1];v=area(c)
    if v>1e-28:cells.append(c);weights.append(v)
  root_area=area(leaf)
  if not cells:cells=[leaf.copy()];weights=[root_area if root_area>0 else 1.]
  elif abs(sum(weights)-root_area)>1e-9*root_area+1e-24:
   cells=[leaf.copy()];weights=[1.];fallbacks+=1
  total=sum(weights)
  for cell,weight in zip(cells,weights):
   new_ids.append(index.copy());new_cells.append(cell);new_areas.append(weight/total*A)
 return new_ids,new_cells,new_areas,fallbacks

def partition(blade,ids,leaves,areas,x,rotation,translation,face_ids):
 vertices=np.asarray(blade['vertices']);faces=np.asarray(blade['triangles']);planes=[]
 for face in face_ids:
  a,b,c=vertices[faces[int(face)]];n=np.cross(b-a,c-a);n/=np.linalg.norm(n);d=float(n@a)
  if not any(np.linalg.norm(n-old_n)<1e-6 and abs(d-old_d)<1e-8 for old_n,old_d in planes):planes.append((n,d))
 original=list(planes)
 for i,(n,d) in enumerate(original):
  for m,e in original[i+1:]:
   normal=n-m;length=np.linalg.norm(normal)
   if length>1e-6:planes.append((normal/length,(d-e)/length))
 ni,nc,na,fallbacks=compute(np.asarray(ids),np.asarray(leaves),np.asarray(areas),np.asarray(x),np.asarray(rotation),np.asarray(translation),np.asarray([p[0]for p in planes]).reshape(-1,3),np.asarray([p[1]for p in planes]))
 if abs(sum(na)-sum(areas))>1e-12*max(sum(areas),1e-12):raise ValueError('Partition lost material reference area')
 return np.asarray(ni),np.asarray(nc),np.asarray(na),dict(unpartitioned_roundoff_fallbacks=fallbacks,face_planes=len(original),partition_planes=len(planes),original_cells=len(leaves),partitioned_cells=len(nc))
