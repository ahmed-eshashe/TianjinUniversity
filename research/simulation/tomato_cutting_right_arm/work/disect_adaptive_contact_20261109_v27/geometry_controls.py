from pathlib import Path
import json,numpy as np
from scipy.interpolate import PchipInterpolator
from adaptive_contact import AdaptiveContact
W=Path(__file__).resolve().parent;R=W.parents[1]
v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)*.001
f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]])
c=AdaptiveContact.__new__(AdaptiveContact);c.edges=np.array([[0,1]]);c.edge_weights=np.ones(1);c.force_atol=1e-10;c.rtol=1e-6;c.max_depth=40
q=np.array([[-.002,.00013,.00021],[.002,.00013,.00021]]);zero=np.zeros_like(q)
a=c.evaluate(q,zero,v,f,np.zeros(3),np.zeros(3))
assert a['inside_intervals']>0 and len(a['phi'])>0
angle=.471;rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
shift=np.array([.004,.002,-.001])
b=c.evaluate(q@rot.T+shift,zero,v@rot.T+shift,f,np.zeros(3),shift)
objective=float(np.max(abs(b['force']-a['force']@rot.T)));assert objective<1e-8
assert abs(b['energy_J']-a['energy_J'])<1e-12
assert np.linalg.norm(a['reaction']+a['force'].sum(0))<1e-12
assert np.linalg.norm(a['moment']+np.cross(q,a['force']).sum(0))<1e-12
feature=[]
for eps in [1e-6,1e-8,1e-10]:
 energies=[]
 for sign in [-1,1]:
  qp=np.array([[-.002,0,.0002],[0,.002+sign*eps,.0002]])
  energies.append(c.evaluate(qp,zero,v,f,np.zeros(3),np.zeros(3))['energy_J'])
 feature.append(dict(epsilon_m=eps,energy_J=energies,jump_J=abs(energies[1]-energies[0])))
assert feature[-1]['jump_J']<1e-12
# Independent saved missed-crossing fixtures from BOTH original timestep runs.
old=W.parent/'disect_shallow_20261109_v25';p=json.loads((old/'correction_plan.json').read_text())
u=.04/p['durations_s'][0];depth=p['downward_stroke_m']*(10*u**3-15*u**4+6*u**5)
curve=PchipInterpolator(*np.array(p['front_lateral_path_m']).T)
T=np.array(p['selected']['translation_m'])+[float(curve(depth)),-depth,0]
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
rotation=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation']
vertices=np.array(d['vertices'])@rotation.T+T;faces=np.array(d['triangles'])
audit=json.loads((old/'edge_crossing_verification.json').read_text());detected=[]
for row in audit['rows']:
 state=np.load(old/f"{row['run']}_final.npz");ids=[row['interior_node'],row['cut_node']]
 result=c.evaluate(state['x'][ids],np.zeros((2,3)),vertices,faces,np.zeros(3),T)
 ok=result['inside_intervals']>0 and len(result['phi'])>0 and result['energy_J']>0
 assert ok
 detected.append(dict(run=row['run'],material_edge=ids,detected=bool(ok)))
out=dict(scope='Adaptive contact geometric controls; no physical stepping',
         rigid_force_error_N=objective,grazing_feature_continuity=feature,
         saved_missed_crossings=detected,passed=True)
(W/'geometry_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
