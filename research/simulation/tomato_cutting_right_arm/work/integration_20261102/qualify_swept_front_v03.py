from pathlib import Path
import sys,json,hashlib,time,numpy as np
r=Path(__file__).resolve().parents[2];sys.path[:0]=[str(r/'.deps/ipctk-1.6.1-local-cp312'),str(r/'rl')]
import ipctk
from tomato_swept_front import SweptFrontDetector
from tomato_cut_geometry import current_footprints
ipctk.set_num_threads(1);out=r/'runs/offline/swept_front_20261102_03';out.mkdir(exist_ok=True);cases=[];start=time.monotonic()
a=np.array([[0.,-.01,-.01],[0,.01,-.01],[0,0,.01]])
b=np.array([[-.01,-.004,0],[-.01,.004,0],[-.01,0,.005]])
for name,a0,a1,b0,b1,expect in [('tunneling',a,a,b,b+[.02,0,0],True),('clear',a,a,b,b+[0,0,.001],False),('moving_both',a,a+[-.01,0,0],b,b+[.01,0,0],True),('initial_contact',a,a,b+[.01,0,0],b+[.01,0,0],True)]:
 for tolerance in [1e-9,1e-10]:
  detector=SweptFrontDetector(ipctk,tolerance=tolerance);row=detector.detect(a0[None],a1[None],b0[None],b1[None],[0]);row.update(case=name,tolerance_m=tolerance)
  if bool(row['events'])!=expect:raise ValueError(f'{name} failed: {row}')
  cases.append(row)
# Actual CAD / all current material footprints. This is an offline prescribed
# geometry sweep, deliberately not a robot command or mechanical fracture run.
d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());reg=np.load(r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz');frontids=json.loads((r/'runs/offline/cut_front_registration_20261102_02/registration.json').read_text())['front']['face_ids'];vertices=np.array(blade['vertices']);faces=np.array(blade['triangles']);rotation=np.array([[0,0,1],[1,0,0],[0,1,0]]);center_z=float(vertices[faces[frontids]].mean((0,1))[2]);origin=np.array([d['cut_x_m']-center_z,.301608,.09]);front0=(vertices@rotation.T+origin)[faces[frontids]];front1=front0+[0,0,-.09];x=np.array([n['position_m']for n in d['nodes']])+[0,0,.002];material=current_footprints(x,reg)
for name,f0,f1,m0,m1,expect in [('actual_full_sweep',front0,front1,material,material,47),('actual_clear',front0+[.01,0,0],front1+[.01,0,0],material,material,0),('common_rigid_motion',front0+[.2,-.1,.3],front1+[.2,-.1,.3],material+[.2,-.1,.3],material+[.2,-.1,.3],47)]:
 row=SweptFrontDetector(ipctk).detect(f0,f1,m0,m1,reg['patch']);row['case']=name
 if len(row['events'])!=expect:raise ValueError(f'{name}: {len(row["events"])} != {expect}')
 cases.append(row);(out/'partial.json').write_text(json.dumps(dict(cases=cases,elapsed_wall_s=time.monotonic()-start),indent=2)+'\n')
inputs=[r/'rl/tomato_swept_front.py',r/'rl/tomato_cut_geometry.py',Path(__file__),Path(ipctk.__file__),r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz']
report=dict(passed=True,cases=cases,ipctk_version=ipctk.__version__,elapsed_wall_s=time.monotonic()-start,cad_edge_center_local_z_m=center_z,scope='Offline geometry-only positive/negative controls. Conservative CCD events do not certify a performed cut, active blade overlap, eligible fracture, physical contact, actual robot motion or complete trajectory accuracy.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print([(c['case'],len(c['events']),c['candidate_triangle_pairs'])for c in cases]);print('seconds',report['elapsed_wall_s'])
