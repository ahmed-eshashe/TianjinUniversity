"""Conservative original-CAD solid-cell penetration proof.

The distance to a fixed triangle is convex. Its maximum over a convex material /
CAD-cell intersection is bounded by its values at the intersection vertices.
Any original boundary triangle supplies an upper bound on interior depth.
Ill-conditioned or unresolved cases fall back to the existing volume proof.
No material, CAD face, force, timestep or penetration limit is changed.
"""
from pathlib import Path
import numpy as np,time
from numba import njit

@njit(cache=True)
def planes_of(t):
 p=np.empty((4,4));h=0.
 for i in range(4):
  for j in range(i):h=max(h,np.linalg.norm(t[i]-t[j]))
 for i in range(4):
  face=np.empty((3,3));k=0
  for j in range(4):
   if j!=i:face[k]=t[j];k+=1
  n=np.cross(face[1]-face[0],face[2]-face[0]);size=np.linalg.norm(n)
  if size==0:return p,False
  n/=size
  if np.dot(n,t[i]-face[0])>0:n=-n
  p[i,:3]=n;p[i,3]=-np.dot(n,face[0])
  if abs(np.dot(n,t[i])+p[i,3])<1e-8*h:return p,False
 return p,True

@njit(cache=True)
def inside(p,planes):
 for j in range(4):
  if np.dot(planes[j,:3],p)+planes[j,3]>1e-12:return False
 return True

@njit(cache=True)
def intersection(a,b,pa,pb):
 pts=np.empty((56,3));n=0
 for i in range(4):
  if inside(a[i],pb):pts[n]=a[i];n+=1
  if inside(b[i],pa):pts[n]=b[i];n+=1
 for side in range(2):
  vertices=a if side==0 else b;other=pb if side==0 else pa;own=pa if side==0 else pb
  for i in range(4):
   for j in range(i):
    for k in range(4):
     d0=np.dot(other[k,:3],vertices[i])+other[k,3];d1=np.dot(other[k,:3],vertices[j])+other[k,3]
     if (d0<0<d1) or (d1<0<d0):
      point=vertices[i]+d0/(d0-d1)*(vertices[j]-vertices[i])
      if inside(point,other) and inside(point,own):pts[n]=point;n+=1
 return pts[:n]

@njit(cache=True)
def distance(p,a,b,c):
 ab=b-a;ac=c-a;ap=p-a;d1=np.dot(ab,ap);d2=np.dot(ac,ap)
 if d1<=0 and d2<=0:return np.linalg.norm(ap)
 bp=p-b;d3=np.dot(ab,bp);d4=np.dot(ac,bp)
 if d3>=0 and d4<=d3:return np.linalg.norm(bp)
 vc=d1*d4-d3*d2
 if vc<=0 and d1>=0 and d3<=0:return np.linalg.norm(p-(a+d1/(d1-d3)*ab))
 cp=p-c;d5=np.dot(ab,cp);d6=np.dot(ac,cp)
 if d6>=0 and d5<=d6:return np.linalg.norm(cp)
 vb=d5*d2-d1*d6
 if vb<=0 and d2>=0 and d6<=0:return np.linalg.norm(p-(a+d2/(d2-d6)*ac))
 va=d3*d6-d5*d4
 if va<=0 and d4-d3>=0 and d5-d6>=0:return np.linalg.norm(p-(b+(d4-d3)/((d4-d3)+(d5-d6))*(c-b)))
 den=va+vb+vc
 if den==0:return min(np.linalg.norm(ap),np.linalg.norm(bp),np.linalg.norm(cp))
 return np.linalg.norm(p-(a+vb/den*ab+vc/den*ac))

@njit(cache=True)
def bounds(local,cells,cplanes,cvalid,lo,hi,triangles,ptr,ids,target):
 unresolved=np.zeros(len(local),np.bool_);maximum=0.;pairs=0;queries=0;fallback_condition=0
 for i in range(len(local)):
  a=local[i];amin=np.empty(3);amax=np.empty(3)
  for k in range(3):amin[k]=a[:,k].min();amax[k]=a[:,k].max()
  pa,valid=planes_of(a)
  for ci in range(len(cells)):
   if np.any(amax+1e-12<lo[ci]) or np.any(hi[ci]+1e-12<amin):continue
   if not valid or not cvalid[ci]:unresolved[i]=True;fallback_condition+=1;continue
   points=intersection(a,cells[ci],pa,cplanes[ci]);pairs+=1
   if len(points)==0:continue
   center=points.sum(0)/len(points);bestface=-1;best=1e10
   for f in range(ptr[ci],ptr[ci+1]):
    j=ids[f];d=distance(center,triangles[j,0],triangles[j,1],triangles[j,2]);queries+=1
    if d<best:best=d;bestface=j
   bound=0.
   for p in points:bound=max(bound,distance(p,triangles[bestface,0],triangles[bestface,1],triangles[bestface,2]));queries+=1
   # A different single boundary face may prove a tighter bound. No closest-
   # face assumption is needed for correctness; each tested face is an upper.
   if bound>target:
    for f in range(ptr[ci],ptr[ci+1]):
     j=ids[f];candidate=0.
     for p in points:candidate=max(candidate,distance(p,triangles[j,0],triangles[j,1],triangles[j,2]));queries+=1
     bound=min(bound,candidate)
     if bound<=target:break
   maximum=max(maximum,bound)
   if bound>target:unresolved[i]=True
 return unresolved,maximum,pairs,queries,fallback_condition

class ConvexGuard:
 def __init__(self,cad):
  self.cad=cad;z=np.load(Path(__file__).resolve().parents[1]/'assets/blade_partition.npz');self.cells=z['x'][z['tets']];p=[planes_of(t) for t in self.cells];self.planes=np.array([v[0] for v in p]);self.valid=np.array([v[1] for v in p]);self.lo=self.cells.min(1);self.hi=self.cells.max(1);self.tri=cad.vertices[cad.faces];z=np.load(Path(__file__).resolve().parents[1]/'assets/inside_candidates.npz');self.ptr=z['ptr'];self.ids=z['ids']
 def certify(self,tets,T,R=None,limit=.0001,motion=0.,maxdepth=24,allowance=2e-6):
  from blade_geometry import certify
  start=time.perf_counter();R=self.cad.R if R is None else R;local=(np.asarray(tets)-T)@R;threshold=limit-motion-allowance
  if threshold<=0:return dict(passed=False,reason='motion_exceeds_certificate_budget',motion_bound_m=motion)
  unresolved,upper,pairs,queries,condition=bounds(local,self.cells,self.planes,self.valid,self.lo,self.hi,self.tri,self.ptr,self.ids,threshold)
  fallback=None
  if unresolved.any():fallback=certify(np.asarray(tets)[unresolved],self.cad,T,R,limit=limit,motion=motion,maxdepth=maxdepth,allowance=allowance)
  passed=fallback is None or fallback['passed'];return dict(passed=bool(passed),reason='original_CAD_convex_distance_bound' if passed else fallback['reason'],bound_m=float(max(upper+motion+allowance,0)) if fallback is None else None,intersection_pairs=int(pairs),triangle_queries=int(queries),fallback_tets=int(unresolved.sum()),ill_conditioned_pairs=int(condition),fallback=fallback,wall_s=time.perf_counter()-start,motion_bound_m=motion)
