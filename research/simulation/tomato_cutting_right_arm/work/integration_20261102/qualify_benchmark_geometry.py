from pathlib import Path
import sys,json,hashlib,numpy as np
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'rl'))
from tomato_benchmark_metrics import reference_geometry,evaluate_cap,symmetric_refinement_error
p=r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json';d=json.loads(p.read_text());g=reference_geometry(d);x=g['reference'];cases=[]
for name,theta,shift,scale in [('reference',0,[0,0,0],1),('rigid_pose',.63,[.4,-.2,.1],1),('scale_negative',.3,[.2,.1,-.1],1.1)]:
 c,s=np.cos(theta),np.sin(theta);rot=np.array([[c,-s,0],[s,c,0],[0,0,1]]);y=(x-x.mean(0))*scale@rot.T+x.mean(0)+shift;row=evaluate_cap(y,g);row['case']=name
 if scale==1 and row['maximum_profile_error_m']>1e-10:raise ValueError('Rigid registration changed shape')
 if scale!=1 and row['maximum_profile_error_m']<.0005:raise ValueError('Shape scaling was hidden')
 cases.append(row)
assert symmetric_refinement_error(0,0,1e-6)==0
assert symmetric_refinement_error(0,1e-7,1e-6)==.1
out=r/'runs/offline/benchmark_geometry_20261102_01';out.mkdir(exist_ok=True)
report=dict(passed=True,cases=cases,sample_yz_reference_m=g['sample_yz'].tolist(),scope='Reference geometry and metric controls only. No released cap or actual cut.',source_sha256={str(q):hashlib.sha256(q.read_bytes()).hexdigest()for q in [p,r/'rl/tomato_benchmark_metrics.py',Path(__file__)]})
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(report['sample_yz_reference_m']);print([(c['case'],c['reference_profile_m'],c['maximum_profile_error_m'])for c in cases])
