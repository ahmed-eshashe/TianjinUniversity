"""Disjoint material-coordinate coverage of a conservatively padded CAD solid.

Each original tetrahedron's unit facet planes AND its axis bounds expand by h.
Their intersection contains its true h-neighbourhood; the union therefore
covers the solid's h-neighbourhood. Triangle-domain polygon subtraction assigns
overlapping expanded cells once. Positive original-reference-area quadrature
is fixed during an interval. Numerical geometry, force quadrature accuracy,
relative-motion bounds and integration still require separate qualifications.
"""
import numpy as np
from tomato_exact_blade_coverage import cell_planes,clip_polygon

def signed_uv_area(polygon):
 p=np.asarray(polygon)
 if len(p)<3:return 0.
 q=p[:,1:];return float(.5*np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1)))

def clip_uv(polygon,normal,anchor,*,inside):
 if len(polygon)<3:return []
 result=[];previous=polygon[-1];dp=normal@(previous[1:]-anchor)
 for current in polygon:
  dc=normal@(current[1:]-anchor);ip=dp<=0 if inside else dp>=0;ic=dc<=0 if inside else dc>=0
  if ip!=ic:result.append(previous+(dp/(dp-dc))*(current-previous))
  if ic:result.append(current)
  previous=current;dp=dc
 return result

def subtract_convex(polygon,covered):
 """Disjoint convex pieces of P minus a convex Q, in triangle barycentrics."""
 if len(polygon)<3:return []
 q=np.asarray(covered)
 if len(q)<3 or abs(signed_uv_area(q))<1e-24:return [polygon]
 if signed_uv_area(q)<0:q=q[::-1]
 remaining=polygon;pieces=[]
 for index,first in enumerate(q):
  last=q[(index+1)%len(q)];edge=last[1:]-first[1:]
  if np.linalg.norm(edge)<1e-15:continue
  normal=np.array([edge[1],-edge[0]]);outside=clip_uv(remaining,normal,first[1:],inside=False)
  if len(outside)>=3 and abs(signed_uv_area(outside))>1e-24:pieces.append(outside)
  remaining=clip_uv(remaining,normal,first[1:],inside=True)
  if len(remaining)<3 or abs(signed_uv_area(remaining))<1e-24:break
 return pieces

def padded_coverage(vertices,cells,positions,triangles,reference,*,padding_m=1e-5,level=1,capacity=131072,maximum_pieces_per_triangle=4096,split_fraction=np.sqrt(2.)-1.):
 v=np.asarray(vertices,dtype=float);cells=np.asarray(cells,dtype=int);x=np.asarray(positions,dtype=float);triangles=np.asarray(triangles,dtype=int);reference=np.asarray(reference,dtype=float)
 if not .2<=split_fraction<=.8 or not 0<=padding_m<=.001 or not 0<=level<=5 or not np.isfinite(v).all()or not np.isfinite(x).all()or not np.isfinite(reference).all():raise ValueError('Finite bounded padded material coverage required')
 planes=cell_planes(v,cells);points=v[cells];lo=points.min(1)-padding_m;hi=points.max(1)+padding_m;samples=[];polygons={};records=[]
 for ti,ids in enumerate(triangles):
  soft=x[ids];rest=reference[ids];physical_area=.5*np.linalg.norm(np.cross(soft[1]-soft[0],soft[2]-soft[0]));reference_area=.5*np.linalg.norm(np.cross(rest[1]-rest[0],rest[2]-rest[0]))
  if min(physical_area,reference_area)<=1e-20:raise ValueError('Degenerate tissue triangle in padded coverage')
  broad=np.flatnonzero(np.all(hi>=soft.min(0)-1e-12,1)&np.all(lo<=soft.max(0)+1e-12,1));previous=[];owned=[];raw_area=0.
  for cell in broad:
   polygon=[np.array([1.,0.,0.]),np.array([0.,1.,0.]),np.array([0.,0.,1.])]
   for n,a in planes[cell]:
    polygon=clip_polygon(polygon,soft,n,a+padding_m*n)
    if len(polygon)<3:break
   if len(polygon)<3:continue
   for axis in range(3):
    n=np.eye(3)[axis];a=np.zeros(3);a[axis]=hi[cell,axis];polygon=clip_polygon(polygon,soft,n,a);a[axis]=lo[cell,axis];polygon=clip_polygon(polygon,soft,-n,a)
    if len(polygon)<3:break
   if len(polygon)<3 or abs(signed_uv_area(polygon))<1e-24:continue
   raw_area+=2*abs(signed_uv_area(polygon))*reference_area;pieces=[polygon]
   for earlier in previous:
    pieces=[piece for current in pieces for piece in subtract_convex(current,earlier)]
    if len(pieces)>maximum_pieces_per_triangle:raise ValueError('Padded polygon ownership capacity exceeded')
    if not pieces:break
   previous.append(polygon);owned.extend(pieces)
   if len(owned)>maximum_pieces_per_triangle:raise ValueError('Padded polygon ownership capacity exceeded')
  if not owned:continue
  area=2*sum(abs(signed_uv_area(p))for p in owned)*reference_area
  if area>reference_area*(1+1e-8)+1e-18:raise ValueError('Padded union exceeds original material triangle area')
  polygons[ti]=[np.asarray(p).tolist()for p in owned];records.append(dict(triangle=ti,owned_polygons=len(owned),reference_area_m2=area,raw_duplicated_reference_area_m2=raw_area,physical_area_m2=area*physical_area/reference_area))
  for polygon in owned:
   local=[np.array([polygon[0],polygon[j],polygon[j+1]])for j in range(1,len(polygon)-1)]
   for _ in range(level):
    refined=[]
    for t in local:
     a,b,c=t;f=split_fraction;ab=(1-f)*a+f*b;bc=(1-f)*b+f*c;ca=(1-f)*c+f*a;refined.extend([np.array([a,ab,ca]),np.array([ab,b,bc]),np.array([ca,bc,c]),np.array([ab,bc,ca])])
    local=refined
   for t in local:
    material=t@rest;A=.5*np.linalg.norm(np.cross(material[1]-material[0],material[2]-material[0]))
    if A<=1e-24:continue
    for gauss in [(2/3,1/6,1/6),(1/6,2/3,1/6),(1/6,1/6,2/3)]:
     bary=np.asarray(gauss)@t
     if not np.isfinite(bary).all()or bary.min()<-1e-12 or abs(bary.sum()-1)>1e-12:raise ValueError('Invalid positive material pressure quadrature')
     samples.append(dict(triangle_id=ti,corners=ids.tolist(),barycentric=bary.tolist(),area_m2=float(A/3),point_m=(bary@soft).tolist()))
     if len(samples)>=capacity:raise ValueError('Padded pressure sample capacity saturated')
 return dict(samples=samples,polygons_by_triangle=polygons,triangle_records=records,padding_m=padding_m,quadrature_level=level,subdivision_split_fraction=float(split_fraction),reference_area_m2=sum(r['reference_area_m2']for r in records),raw_duplicated_reference_area_m2=sum(r['raw_duplicated_reference_area_m2']for r in records),scope='Conservative expanded solid/material-domain union and fixed positive reference-area packet only; no collision, force, time-step or robot qualification.')
