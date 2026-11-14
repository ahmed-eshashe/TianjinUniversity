from pathlib import Path
import sys,json,time
import numpy as np
from scipy.spatial import Delaunay,cKDTree
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_mesh_validation_20261108_v02/mesh_deps'))
import tetgen
z=np.load(W.parent/'disect_precontact_20261108_v06/conforming_split.npz')
x=z['x']; plane=-.0225
# Preserve every clipped exterior triangle, but discard the old internal cut triangulation.
outer=z['outer']; coords=x[outer]; points,inv=np.unique(coords.reshape(-1,3),axis=0,return_inverse=True); faces=inv.reshape(-1,3)
seam=np.flatnonzero(abs(points[:,0]-plane)<1e-12)
sys.path.insert(0,str(W.parent/'disect_mesh_validation_20261108_v02/audit_deps'))
from shapely import LineString,union_all,constrained_delaunay_triangles
from shapely.ops import polygonize
oldcap=z['cut_minus']; edges=np.sort(np.vstack([oldcap[:,[0,1]],oldcap[:,[1,2]],oldcap[:,[2,0]]]),axis=1)
edge,count=np.unique(edges,axis=0,return_counts=True)
polygon=union_all(list(polygonize([LineString(x[e,1:]) for e in edge[count==1]])))
tris=constrained_delaunay_triangles(polygon)
cap=np.array([cKDTree(points).query(np.column_stack([np.full(3,plane),np.array(g.exterior.coords)[:3]]))[1] for g in tris.geoms])
for p in x[z['fixed']]:
 if np.linalg.norm(points-p,axis=1).min()>1e-12:points=np.vstack([points,p])
start=time.perf_counter()
allfaces=np.vstack([faces,cap]).astype(np.int32)
tri=points[allfaces];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None]
sgn=np.where(norm[np.arange(len(norm)),np.argmax(abs(norm),axis=1)]<0,-1,1);norm*=sgn[:,None]
planes=np.column_stack([norm,-np.einsum('ij,ij->i',norm,tri[:,0])])
_,markers=np.unique(np.round(planes,10),axis=0,return_inverse=True)
m=tetgen.TetGen(points,allfaces,(markers+1).astype(np.int32))
r=m.tetrahedralize(order=1,epsilon=1e-12,nomergefacet=False,nomergevertex=True,facet_separate_ang_tol=179.99999999,collinear_ang_tol=179.99999999,minratio=1.6,mindihedral=5,nobisect=False,maxvolume=1e-8,fixedvolume=True,steinerleft=30000,quiet=True)
X=np.asarray(r[0]);t=np.asarray(r[1]);vol=np.linalg.det(X[t[:,1:]]-X[t[:,0]][:,None])/6
neg=vol<0;t[neg,0],t[neg,1]=t[neg,1].copy(),t[neg,0].copy();vol=abs(vol)
side=np.where(X[t,0].mean(1)<plane,-1,1)
cross=((X[t,0].min(1)<plane-1e-12)&(X[t,0].max(1)>plane+1e-12)).sum()
assert cross==0,'Tetrahedra cross interface'
paired=np.intersect1d(np.unique(t[side<0]),np.unique(t[side>0]));assert np.max(abs(X[paired,0]-plane))<1e-12
copies={int(k):len(X)+i for i,k in enumerate(paired)};X=np.vstack([X,X[paired]])
for row in t[side>0]:pass
for i in np.flatnonzero(side>0):t[i]=[copies.get(int(k),int(k)) for k in t[i]]
ties=np.array([[k,copies[int(k)]] for k in paired]);rho=z['mass'].sum()/vol.sum();mass=np.zeros(len(X));np.add.at(mass,t.ravel(),np.repeat(rho*vol/4,4))
support_dist,fixed=cKDTree(X).query(x[z['fixed']])
ori=t[:,[[0,2,1],[0,1,3],[0,3,2],[1,2,3]]].reshape(-1,3);_,idx,count=np.unique(np.sort(ori,axis=1),axis=0,return_index=True,return_counts=True);boundary=ori[idx[count==1]];iscut=np.max(abs(X[boundary,0]-plane),axis=1)<1e-12
cut=boundary[iscut];minus=set(t[side<0].ravel());cutminus=np.array([f for f in cut if f[0] in minus]);cutplus=np.array([f for f in cut if f[0] not in minus]);sv=np.linalg.svd(X[t[:,1:]]-X[t[:,0]][:,None],compute_uv=False)
np.savez_compressed(W/'conforming_split.npz',x=X,tets=t,mass=mass,fixed=fixed,ties=ties,tet_side=side,volume=vol,cut_minus=cutminus,cut_plus=cutplus,outer=boundary[~iscut],boundary=boundary,source_x=z['source_x'],source_tets=z['source_tets'],source_outer=z['source_outer'])
out=dict(scope='Mesh construction only; mechanics unvalidated',nodes=len(X),tetrahedra=len(t),interface_pairs=len(ties),min_volume_m3=float(vol.min()),min_mass_kg=float(mass.min()),min_singular_m=float(sv[:,-1].min()),max_condition=float((sv[:,0]/sv[:,-1]).max()),mass_kg=float(mass.sum()),volume_relative_error=float(vol.sum()/z['volume'].sum()-1),support_error_m=float(support_dist.max()),nonmanifold_faces=int((count>2).sum()),wall_s=time.perf_counter()-start)
(W/'mesh_build.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
