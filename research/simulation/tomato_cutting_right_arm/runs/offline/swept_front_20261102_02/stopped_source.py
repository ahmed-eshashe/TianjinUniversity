"""Geometry component: swept finite CAD front against deforming material footprints.

This only reports candidate edge events. It never changes history or enables
fracture. Inputs are accepted endpoint geometries, interpolated linearly per
vertex; a curved rigid trajectory requires independently controlled subdivision.
"""
import numpy as np
EDGES=((0,1),(1,2),(2,0))

class SweptFrontDetector:
 def __init__(self,ipctk,*,tolerance=1e-9):
  self.ipc=ipctk;self.ccd=ipctk.TightInclusionCCD(tolerance=tolerance,max_iterations=10000000,conservative_rescaling=.8);self.tolerance=tolerance
 def _intersects(self,a,b):
  return any(self.ipc.is_edge_intersecting_triangle(a[i],a[j],*b) or self.ipc.is_edge_intersecting_triangle(b[i],b[j],*a) for i,j in EDGES)
 def triangle_event(self,a0,a1,b0,b1):
  # Exact static predicates, then continuous vertex/face and edge/edge queries.
  if self._intersects(a0,b0):return True,0.,'initial_intersection'
  earliest=1.;hit=False
  for i in range(3):
   for p0,p1,t0,t1 in [(a0[i],a1[i],b0,b1),(b0[i],b1[i],a0,a1)]:
    found,toi=self.ccd.point_triangle_ccd(p0,*t0,p1,*t1)
    if found:hit=True;earliest=min(earliest,float(toi))
  for i,j in EDGES:
   for k,l in EDGES:
    found,toi=self.ccd.edge_edge_ccd(a0[i],a0[j],b0[k],b0[l],a1[i],a1[j],b1[k],b1[l])
    if found:hit=True;earliest=min(earliest,float(toi))
  if self._intersects(a1,b1):hit=True;earliest=min(earliest,1.)
  return hit,earliest,'continuous_feature_query'
 def detect(self,front0,front1,material0,material1,patches):
  arrays=[np.asarray(v,dtype=float)for v in [front0,front1,material0,material1]];a0,a1,b0,b1=arrays;patches=np.asarray(patches,dtype=int)
  if a0.shape!=a1.shape or b0.shape!=b1.shape or a0.shape[1:]!=(3,3) or b0.shape[1:]!=(3,3) or len(patches)!=len(b0) or not all(np.isfinite(v).all()for v in arrays):raise ValueError('Invalid accepted swept geometry')
  for v in arrays:
   if np.any(np.linalg.norm(np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]),axis=1)<1e-16):raise ValueError('Degenerate endpoint facet')
  alo=np.minimum(a0.min(1),a1.min(1));ahi=np.maximum(a0.max(1),a1.max(1));blo=np.minimum(b0.min(1),b1.min(1));bhi=np.maximum(b0.max(1),b1.max(1));events={};candidates=0
  for i in range(len(a0)):
   ids=np.flatnonzero(np.all(bhi>=alo[i],axis=1)&np.all(blo<=ahi[i],axis=1))
   for j in ids:
    candidates+=1;hit,toi,kind=self.triangle_event(a0[i],a1[i],b0[j],b1[j])
    if hit:
     patch=int(patches[j]);row=dict(patch=patch,front_face_index=i,material_subtriangle_index=int(j),conservative_time_fraction=toi,kind=kind)
     if patch not in events or toi<events[patch]['conservative_time_fraction']:events[patch]=row
  return dict(events=list(events.values()),candidate_triangle_pairs=candidates,scope='Conservative continuous edge-event candidates for linear vertex trajectories only; no committed eligibility, overlap state, damage, robot route or performed cut.')
