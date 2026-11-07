from pathlib import Path
import sys,json,numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
prepared=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');origin=prepared['world_from_sim_translation_m'];ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());R=ref['rotation'];t=ref['translation']-origin
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(r/'.deps/ipctk-1.6.1-local-cp312'))
import ipctk
from tomato_cut_eligibility import CutEligibility
from tomato_swept_front import SweptFrontDetector
ipctk.set_num_threads(1)
reg=np.load(r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz');front=json.loads((r/'runs/offline/cut_front_registration_20261102_02/registration.json').read_text())['front']['face_ids'];solid=json.loads((r/'work/exact_blade_cells.json').read_text());pose=np.r_[t+origin+[0,0,.0001],Rotation.from_matrix(R).as_quat()]
elig=CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),prepared['x_sim']+origin,pose)
pose=np.r_[ref['translation'],Rotation.from_matrix(ref['rotation']).as_quat()]
elig=CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),prepared['x_sim']+origin,pose)
rows=[]
for z in np.linspace(pose[2],.015,53)[1:]:
 end=pose.copy();end[2]=z;end[0]+=-R[2,2]/R[0,2]*(z-pose[2])
 trial=elig.trial(prepared['x_sim']+origin,end)
 elig.commit(trial,accepted=True)
 row=dict(z=float(z),inward=list(trial.inward_patches),overlap=list(trial.overlapping_patches),eligible=np.flatnonzero(trial.eligible).tolist())
 rows.append(row)
 if trial.inward_patches: print(row,flush=True)
(w/'tangent_geometry_scan.json').write_text(json.dumps(dict(pose=pose.tolist(),rows=rows,scope='Frozen material geometry scan only, not mechanics'),indent=2))
