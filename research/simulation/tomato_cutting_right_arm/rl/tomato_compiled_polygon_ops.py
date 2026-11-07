"""Compiled float64 polygon arithmetic; same clipping signs and area thresholds.
No fast-math or geometric tolerance changes. Reference Python implementation
remains in tomato_vectorized_material_coverage / tomato_exact_blade_coverage.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def signed_area(p):
 if len(p)<3:return 0.
 q=p[:,1:]
 return .5*np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))

@njit(cache=True)
def uv_clip(p,normal,anchor,inside):
 if len(p)<3:return np.empty((0,3),np.float64)
 result=np.empty((2*len(p)+2,3),np.float64);count=0;previous=p[-1];dp=normal@(previous[1:]-anchor)
 for current in p:
  dc=normal@(current[1:]-anchor);ip=dp<=0 if inside else dp>=0;ic=dc<=0 if inside else dc>=0
  if ip!=ic:result[count]=previous+(dp/(dp-dc))*(current-previous);count+=1
  if ic:result[count]=current;count+=1
  previous=current;dp=dc
 return result[:count].copy()

@njit(cache=True)
def subtract(p,q):
 pieces=[]
 if len(p)<3:return pieces
 if len(q)<3 or abs(signed_area(q))<1e-24:
  pieces.append(p);return pieces
 if signed_area(q)<0:q=q[::-1].copy()
 remaining=p
 for index in range(len(q)):
  first=q[index];last=q[(index+1)%len(q)];edge=last[1:]-first[1:]
  if np.linalg.norm(edge)<1e-15:continue
  normal=np.array([edge[1],-edge[0]]);outside=uv_clip(remaining,normal,first[1:],False)
  if len(outside)>=3 and abs(signed_area(outside))>1e-24:pieces.append(outside)
  remaining=uv_clip(remaining,normal,first[1:],True)
  if len(remaining)<3 or abs(signed_area(remaining))<1e-24:break
 return pieces

@njit(cache=True)
def spatial_clip(p,soft,normal,anchor):
 if len(p)==0:return np.empty((0,3),np.float64)
 result=np.empty((2*len(p)+2,3),np.float64);count=0;previous=p[-1];dp=normal@(previous@soft-anchor)
 for current in p:
  dc=normal@(current@soft-anchor);ip=dp<=0.;ic=dc<=0.
  if ip!=ic:result[count]=previous+(dp/(dp-dc))*(current-previous);count+=1
  if ic:result[count]=current;count+=1
  previous=current;dp=dc
 return result[:count].copy()

def signed_uv_area(polygon):return float(signed_area(np.asarray(polygon,dtype=np.float64).reshape(-1,3)))
def subtract_convex(polygon,covered):return subtract(np.asarray(polygon,dtype=np.float64).reshape(-1,3),np.asarray(covered,dtype=np.float64).reshape(-1,3))
def clip_polygon(polygon,soft,normal,anchor):return spatial_clip(np.asarray(polygon,dtype=np.float64).reshape(-1,3),soft,normal,anchor)
