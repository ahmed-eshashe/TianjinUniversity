import json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_surface_cohesion import SurfaceCohesion
from tomato_coupled_contact import cut_pairs
from tomato_objective_cohesion_reference import make_patch,response
from tomato_objective_force_reference import explicit_force
r=Path(__file__).resolve().parents[2];d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());x=np.array([n['position_m'] for n in d['nodes']]);pairs=cut_pairs(d);patches=SurfaceCohesion(d,pairs,0.).patches;maximum=0.;cases=0
q=Rotation.from_rotvec([.3,.6,-.2]).as_matrix()
for p in patches:
 ids=pairs[p['indices']];l=p['law'];m=make_patch(x[ids],p['weights'],p['stiffness'],(l.onset_m,l.failure_m,l.stiffness_n_m))
 for gap in [[.0005,.0002,.0003],[-.0005,.002,0],[.003,0,.0001]]:
  for rotation in [np.eye(3),q]:
   pos=x[ids].copy();pos[:,1]+=gap;pos=pos@rotation.T+[.2,-.1,.3]
   f=explicit_force(pos,m,eligible=True);ref=response(pos,m,eligible=True)['force_n'];error=float(np.abs(f-ref).max());maximum=max(maximum,error);cases+=1
   if error>1e-10:raise ValueError(error)
(r/'work/integration_20261102/explicit_force_check.json').write_text(json.dumps(dict(passed=True,cases=cases,maximum_force_error_n=maximum,scope='Explicit NumPy force formula vs independent CPU automatic derivatives; no native solver stepping'),indent=2)+'\n');print(cases,maximum)
