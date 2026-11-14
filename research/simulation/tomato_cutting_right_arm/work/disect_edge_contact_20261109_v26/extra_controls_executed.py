from pathlib import Path
import json,numpy as np
from edge_blade import EdgeBlade,m,tensor,torch
from volume_certificate import certify
W=Path(__file__).resolve().parent
# Positive and adversarial whole-volume fixtures with independently known solids.
v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)*.001
f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]])
q=np.array([[3,3,3],[5,-5,-5],[-5,5,-5],[-5,-5,5]],float)*.001
t=np.array([[0,1,2,3]])
bad=certify(q,t,v,f);assert not bad['passed'] and bad.get('actual_violation')
good=certify(q+[.02,0,0],t,v,f);assert good['passed']
b=EdgeBlade();saved=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')
b.x.copy_(tensor(saved['x']));b.v.copy_(tensor(saved['v']));b.blade_enabled=True
b.blade_translation=np.array(json.loads((W/'probe_placement.json').read_text())['loaded_component_hold_translation_m'])
b.blade_velocity=np.zeros(3);b.geometry();history=b.fracture.state_dict()['history'].copy()
b.geometry();pure=bool(np.array_equal(history,b.fracture.state_dict()['history']))
b.reset();reset=bool(not b.blade_enabled and b.blade_dashpot is None and b.fracture_trial is None and not b.eligibility.any() and np.all(b.fracture.state_dict()['history']==0) and not b.blade_translation.any())
assert pure and reset
# Two quadrature resolutions at both actual coupled final states; immutable q/v.
comparisons=[]
for name in ['coarse','fine']:
 state=np.load(W/f'corrected_probe_{name}_final.npz');q=state['x'];vel=state['v'];values=[]
 for order in [512,1024]:
  c=EdgeBlade(order);ev,bd=c.contact(q,vel,b.blade_translation if False else np.array(json.loads((W/'probe_placement.json').read_text())['loaded_component_hold_translation_m']),np.zeros(3))
  force=ev['force'] if bd is None else ev['force']-bd.apply(tensor(vel)).cpu().numpy()
  values.append((force,ev))
 a,c=values;relative=float(np.linalg.norm(a[0]-c[0])/max(np.linalg.norm(c[0]),1e-6))
 comparisons.append(dict(run=name,force_quadrature_relative=relative,passed=relative<=.05))
 assert relative<=.05
out=dict(scope='Component controls; not damage-enabled moving-contact or full-stroke qualification',
 whole_volume_negative_control=bad,whole_volume_positive_control=good,
 repeated_trial_history_pure=pure,reset_clears_contact_and_fracture=reset,
 coupled_final_quadrature=compares if False else comparisons,passed=True)
(W/'extra_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
