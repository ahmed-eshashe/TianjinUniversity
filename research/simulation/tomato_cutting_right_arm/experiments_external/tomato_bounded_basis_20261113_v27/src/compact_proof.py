"""Conservative clearance envelope; NEVER used for material or contact forces.

The union of regions with identical affine maps is contained in the convex
hull of its vertices. Prove that hull, or fall back to all original material
volume. Only exactly identical parent and sparse-map rows are grouped.
"""
import numpy as np
from scipy.spatial import ConvexHull
from scipy.sparse import coo_matrix
class CompactProof:
 def __init__(self,a,surface,guard):
  self.surface=surface;self.guard=guard;b=a.body;groups={}
  for r in range(len(b.polys)):
   m=a.E[b.ids[r]].tocsr();m.sort_indices();key=(b.inv[r].tobytes(),m.indptr.tobytes(),m.indices.tobytes(),m.data.tobytes());groups.setdefault(key,[]).append(r)
  tets=[];owner=[]
  for members in groups.values():
   points=np.unique(np.concatenate([b.polys[r] for r in members]),axis=0);center=points.mean(0);scale=np.ptp(points,axis=0).max();h=ConvexHull((points-center)/scale)
   if len(h.vertices)==4:
    tets.append(points[h.vertices]);owner.extend([members[0]]*4)
   else:
    for tri in h.simplices:tets.append(np.vstack([center,points[tri]]));owner.extend([members[0]]*4)
  self.tets0=np.asarray(tets);self.owners=np.asarray(owner)[::4];X=self.tets0.reshape(-1,3);r=np.asarray(owner);N=np.einsum('pi,pij->pj',np.c_[np.ones(len(X)),X],b.inv[r]);Q0=coo_matrix((N.ravel(),(np.repeat(np.arange(len(X)),4),b.ids[r].ravel())),shape=(len(X),len(b.u)));self.Q=(Q0@a.E).tocsr();self.report=dict(groups=len(groups),original_regions=len(b.polys),proof_tets=len(tets),original_tets=len(surface.volume_tets))
 def __call__(self,q,T,R,motion=0.,maxdepth=24):
  result=self.guard.certify(self.tets0+(self.Q@q).reshape(-1,4,3),T,R,motion=motion,maxdepth=maxdepth)
  if result['passed']:result['conservative_grouping']=self.report;return result
  # An envelope failure is never evidence of a true physical violation.
  exact=self.guard.certify(self.surface.tets(q),T,R,motion=motion,maxdepth=maxdepth);exact['envelope_fallback']=result;return exact
