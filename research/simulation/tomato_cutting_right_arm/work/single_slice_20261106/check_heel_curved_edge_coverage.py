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

# Bring the straight heel over the bent interface, then descend along its fitted slope.
# All poses are prospective; the accepted checkpoint is read-only.
R0=Rotation.from_quat(pose[3:]).as_matrix()
heel=np.array([-.02028,.05,.00105]);local=(heel-pose[:3])@R0
poses=[]
def append(p,n):
    a=poses[-1].copy() if poses else pose.copy()
    rot0=Rotation.from_quat(a[3:]);rv=(Rotation.from_quat(p[3:])*rot0.inv()).as_rotvec()
    for u in np.linspace(0,1,n+1)[1:]:
        poses.append(np.r_[a[:3]*(1-u)+p[:3]*u,(Rotation.from_rotvec(rv*u)*rot0).as_quat()])
p=pose.copy();p[2]+=.04;append(p,40)
rot=Rotation.from_euler('z',np.arctan(.117))*Rotation.from_matrix(R0)
center=np.array([-.013-.65*.035,0,.035])
p=np.r_[center-rot.as_matrix()@local,rot.as_quat()];append(p,150)
for h in np.linspace(.035,.0015,68)[1:]:
    center=np.array([-.0095-.0035*np.clip((h-.0015)/.006,0,1)-.65*h,0,h]);p=np.r_[center-rot.as_matrix()@local,rot.as_quat()];append(p,1)
rows=[]
for i,p in enumerate(poses):
    trial=e.trial(world,p);e.commit(trial,accepted=True)
    bv=e.local_vertices@Rotation.from_quat(p[3:]).as_matrix().T+p[:3]
    rows.append(dict(index=i,seen=int(e.seen.sum()),eligible=int(e.eligible.sum()),new_edge_events=list(trial.inward_patches),blade_min_z_m=float(bv[:,2].min())))
result=dict(scope='Frozen accepted geometry only; not dynamic qualification',rows=rows,unreached=np.flatnonzero(~e.seen).tolist(),all_reached=bool(e.seen.all()),poses=np.asarray(poses).tolist(),minimum_clearance_m=min(row['blade_min_z_m'] for row in rows))
(w/'heel_curved_edge_coverage.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k not in ['rows','poses']})
