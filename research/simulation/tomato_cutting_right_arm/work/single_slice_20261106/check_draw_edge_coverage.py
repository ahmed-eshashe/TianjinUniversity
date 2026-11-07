"""Frozen accepted-geometry screen; not a prediction of deforming contact."""
from pathlib import Path
import json, sys
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1]
sys.path[:0]=[str(r/'rl'),str(r/'.deps/ipctk-1.6.1-local-cp312')]
import ipctk
from tomato_cut_eligibility import CutEligibility,freeze
from tomato_swept_front import SweptFrontDetector
ipctk.set_num_threads(1)
blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
solid=json.loads((r/'work/exact_blade_cells.json').read_text())
reg=np.load(r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz')
front=json.loads((r/'runs/offline/cut_front_registration_20261102_02/registration.json').read_text())['front']['face_ids']
prepared=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz')
ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
origin=np.array([-.0225,0,.0295])
e=CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),prepared['x_sim']+origin,np.r_[ref['translation'],Rotation.from_matrix(ref['rotation']).as_quat()])
z=np.load(w/'robot_cut13/checkpoints/step_005375.npz');world=z['x']+origin
pose=np.r_[z['blade_translation']+origin,Rotation.from_matrix(z['blade_rotation']).as_quat()]
e.world=freeze(world);e.pose=freeze(pose);e.seen=freeze(z['seen']);e.eligible=freeze(z['eligible'])
rows=[]
offsets=[np.array([0,-u,0]) for u in np.linspace(0,.06,31)[1:]]+[np.array([u,-.06,0]) for u in np.linspace(0,.018,37)[1:]]
for index,offset in enumerate(offsets):
    p=pose.copy();p[:3]+=offset
    trial=e.trial(world,p);e.commit(trial,accepted=True)
    rows.append(dict(offset_m=offset.tolist(),seen=int(e.seen.sum()),eligible=int(e.eligible.sum()),new_edge_events=list(trial.inward_patches)))
result=dict(scope='Frozen accepted geometry only; not dynamic qualification',rows=rows,unreached=np.flatnonzero(~e.seen).tolist(),all_reached=bool(e.seen.all()))
(w/'draw_edge_coverage.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
