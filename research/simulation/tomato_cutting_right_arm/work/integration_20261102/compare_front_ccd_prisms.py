from pathlib import Path
import sys,json,time,hashlib,numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[2];sys.path[:0]=[str(r/'.deps/ipctk-1.6.1-local-cp312'),str(r/'rl')];import ipctk
from tomato_swept_front import SweptFrontDetector
from tomato_front_sweep_reference import translated_front_events
ipctk.set_num_threads(1);source=r/'runs/offline/front_prism_reference_20261102_02/ccd_comparison_inputs.npz';data=np.load(source);a=data['front0'];b=data['front1'];m=data['material'];bent=data['bent'];patches=data['patches'];R=Rotation.from_rotvec([.23,-.41,.12]).as_matrix();out=r/'runs/offline/front_ccd_reference_20261102_01';out.mkdir(exist_ok=True);cases=[];start=time.monotonic();shift=np.array([.001,0,0])
# Moving-target reference uses the exact common-translation relative frame.
fixtures=[('shallow',a,a+[0,0,-.0317],m,m,a,a+[0,0,-.0317],m),('deformed',a,b,bent,bent,a,b,bent),('moving_target',a,b,m,m+shift,a,b-shift,m),('rotated_shallow',a@R.T,a@R.T+np.array([0,0,-.0317])@R.T,m@R.T,m@R.T,a@R.T,a@R.T+np.array([0,0,-.0317])@R.T,m@R.T)]
for label,f0,f1,m0,m1,ra,rb,rm in fixtures:
 truth=translated_front_events(ra,rb,rm,patches);expected=sorted(e['patch']for e in truth['events'])
 for tolerance in [1e-9,1e-10]:
  row=SweptFrontDetector(ipctk,tolerance=tolerance).detect(f0,f1,m0,m1,patches);actual=sorted(e['patch']for e in row['events']);row.update(case=label,tolerance_m=tolerance,reference_patch_ids=expected,mask_matches_exact_positive_area_reference=actual==expected)
  cases.append(row);(out/'partial.json').write_text(json.dumps(dict(cases=cases,elapsed_wall_s=time.monotonic()-start),indent=2)+'\n');print(label,tolerance,len(actual),len(expected),actual==expected,flush=True)
  if actual!=expected:raise ValueError('Conservative CCD mask differs from independent positive-area prism reference; do not use it to commit fracture')
report=dict(passed=True,cases=cases,elapsed_wall_s=time.monotonic()-start,scope='Continuous geometry candidate versus independent positive-area prism intersections for a translating actual CAD band, current deformed snapshots, target rigid translation, proper common rotation and two CCD tolerances. No nonuniform within-step target deformation, active eligibility/history, actual robot motion, physical support or performed cut qualified.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [source,r/'rl/tomato_swept_front.py',r/'rl/tomato_front_sweep_reference.py',Path(ipctk.__file__),Path(__file__)]});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print('seconds',report['elapsed_wall_s'],flush=True)
