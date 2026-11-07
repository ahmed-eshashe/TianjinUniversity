"""Conservative per-material-triangle quadrature feature selection.

For a triangle enclosed by radius r about center c, every point p satisfies
|p-c|<=r. Distance to any closed face is 1-Lipschitz. A face with
 d(c,face) > min_face d(c,face) + 2*r
cannot be closest anywhere on that triangle. Only its QUADRATURE partition
planes are omitted. Actual CAD queries always retain all authored faces.
The parent/children accuracy and old/new remap checks remain unchanged.
"""
import numpy as np
import warp as wp
from tomato_exact_blade_queries import closest
from tomato_compiled_plane_partition import partition as reference_partition

@wp.kernel(enable_backward=False)
def center_distances(v:wp.array[wp.vec3d],faces:wp.array[wp.vec3i],centers:wp.array[wp.vec3d],distance:wp.array2d[wp.float64]):
 i,j=wp.tid();f=faces[j];q=closest(v[f[0]],v[f[1]],v[f[2]],centers[i]);distance[i,j]=wp.length(centers[i]-q)

def candidate_faces(blade,positions):
 positions=np.asarray(positions,float);centers=positions.mean(1);radius=np.linalg.norm(positions-centers[:,None,:],axis=2).max(1)
 vertices=wp.array(np.asarray(blade['vertices']),dtype=wp.vec3d);faces=wp.array(np.asarray(blade['triangles'],np.int32),dtype=wp.vec3i);c=wp.array(centers,dtype=wp.vec3d);d=wp.empty((len(centers),len(blade['triangles'])),dtype=wp.float64)
 wp.launch(center_distances,dim=d.shape,inputs=[vertices,faces,c],outputs=[d],block_dim=64);distance=d.numpy()
 if not np.isfinite(distance).all():raise ValueError('Nonfinite local face bound')
 # Absolute 0.1 nm expansion protects roundoff in meter-scale coordinates.
 mask=distance<=distance.min(1)[:,None]+2*radius[:,None]+1e-10
 if not mask.any(1).all():raise ValueError('Empty conservative face candidate set')
 return mask,dict(center_distance=distance,radius=radius)

def partition(blade,ids,leaves,areas,x,rotation,translation,face_ids):
 ids=np.asarray(ids);leaves=np.asarray(leaves);areas=np.asarray(areas);unique,inverse=np.unique(ids,axis=0,return_inverse=True);local=(np.asarray(x)[unique]-translation)@rotation;mask,_=candidate_faces(blade,local)
 new_ids=[];new_cells=[];new_areas=[];reports=[]
 for k,index in enumerate(unique):
  group=np.flatnonzero(inverse==k);selected=np.flatnonzero(mask[k]);ni,nc,na,report=reference_partition(blade,ids[group],leaves[group],areas[group],x,rotation,translation,selected)
  new_ids.append(ni);new_cells.append(nc);new_areas.append(na);reports.append(dict(triangle=index.tolist(),candidate_faces=len(selected),**report))
 ni=np.concatenate(new_ids);nc=np.concatenate(new_cells);na=np.concatenate(new_areas)
 if abs(na.sum()-areas.sum())>1e-12*max(areas.sum(),1e-12):raise ValueError('Local partition lost reference area')
 return ni,nc,na,dict(selection='conservative_distance_lipschitz_bound',original_cells=len(leaves),partitioned_cells=len(nc),material_triangles=len(unique),maximum_local_face_planes=max(q['face_planes']for q in reports),maximum_local_partition_planes=max(q['partition_planes']for q in reports),unpartitioned_roundoff_fallbacks=sum(q['unpartitioned_roundoff_fallbacks']for q in reports),groups=reports)
