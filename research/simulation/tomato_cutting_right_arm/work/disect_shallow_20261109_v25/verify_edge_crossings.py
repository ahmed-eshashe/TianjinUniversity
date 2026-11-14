from pathlib import Path
import sys,json,numpy as np
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));from blade_contact import CADBlade
p=json.loads((W/'correction_plan.json').read_text());r=json.loads((W/'material_edge_audit_result.json').read_text());t=r['sim_s'];u=t/p['durations_s'][0];depth=p['downward_stroke_m']*(10*u**3-15*u**4+6*u**5);curve=PchipInterpolator(*np.array(p['front_lateral_path_m']).T);T=np.array(p['selected']['translation_m'])+[float(curve(depth)),-depth,0];cad=CADBlade();rows=[]
for name in ['coarse0040','fine0040']:
 q=np.load(W/f'{name}_final.npz')['x']
 for e in r['examples']:
  if not e['point_detector_misses_crossing']:continue
  ids=[e['interior_node'],e['cut_node']];a,b=q[ids];line=a[None]+np.linspace(0,1,1001)[:,None]*(b-a);query=cad.query(line,T);phi=query['phi'];rows.append(dict(run=name,interior_node=ids[0],cut_node=ids[1],endpoint_SDF_m=phi[[0,-1]].tolist(),most_negative_interior_SDF_m=float(phi.min()),verified_missed_crossing=bool(phi[0]>1e-6 and phi[-1]>1e-6 and phi.min()< -1e-6),exceeds_original_point_penetration_limit=bool(phi.min()<-.0001)))
out=dict(scope='Independent exact solid-angle/distance queries along saved material edges; no ray-intersection algorithm or simulation used',rows=rows,verified_missed_crossings=sum(r['verified_missed_crossing'] for r in rows),verified_edges_exceeding_0p1mm_limit=sum(r['verified_missed_crossing'] and r['exceeds_original_point_penetration_limit'] for r in rows),coverage_failure_confirmed=bool(any(r['verified_missed_crossing'] and r['exceeds_original_point_penetration_limit'] for r in rows)));(W/'edge_crossing_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
