"""Render-only clipped Voronoi skin; all cracks are keyed to existing bonds."""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np
from scipy.spatial import ConvexHull,HalfspaceIntersection,Voronoi,cKDTree
W=Path(__file__).parent;REFERENCE=Path('/home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28');sys.path.insert(0,str(REFERENCE/'src'))
from model import lattice
m=lattice('tomato');x=m['x'].astype(float);n=len(x);start=time.perf_counter()
p=np.load('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz')['poly_vertices'];p-=.5*(p.min(0)+p.max(0));p[:,1]+=x[:,1].mean();hull=ConvexHull(p);outer=np.r_[hull.equations,[[0.,-1.,0.,0.]]];vor=Voronoi(x);neighbors=[[] for _ in x]
for i,j in vor.ridge_points:neighbors[i].append(j);neighbors[j].append(i)
edge_map={tuple(sorted(e)):i for i,e in enumerate(m['edges'])}
vertices=[];owners=[];triangles=[];tri_owner=[];tri_other=[];tri_bond=[];skin=[];unknown=[]
for i,point in enumerate(x):
 nbr=np.asarray(neighbors[i]);d=x[nbr]-point;norm=np.linalg.norm(d,axis=1);N=d/norm[:,None];b=-np.einsum('ij,ij->i',N,.5*(x[nbr]+point));internal=np.c_[N,b];region=vor.regions[vor.point_region[i]]
 if -1 not in region and len(region)>0:
  vv=vor.vertices[region]
  # Finite interior cells can be used directly if they lie within every exterior plane.
  interior=np.max(vv@outer[:,:3].T+outer[:,3])<1e-9
 else:interior=False
 if not interior:
  hs=np.r_[internal,outer]
  vv=HalfspaceIntersection(hs,point).intersections
 ch=ConvexHull(vv);base=len(vertices);vertices.extend(vv);owners.extend([i]*len(vv))
 for face in ch.simplices:
  a,c,e=vv[face];normal=np.cross(c-a,e-a);area=np.linalg.norm(normal)*.5
  if area<1e-15:continue
  if np.dot(normal,(a+c+e)/3-point)<0:face=face[[0,2,1]]
  distances=np.abs(vv[face]@internal[:,:3].T+internal[:,3]);plane_error=distances.max(0);j=int(np.argmin(plane_error));is_skin=plane_error[j]>2e-8
  other=-1 if is_skin else int(nbr[j]);bond=-1 if is_skin else edge_map.get(tuple(sorted((i,other))),-1)
  if other>=0 and bond<0:unknown.append((i,other,area))
  triangles.append(face+base);tri_owner.append(i);tri_other.append(other);tri_bond.append(bond);skin.append(is_skin)
 if i%400==0:print(i,n,'vertices',len(vertices),'seconds',time.perf_counter()-start,flush=True)
v=np.asarray(vertices);owner=np.asarray(owners,np.int32);f=np.asarray(triangles,np.int32);skin=np.array(skin,bool);bond=np.array(tri_bond,np.int32);other=np.array(tri_other,np.int32)
# Coincident vertices share a support set. Broken local connections split that set;
# the rendered motion is interpolated from each side, with no opening animation.
_,unique_index,group=np.unique(np.round(v,8),axis=0,return_index=True,return_inverse=True);unique=v[unique_index];distance,support=cKDTree(x).query(unique,k=8);weights=1/np.maximum(distance,.00015)**2;weights/=weights.sum(1,keepdims=True);owner_slot=np.argmax(support[group]==owner[:,None],axis=1)
assert np.all(np.any(support[group]==owner[:,None],axis=1)),'Cell owner missing from local support'
pairs=np.array([(a,b) for a in range(8) for b in range(a+1,8)],np.int32);local_bonds=np.full((len(unique),len(pairs)),-1,np.int32)
for k,(a,b) in enumerate(pairs):local_bonds[:,k]=[edge_map.get(tuple(sorted((i,j))),-1) for i,j in zip(support[:,a],support[:,b])]
np.savez_compressed(W/'assets/surface.npz',vertices=v.astype(np.float32),owner=owner,faces=f,skin=skin,face_bond=bond,face_other=other,face_owner=np.array(tri_owner,np.int32),unique=unique.astype(np.float32),group=group.astype(np.int32),support=support.astype(np.int32),weights=weights.astype(np.float32),owner_slot=owner_slot.astype(np.int32),pairs=pairs,local_bonds=local_bonds,particle_rest=x.astype(np.float32))
report={'vertices':len(v),'unique_vertices':len(unique),'triangles':len(f),'skin_triangles':int(skin.sum()),'potential_cut_triangles':int((~skin).sum()),'internal_faces_without_physical_bond':len(unknown),'unknown_area_m2':float(sum(a for i,j,a in unknown)),'build_wall_s':time.perf_counter()-start,'physics_changed':False,'display_only':True,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (REFERENCE/'src').glob('*.py')}};(W/'reports/build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
