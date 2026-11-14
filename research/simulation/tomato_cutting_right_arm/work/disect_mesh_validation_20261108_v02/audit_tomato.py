from pathlib import Path
import numpy as np,json
from scipy.spatial import ConvexHull,cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
w=Path(__file__).resolve().parent;z=np.load(w/'source_tomato.npz');x=z['x'];t=z['tets'];mass=z['mass'];surface=z['surface']
# Only merge exact coordinate coincidences in an offline audit. Never mutate source.
ux,inv=np.unique(x,axis=0,return_inverse=True);wt=inv[t]
f=np.sort(np.concatenate([wt[:,[0,1,2]],wt[:,[0,1,3]],wt[:,[0,2,3]],wt[:,[1,2,3]]]),axis=1);uf,n=np.unique(f,axis=0,return_counts=True);boundary=uf[n==1];bf=ux[boundary];area=np.linalg.norm(np.cross(bf[:,1]-bf[:,0],bf[:,2]-bf[:,0]),axis=1)/2
hull=ConvexHull(ux);vol=np.linalg.det(x[t[:,1:]]-x[t[:,0]][:,None,:])/6
# All vertices on one hull supporting plane => exterior face. Distances chunked.
on_hull=np.zeros(len(boundary),bool)
for start in range(0,len(hull.equations),128):
 eq=hull.equations[start:start+128];dist=bf@eq[:,:3].T+eq[:,3];on_hull|=np.any(np.max(abs(dist),axis=1)<1e-10,axis=1)
internal=~on_hull;edges=np.sort(np.concatenate([boundary[:,[0,1]],boundary[:,[1,2]],boundary[:,[2,0]]]),axis=1);ee,en=np.unique(edges,axis=0,return_counts=True)
e=np.concatenate([wt[:,[0,i]] for i in [1,2,3]]);nc,l=connected_components(coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(ux),len(ux))),directed=False)
# Boundary matches authored surface geometrically? Triangulations can differ;
# hull supporting-plane check detects exposed interior faces independently.
q=x[t];lengths=np.linalg.norm(q[:,:,None]-q[:,None,:],axis=-1);quality=6*abs(vol)/np.maximum(lengths.max(axis=(1,2))**3,1e-300)
out={'source_nodes':len(x),'exact_unique_nodes':len(ux),'tetrahedra':len(t),'positive_volumes':bool((vol>0).all()),'minimum_volume_m3':float(vol.min()),'sum_volume_m3':float(vol.sum()),'convex_hull_volume_m3':float(hull.volume),'volume_relative_error':float(vol.sum()/hull.volume-1),'tet_graph_components_after_exact_weld':int(nc),'face_incidence_histogram':{str(k):int((n==k).sum()) for k in np.unique(n)},'boundary_triangles':len(boundary),'boundary_faces_on_exterior_hull':int(on_hull.sum()),'unpaired_interior_faces':int(internal.sum()),'unpaired_interior_face_area_m2':float(area[internal].sum()),'boundary_edge_incidence_histogram':{str(k):int((en==k).sum()) for k in np.unique(en)},'minimum_6V_over_maxedge_cubed':float(quality.min()),'total_mass_kg':float(mass.sum()),'direct_FEM_input_qualified':bool((vol>0).all() and not internal.any() and np.all(n<=2) and np.all(en==2) and nc==1),'interpretation':'Interior unpaired faces are not permissible in a conforming intact tetrahedral FEM mesh. Exact weld is audit-only; original same-position interface nodes remain unchanged.'}
np.savez(w/'tomato_internal_face_diagnostic.npz',points=ux,internal_faces=boundary[internal],tet_indices=wt)
(w/'tomato_fem_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
