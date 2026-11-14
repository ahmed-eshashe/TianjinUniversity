"""Independent stationary-target, fixed-orientation edge-sweep volume reference.

A translated finite CAD facet sweeps its convex triangular prism. Positive-area
intersection with a material footprint is stronger than a proximity threshold.
This restricted reference is not a general moving/deforming-target detector.
"""
import numpy as np
from scipy.spatial import ConvexHull

def clipped_area(triangle,planes):
 polygon=np.asarray(triangle,dtype=float)
 for equation in planes:
  if len(polygon)<3:return 0.
  values=polygon@equation[:3]+equation[3];result=[]
  for i,p in enumerate(polygon):
   previous=polygon[i-1];a=values[i-1];b=values[i]
   if (a<=0)!=(b<=0):result.append(previous+(a/(a-b))*(p-previous))
   if b<=0:result.append(p)
  polygon=np.array(result).reshape(-1,3)
 if len(polygon)<3:return 0.
 return float(sum(np.linalg.norm(np.cross(polygon[i]-polygon[0],polygon[i+1]-polygon[0]))/2 for i in range(1,len(polygon)-1)))

def translated_front_events(front0,front1,material,patches,*,minimum_area_m2=1e-16):
 front0=np.asarray(front0);front1=np.asarray(front1);delta=front1-front0
 if np.max(abs(delta-delta[0,0]))>1e-12:raise ValueError('Reference only supports common translation, no rotating/deforming front')
 material=np.asarray(material);lo=material.min(1);hi=material.max(1);patches=np.asarray(patches);found={};candidates=0
 for i,(a,b) in enumerate(zip(front0,front1)):
  vertices=np.concatenate([a,b]);prism=ConvexHull(vertices)
  if prism.volume<=1e-24:raise ValueError('Degenerate swept prism')
  lower=vertices.min(0);upper=vertices.max(0);ids=np.flatnonzero(np.all(hi>=lower,1)&np.all(lo<=upper,1))
  for j in ids:
   patch=int(patches[j])
   if patch in found:continue
   candidates+=1;area=clipped_area(material[j],prism.equations)
   if area>minimum_area_m2:found[patch]=dict(patch=patch,front_face_index=i,material_subtriangle_index=int(j),positive_intersection_area_m2=area)
 return dict(events=list(found.values()),candidate_triangle_pairs=candidates,scope='Positive-area swept triangular-prism intersections, stationary target and translating CAD only; no actual mechanical cut or irreversible history commit.')
