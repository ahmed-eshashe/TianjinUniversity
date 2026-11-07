"""Versioned compiled polygon arithmetic on the unchanged padded coverage."""
import numpy as np
from tomato_exact_blade_coverage import cell_planes
from tomato_compiled_polygon_ops import signed_uv_area,subtract_convex,clip_polygon

def padded_coverage(vertices,cells,positions,triangles,reference,*,padding_m=1e-5,level=1,capacity=131072,maximum_pieces_per_triangle=4096,split_fraction=np.sqrt(2.)-1.):
 v=np.asarray(vertices,dtype=float);cells=np.asarray(cells,dtype=int);x=np.asarray(positions,dtype=float);triangles=np.asarray(triangles,dtype=int);reference=np.asarray(reference,dtype=float)
 if not .2<=split_fraction<=.8 or not 0<=padding_m<=.001 or not 0<=level<=6 or not np.isfinite(v).all()or not np.isfinite(x).all()or not np.isfinite(reference).all():raise ValueError('Finite bounded padded material coverage required')
 planes=cell_planes(v,cells);points=v[cells];lo=points.min(1)-padding_m;hi=points.max(1)+padding_m;samples=[];polygons={};records=[]
 soft_all=x[triangles];soft_lo=soft_all.min(1);soft_hi=soft_all.max(1)
 rest_all=reference[triangles]
 for all_tri in [soft_all,rest_all]:
  if np.any(.5*np.linalg.norm(np.cross(all_tri[:,1]-all_tri[:,0],all_tri[:,2]-all_tri[:,0]),axis=1)<=1e-20):raise ValueError('Degenerate tissue triangle in padded coverage')
 broad_mask=np.all(hi[None,:,:]>=soft_lo[:,None,:]-1e-12,2)&np.all(lo[None,:,:]<=soft_hi[:,None,:]+1e-12,2)
 for ti in np.flatnonzero(broad_mask.any(1)):
  ids=triangles[ti]
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
   local=np.asarray(local);material=local@rest
   areas=.5*np.linalg.norm(np.cross(material[:,1]-material[:,0],material[:,2]-material[:,0]),axis=1)
   gauss=np.asarray([(2/3,1/6,1/6),(1/6,2/3,1/6),(1/6,1/6,2/3)])
   bary_all=(gauss@local).reshape(-1,3);area_all=np.repeat(areas/3,3);points_all=bary_all@soft
   if not np.isfinite(bary_all).all() or bary_all.min()<-1e-12 or np.max(abs(bary_all.sum(1)-1))>1e-12:raise ValueError('Invalid positive material pressure quadrature')
   for bary,A,point in zip(bary_all,area_all,points_all):
    if A<=1e-24/3:continue
    samples.append(dict(triangle_id=int(ti),corners=ids.tolist(),barycentric=bary.tolist(),area_m2=float(A),point_m=point.tolist()))
    if len(samples)>=capacity:raise ValueError('Padded pressure sample capacity saturated')
 return dict(samples=samples,polygons_by_triangle=polygons,triangle_records=records,padding_m=padding_m,quadrature_level=level,subdivision_split_fraction=float(split_fraction),reference_area_m2=sum(r['reference_area_m2']for r in records),raw_duplicated_reference_area_m2=sum(r['raw_duplicated_reference_area_m2']for r in records),scope='Conservative expanded solid/material-domain union and fixed positive reference-area packet only; no collision, force, time-step or robot qualification.')
