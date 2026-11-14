from pathlib import Path
import sys,json,numpy as np
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;R=W.parents[1]
sys.path.insert(0,str(W.parent/'disect_edge_contact_20261109_v26'))
from volume_certificate import certify
state=np.load(W/'strong0032_final.npz');mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz')
raw=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rotation=A.T@ref['rotation']
plan=json.loads((W/'correction_plan.json').read_text());clock=float(state['step'])*float(state['dt']);u=clock/plan['durations_s'][0];r=10*u**3-15*u**4+6*u**5;depth=plan['downward_stroke_m']*r;curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T);T=np.array(plan['selected']['translation_m'])+[float(curve(depth)),-depth,0]
out=certify(state['x'],mesh['tets'],np.array(raw['vertices'])@rotation.T+T,np.array(raw['triangles']),limit=1e-5,max_depth=52,wall_cap=180.)
result=dict(scope='Read-only tighter diagnostic of accepted 26.5 ms state; 10 um diagnostic target is NOT a new physical stop',sim_s=clock,diagnostic=out)
(W/'saved_geometry_review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
