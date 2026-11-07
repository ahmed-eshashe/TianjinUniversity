from pathlib import Path
import sys,json,hashlib,time,numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[2];sys.path[:0]=[str(r/'.deps/ipctk-1.6.1-local-cp312'),str(r/'rl')];import ipctk
from tomato_cut_eligibility import CutEligibility
from tomato_swept_front import SweptFrontDetector
ipctk.set_num_threads(1);s=r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json';b=r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';cells=r/'work/exact_blade_cells.json';regpath=r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz';frontpath=r/'runs/offline/cut_front_registration_20261102_02/registration.json';d=json.loads(s.read_text());blade=json.loads(b.read_text());solid=json.loads(cells.read_text());reg=np.load(regpath);front=json.loads(frontpath.read_text())['front']['face_ids'];x=np.array([n['position_m']for n in d['nodes']])+[0,0,.002];R=np.array([[0,0,1],[1,0,0],[0,1,0]]);local=np.array(blade['vertices']);f=np.array(blade['triangles'])[front];center=float(local[f].mean((0,1))[2]);pose=np.r_[[d['cut_x_m']-center,.301608,.09],Rotation.from_matrix(R).as_quat()];cases=[];start=time.monotonic()
def build(world=x,p=pose):return CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),world,p)
def row(label,e,t):return dict(case=label,seen=int(e.seen.sum()),eligible=int(e.eligible.sum()),trial_inward=len(t.inward_patches),trial_overlap=len(t.overlapping_patches),trial_eligible=int(t.eligible.sum()))
e=build();deep=pose.copy();deep[2]=0.;trial=e.trial(x,deep);e.commit(trial,accepted=False)
if e.seen.any() or e.eligible.any() or not np.array_equal(e.pose,pose):raise ValueError('Rejected geometry mutated eligibility')
cases.append(row('rejected_deep_sweep',e,trial));shallow=pose.copy();shallow[2]-=.0317;trial=e.trial(x,shallow);e.commit(trial,accepted=True)
if not 0<e.eligible.sum()<47 or not set(np.flatnonzero(e.eligible))<=set(trial.inward_patches):raise ValueError('Missing bounded shallow inward event')
expected=e.eligible.copy();cases.append(row('accepted_shallow_sweep',e,trial));trial=e.trial(x,pose);e.commit(trial,accepted=True)
if e.eligible.any() or not e.seen.any():raise ValueError('Withdrawal retained active rows or lost explicit seed semantics')
cases.append(row('withdrawal_deactivates',e,trial));e.reset(x,pose);trial=e.trial(x,shallow);e.commit(trial,accepted=True)
if not np.array_equal(e.eligible,expected):raise ValueError('Dirty reset/replay changed geometric eligibility')
cases.append(row('reset_replay',e,trial));stale=False
try:e.commit(trial,accepted=True)
except ValueError:stale=True
if not stale:raise ValueError('Stale accepted trial reused')
# Broad-face entry: the cutting front remains below the target throughout.
start_broad=pose.copy();start_broad[0]+=.02;start_broad[2]=.02;e=build(p=start_broad);end_broad=start_broad.copy();end_broad[0]=pose[0];trial=e.trial(x,end_broad);e.commit(trial,accepted=True)
if not trial.overlapping_patches or e.seen.any() or e.eligible.any():raise ValueError('Broad-face overlap became a cut')
cases.append(row('broad_face_press_no_cut',e,trial));retreat=end_broad.copy();retreat[2]=.09;trial=e.trial(x,retreat);e.commit(trial,accepted=True)
if trial.inward_patches or e.seen.any() or e.eligible.any():raise ValueError('Retreat seeded inward fracture')
cases.append(row('reverse_edge_motion_no_cut',e,trial))
# Common rigid motion preserves masks; fixed orientation during each interval.
rotation=Rotation.from_rotvec([.23,-.41,.12]);rx=x@rotation.as_matrix().T+[.2,-.1,.3]
def transformed(p):return np.r_[rotation.apply(p[:3])+[.2,-.1,.3],(rotation*Rotation.from_quat(p[3:])).as_quat()]
e=build(world=rx,p=transformed(pose));trial=e.trial(rx,transformed(shallow));e.commit(trial,accepted=True)
if not np.array_equal(e.eligible,expected):raise ValueError('Rigid-frame change altered eligibility')
cases.append(row('common_rigid_rotation',e,trial))
out=r/'runs/offline/cut_eligibility_20261102_02';out.mkdir(exist_ok=True);report=dict(passed=True,cases=cases,elapsed_wall_s=time.monotonic()-start,scope='Transactional geometry-only candidate. Actual CAD/registered deformed footprints, current solid overlap and inward swept-edge event. No permanent active rows, no fracture history mutation, no coupled mechanics or performed cut. General nonuniform within-step deformation and one-interval-lag accuracy remain to qualify.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [s,b,cells,regpath,frontpath,r/'rl/tomato_cut_eligibility.py',r/'rl/tomato_swept_front.py',r/'rl/tomato_cut_geometry.py',r/'rl/tomato_exact_blade_coverage.py',Path(ipctk.__file__),Path(__file__)]});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);print('seconds',report['elapsed_wall_s'])
