"""Read-only whole-tetrahedron clearance certificate after horizontal retreat.
Signed exact CAD distance is 1-Lipschitz. Every point in a tetrahedron lies
within sqrt(3/8)*diameter of some vertex (barycentric squared-distance bound).
Thus min_vertex_SDF - sqrt(3/8)*diameter is a conservative element bound.
This checks geometry, not fracture, force calibration or native robot clearance.
"""
from pathlib import Path
import sys,json,argparse,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'))
from blade_contact import CADBlade
p=argparse.ArgumentParser();p.add_argument('checkpoint');p.add_argument('--phase',choices=['slide','body'],default='slide');p.add_argument('--output',required=True);a=p.parse_args();state=np.load(a.checkpoint);plan=json.loads((W/'correction_plan.json').read_text());q=state['x'];T=np.array(plan['selected']['translation_m'])+[plan['front_lateral_path_m'][-1][1],-plan['downward_stroke_m'],0];T+=np.array(plan['blade_slide_direction_sim'])*plan['blade_slide_distance_m'];end=sum(plan['durations_s'][:2])
if a.phase=='body':T+=np.array(plan['bodyward_direction_sim'])*plan['horizontal_withdrawal_m'];end+=plan['durations_s'][2]
assert abs(float(state['step']*state['dt'])-end)<1e-10,'Clearance only checked at intended retreat endpoint'
cad=CADBlade();phi=cad.query(q,T)['phi'];m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');t=m['tets'];diameter=np.zeros(len(t))
for i in range(4):
 for j in range(i):diameter=np.maximum(diameter,np.linalg.norm(q[t[:,i]]-q[t[:,j]],axis=1))
lower=phi[t].min(1)-np.sqrt(3/8)*diameter-1e-9;out=dict(scope='Whole-material-tetrahedron clearance certificate; no contact force modification',phase=a.phase,sim_s=end,minimum_vertex_CAD_SDF_m=float(phi.min()),conservative_whole_tet_clearance_m=float(lower.min()),required_margin_m=.001,passed=bool(np.isfinite(lower).all() and lower.min()>=.001));Path(a.output).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
