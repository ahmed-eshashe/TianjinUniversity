import json,sys,hashlib
from pathlib import Path
import numpy as np,torch
from scipy.spatial.transform import Rotation
from tomato_surface_cohesion import SurfaceCohesion,patch_response
from tomato_coupled_contact import cut_pairs
from tomato_objective_cohesion_reference import make_patch,response
r=Path(__file__).resolve().parents[2];source=r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json'
d=json.loads(source.read_text());x=np.array([n['position_m'] for n in d['nodes']]);pairs=cut_pairs(d);old=SurfaceCohesion(d,pairs,0.);q=Rotation.from_rotvec([.3,.6,-.2]).as_matrix();records=[]
torch.set_num_threads(1)
for patch in old.patches:
 local=x[pairs[patch['indices']]];law=patch['law'];p=make_patch(local,patch['weights'],patch['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m))
 for label,gap in [('tensile',[.0005,0,0]),('mixed_open',[.002,.0003,.0002]),('mixed_compressed',[-.0002,.002,.0003]),('pure_compression',[-.001,0,0])]:
  z=local.copy();z[:,1]+=gap;a=response(z,p,eligible=True);b=response(z@q.T+[.2,-.1,.3],p,eligible=True)
  force_error=float(np.max(np.abs(a['force_n']@q.T-b['force_n'])));energy_error=abs(a['stored_energy_j']-b['stored_energy_j']);moment=float(np.linalg.norm(np.cross(z,a['force_n']).sum(axis=(0,1))));balance=float(np.linalg.norm(a['force_n'].sum(axis=(0,1))))
  if force_error>1e-9 or energy_error>1e-12 or balance>1e-10 or moment>1e-10:raise ValueError('Objective invariants failed')
  row=dict(patch_id=patch['id'],case=label,force_rotation_error_n=force_error,energy_rotation_error_j=energy_error,net_force_n=balance,net_moment_nm=moment,trial_history=a['trial_history'])
  if label=='tensile':
   ref=patch_response(np.tile(gap,(len(local),1)),patch['weights'],patch['stiffness'],0.)
   row['legacy_tensile_force_error_n']=float(np.max(np.abs(a['force_n'][:,1]+ref['gradient_n'])))
   if row['legacy_tensile_force_error_n']>1e-10:raise ValueError('Tensile law changed')
  if label=='pure_compression' and a['trial_history'][1]!=0:raise ValueError('Pure compression damage')
  records.append(row)
result=dict(patches=47,cases=len(records),passed=True,scope='CPU float64 energy/force reference only; no native stepping or full-fruit self-contact qualification',records=records,source_sha256={str(source):hashlib.sha256(source.read_bytes()).hexdigest()})
(r/'work/integration_20261102/objective_registry_check.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(records),'actual-registry objective/mixed-mode reference cases')
