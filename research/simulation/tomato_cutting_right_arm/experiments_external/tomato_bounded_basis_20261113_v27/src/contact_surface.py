"""Affine FEM boundary samples; this first contact adapter supports intact tets.

No shape reconstruction unrelated to constitutive deformation is introduced.
Arbitrary cut polyhedra are explicitly rejected pending boundary coverage tests.
"""
import itertools
import numpy as np
from scipy.sparse import coo_matrix

class Surface:
 def __init__(self,a,spacing=.0005):
  b=a.body
  if np.any(b.codes) or any(len(p)!=4 for p in b.polys):
   raise ValueError('Cut-polyhedron contact surface is not qualified by this adapter')
  faces={}
  for r,ids in enumerate(b.ids):
   for loc in itertools.combinations(range(4),3):
    key=tuple(sorted(ids[list(loc)]))
    faces.setdefault(key,[]).append((r,loc))
  rows=[];cols=[];weights=[];points=[];areas=[];owners=[];triangles=[]
  for key,links in faces.items():
   if len(links)==2:continue
   if len(links)!=1:raise ValueError('nonmanifold face')
   r,loc=links[0];ids=b.ids[r][list(loc)];v=b.grid[ids];triangles.append(v)
   n=max(1,int(np.ceil(max(np.linalg.norm(v[i]-v[j]) for i,j in [(0,1),(0,2),(1,2)])/spacing)))
   A=np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2
   for i in range(n):
    for j in range(n-i):
     bary=[np.array([i+1/3,j+1/3])/n]
     if i+j<n-1:bary.append(np.array([i+2/3,j+2/3])/n)
     for yz in bary:
      w=np.r_[1-yz.sum(),yz];k=len(points);points.append(w@v);areas.append(A/n**2);owners.append(r)
      rows.extend([k]*3);cols.extend(ids);weights.extend(w)
  self.Q0=coo_matrix((weights,(rows,cols)),shape=(len(points),len(b.u))).tocsr();self.Q=(self.Q0@a.E).tocsr()
  self.X=np.array(points);self.area=np.array(areas);self.owner=np.array(owners);self.triangles=np.array(triangles);self.a=a
  if np.max(abs(self.Q@b.grid[a.masters]-self.X))>1e-12 or np.max(abs(self.Q.sum(1).A.ravel()-1))>1e-12:raise ValueError('non-affine contact map')
 def positions(self,q):return self.X+self.Q@q
 def velocities(self,v):return self.Q@v
 def pullback(self,f):return self.Q.T@f
 def tets(self,q):
  b=self.a.body;u=self.a.E@q
  return b.grid[b.ids]+u[b.ids]
