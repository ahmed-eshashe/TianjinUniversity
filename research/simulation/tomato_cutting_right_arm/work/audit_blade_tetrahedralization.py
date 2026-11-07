from pathlib import Path
import json,numpy as np
from scipy.spatial import Delaunay
from collections import Counter
from tomato_native_worker import validate_inputs
from tomato_sdf_native_probe import signed_reference
from tomato_triangle_distance import point_mesh
R=Path.cwd();blade=validate_inputs(R,json.load(open(R/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json')))['blade'];x=np.array(blade['vertices']);t=Delaunay(x).simplices;p=x[t];vol=np.linalg.det(p[:,1:]-p[:,:1])/6;t=t[abs(vol)>1e-20];p=x[t];centres=p.mean(axis=1);keep=[]
for tet,c in zip(t,centres):
 if signed_reference(c.tolist(),blade['vertices'],blade['triangles'])['reference_signed_distance_m']<0:keep.append(tet.tolist())
faces=Counter(tuple(sorted([tet[j] for j in face])) for tet in keep for face in ((0,1,2),(0,1,3),(0,2,3),(1,2,3)));boundary=[f for f,c in faces.items() if c==1];distances=[point_mesh(x[list(f)].mean(axis=0).tolist(),blade['vertices'],blade['triangles'])['distance_m'] for f in boundary]
result=dict(tets=len(keep),boundary_faces=len(boundary),max_boundary_centroid_distance_m=max(distances),off_surface=sum(d>1e-10 for d in distances),tet_indices=keep)
Path('work/blade_tetrahedralization_audit.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k!='tet_indices'})
