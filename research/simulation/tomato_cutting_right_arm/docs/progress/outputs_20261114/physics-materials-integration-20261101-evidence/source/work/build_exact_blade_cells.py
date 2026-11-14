import resource,signal
resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));signal.alarm(45)
from pathlib import Path
import json,hashlib
from collections import Counter
import numpy as np
import meshpy.tet as tet
from tomato_native_worker import validate_inputs
R=Path.cwd();config=json.load(open('runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json'));blade=validate_inputs(R,config)['blade'];info=tet.MeshInfo();info.set_points(blade['vertices']);info.set_facets(blade['triangles']);mesh=tet.tetrahedralize(info,tet.Options('pYQCM'));points=np.array(mesh.points);cells=np.array(mesh.elements);v=np.linalg.det(points[cells[:,1:]]-points[cells[:,:1]])/6
bad=v<0;cells[bad,0],cells[bad,1]=cells[bad,1].copy(),cells[bad,0].copy();v=abs(v)
faces=Counter(tuple(sorted(t[j] for j in face)) for t in cells for face in ((0,1,2),(0,1,3),(0,2,3),(1,2,3)));boundary=set(f for f,c in faces.items() if c==1)
original=set(tuple(sorted(f)) for f in blade['triangles']);same_original_vertices=np.array_equal(points[:len(blade['vertices'])],blade['vertices']);assert same_original_vertices and boundary==original and min(v)>0
surface_volume=sum(np.dot(np.array(blade['vertices'])[f[0]],np.cross(np.array(blade['vertices'])[f[1]],np.array(blade['vertices'])[f[2]]))/6 for f in blade['triangles']);relative_error=abs(sum(v)-surface_volume)/surface_volume;assert relative_error<1e-10
result=dict(passed=True,vertices=points.tolist(),cells=cells.tolist(),boundary_matches_original_facets=True,original_vertices_unchanged=True,positive_cells=True,volume_m3=float(sum(v)),volume_relative_error=relative_error,source_blade_sha256=config['blade']['sha256'],generator='MeshPy 2026.1.1 / TetGen pYQCM, no surface changes',tool_wheel_sha256=hashlib.sha256(next(Path('work/mesh_tools_download').glob('*.whl')).read_bytes()).hexdigest())
p=Path('work/exact_blade_cells.json');p.write_text(json.dumps(result,indent=2));print(dict(tets=len(cells),vertices=len(points),volume_relative_error=relative_error,boundary_matches_original_facets=True))
