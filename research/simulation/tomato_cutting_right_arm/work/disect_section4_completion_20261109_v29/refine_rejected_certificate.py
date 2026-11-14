from pathlib import Path
import sys,json,numpy as np
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;R=W.parents[1];sys.path.insert(0,str(W.parent/'disect_edge_contact_20261109_v26'))
from volume_certificate import certify
m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');saved=np.load(W/'resolve0026_rejected_trial.npz');p=json.loads((W/'correction_plan.json').read_text());rejected=json.loads((W/'resolve0026_rejected_volume_guard.json').read_text());t=rejected['trial_time_s'];u=t/p['durations_s'][0];depth=p['downward_stroke_m']*(10*u**3-15*u**4+6*u**5);curve=PchipInterpolator(*np.array(p['front_lateral_path_m']).T);T=np.array(p['selected']['translation_m'])+[float(curve(depth)),-depth,0]
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');rot=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation'];v=np.array(d['vertices'])@rot.T+T;f=np.array(d['triangles'])
rows=[]
for limit in [1e-4,9.97e-5]:
 result=certify(saved['x'],m['tets'],v,f,limit=limit,max_depth=52,wall_cap=120)
 rows.append(dict(requested_limit_m=limit,**result))
out=dict(scope='Read-only higher-resolution certificate of previously rejected trial; not a physical step or accepted material history',trial_time_s=t,rows=rows)
(W/'rejected_certificate_refinement.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
