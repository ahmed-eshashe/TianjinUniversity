"""Partition quadrature domains, never physical geometry, at CAD feature planes.

Candidate face planes and pair bisectors are integration aids only. Every
resulting point still uses the exact CAD query; missed/merged partition planes
cannot alter geometry or forces, only quadrature efficiency. Root reference
area is retained exactly across positive subcells.
"""
import numpy as np
from tomato_exact_blade_coverage import clip_polygon

def uv_area(poly):
 p=np.asarray(poly)[:,1:];a=p[1:-1]-p[0];b=p[2:]-p[0];return abs(.5*np.sum(a[:,0]*b[:,1]-a[:,1]*b[:,0]))

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
 new_ids=[];new_cells=[];new_areas=[];fallbacks=0
 for index,leaf,A in zip(ids,leaves,areas):
  soft=(x[index]-translation)@rotation;pieces=[list(leaf)]
  for normal,d in planes:
   next_pieces=[]
   for poly in pieces:
    distances=(np.asarray(poly)@soft)@normal-d
    if distances.min()>=-1e-13 or distances.max()<=1e-13:next_pieces.append(poly);continue
    anchor=normal*d
    for sign in [1.,-1.]:
     clipped=clip_polygon(poly,soft,sign*normal,anchor)
     if len(clipped)>=3 and uv_area(clipped)>1e-28:next_pieces.append(clipped)
   pieces=next_pieces
   if len(pieces)>4096:raise ValueError('Material plane partition capacity exceeded')
  cells=[];weights=[]
  for poly in pieces:
   for j in range(1,len(poly)-1):
    c=np.array([poly[0],poly[j],poly[j+1]]);area=uv_area(c)
    if area>1e-28:cells.append(c);weights.append(area)
  root_area=uv_area(leaf)
  if not cells:cells=[leaf];weights=[root_area if root_area>0 else 1.]
  elif abs(sum(weights)-root_area)>1e-9*root_area+1e-24:cells=[leaf];weights=[1.];fallbacks+=1
  weights=np.asarray(weights);weights=weights/weights.sum()*A
  new_ids.extend([index]*len(cells));new_cells.extend(cells);new_areas.extend(weights)
 if abs(sum(new_areas)-sum(areas))>1e-12*max(sum(areas),1e-12):raise ValueError('Partition lost material reference area')
 return np.asarray(new_ids),np.asarray(new_cells),np.asarray(new_areas),dict(unpartitioned_roundoff_fallbacks=fallbacks,face_planes=len(original),partition_planes=len(planes),original_cells=len(leaves),partitioned_cells=len(new_cells))
