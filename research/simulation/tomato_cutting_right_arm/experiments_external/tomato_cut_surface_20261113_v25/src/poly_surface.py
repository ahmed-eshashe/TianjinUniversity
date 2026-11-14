"""Current affine material boundary, including exposed crack faces.

Coplanar overlaps are removed only between compatible, oppositely oriented
material faces. This is geometry bookkeeping, not a fracture authorization.
Contact and volume queries map through the same reduced mechanical state.
"""
import numpy as np
from scipy.spatial import ConvexHull
from scipy.sparse import coo_matrix
from shapely import Polygon,STRtree,union_all,constrained_delaunay_triangles
from reference_v17 import compatible

class Surface:
 def __init__(self,a):
  self.a=a;b=a.body;groups={};fans=[];fan_owner=[]
  for r,poly in enumerate(b.polys):
   center=poly.mean(0);scale=np.ptp(poly,axis=0).max();hull=ConvexHull((poly-center)/scale);faces={}
   for tri,eq in zip(hull.simplices,hull.equations):
    normal=eq[:3];d=eq[3]*scale-normal@center;key=tuple(np.round(np.r_[normal,d],10));faces.setdefault(key,[]).extend(tri)
    fans.append(np.vstack([center,poly[tri]]));fan_owner.append(r)
   for oriented,vertexids in faces.items():
    pts=poly[np.unique(vertexids)];normal=np.array(oriented[:3]);normal/=np.linalg.norm(normal);normal0=normal.copy();d=-normal@pts[0];flip=1 if normal[np.argmax(abs(normal))]>0 else -1;normal*=flip;d*=flip;key=tuple(np.round(np.r_[normal,d],10));groups.setdefault(key,[]).append((r,pts,normal0))
  triangles=[];owners=[];ref_normals=[];triangle_areas=[];exposed_area=0.;surface_records=[];collapsed_area=0.;collapsed_count=0
  for key,entries in groups.items():
   canonical=np.array(key[:3]);canonical/=np.linalg.norm(canonical);origin=entries[0][1][0];axis=np.eye(3)[np.argmin(abs(canonical))];u=np.cross(canonical,axis);u/=np.linalg.norm(u);v=np.cross(canonical,u);basis=np.array([u,v]);polygons=[];orientation=[]
   for r,pts,normal in entries:
    if np.max(abs((pts-origin)@canonical))>1e-11:raise ValueError('ambiguous plane grouping; no boundary deletion')
    poly=Polygon((pts-origin)@basis.T).convex_hull
    if poly.area<=0:raise ValueError('degenerate material facet')
    polygons.append(poly);orientation.append(np.sign(normal@canonical))
   tree=STRtree(polygons)
   for i,((r,pts,normal),poly) in enumerate(zip(entries,polygons)):
    matches=[polygons[j] for j in tree.query(poly) if entries[j][0]!=r and orientation[j]*orientation[i]<0 and compatible(b.codes[r],b.codes[entries[j][0]])]
    exposed=poly.difference(union_all(matches)) if matches else poly
    if exposed.is_empty:continue
    pieces=constrained_delaunay_triangles(exposed);accepted_area=0.
    for tri in pieces.geoms:
     xy=np.asarray(tri.exterior.coords)[:3];p=origin+xy@basis
     # Use the orthonormal plane coordinates for orientation and reference
     # measure. Adding a millimetre-sized origin can round a sub-ULP sliver's
     # two vertices to the same world coordinate. Keep its positive area and
     # quadrature weight; do not erase that facet or any material volume.
     signed_area=float(np.linalg.det(np.array([xy[1]-xy[0],xy[2]-xy[0]])))/2
     if signed_area*(canonical@normal)<0:p=p[[0,2,1]]
     area=float(tri.area)
     if area<=0:raise ValueError('zero reference-plane triangle')
     if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))==0:collapsed_count+=1;collapsed_area+=area
     accepted_area+=area;triangles.append(p);triangle_areas.append(area);owners.append(r);ref_normals.append(normal)
    if abs(accepted_area-exposed.area)>max(1e-20,exposed.area*1e-8):raise ValueError(('incomplete boundary triangulation',accepted_area,exposed.area))
    exposed_area+=accepted_area;surface_records.append((r,accepted_area))
  self.triangles=np.asarray(triangles);self.tri_owner=np.asarray(owners);self.ref_normals=np.asarray(ref_normals);self.X=self.triangles.reshape(-1,3);self.owner=np.repeat(self.tri_owner,3);self.tri_area=np.asarray(triangle_areas);self.area=np.repeat(self.tri_area/3,3)
  self.Q0=self._map(self.X,self.owner);self.Q=(self.Q0@a.E).tocsr()
  self.volume_tets=np.asarray(fans);self.volume_owner=np.repeat(np.asarray(fan_owner),4);self.volume_Q=(self._map(self.volume_tets.reshape(-1,3),self.volume_owner)@a.E).tocsr()
  vol=np.abs(np.linalg.det(self.volume_tets[:,1:]-self.volume_tets[:,:1]))/6
  if abs(vol.sum()-b.V.sum())>b.V.sum()*1e-10:raise ValueError('incomplete material volume coverage')
  if np.max(abs(self.Q.sum(1).A.ravel()-1))>1e-10 or np.max(abs(self.Q@b.grid[a.masters]-self.X))>1e-10:raise ValueError('non-affine contact map')
  self.metadata={'triangles':len(triangles),'reference_area_m2':float(exposed_area),'volume_coverage_m3':float(vol.sum()),'sub_ulp_facets_retained':collapsed_count,'sub_ulp_reference_area_m2':float(collapsed_area),'boundary_mapping':'current material, compatible interior faces removed, incompatible crack faces retained','fracture_authorized':False}
 def _map(self,X,owner):
  b=self.a.body;weights=np.einsum('pi,pij->pj',np.c_[np.ones(len(X)),X],b.inv[owner]);ids=b.ids[owner];return coo_matrix((weights.ravel(),(np.repeat(np.arange(len(X)),4),ids.ravel())),shape=(len(X),len(b.u))).tocsr()
 def positions(self,q):return self.X+self.Q@q
 def velocities(self,v):return self.Q@v
 def pullback(self,f):return self.Q.T@f
 def tets(self,q):return self.volume_tets+(self.volume_Q@q).reshape(-1,4,3)
