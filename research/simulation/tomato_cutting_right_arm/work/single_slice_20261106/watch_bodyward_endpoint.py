"""One bounded read-only follow-up to the existing withdrawal process.
Does not launch a new simulation or change material/robot state.
"""
from pathlib import Path
import time,json,subprocess,sys
import numpy as np
w=Path(__file__).parent;r=w.parents[1];run=w/'robot_cut17';deadline=time.monotonic()+86500
while not (run/'supervisor_result.json').exists():
 if time.monotonic()>deadline:
  (run/'endpoint_review.json').write_text(json.dumps({'status':'watch_deadline_reached','full_slice_success':False}));raise SystemExit(1)
 time.sleep(10)
checkpoints=sorted((run/'checkpoints').glob('step_*.npz'))
if not checkpoints:raise RuntimeError('No complete accepted checkpoint to assess')
cp=checkpoints[-1];m=json.loads(cp.with_suffix('.json').read_text());z=np.load(cp)
subprocess.run([sys.executable,str(w/'assess_remaining_interface.py'),str(cp)],check=True)
route=json.loads((w/'bodyward_withdrawal_plan_v1.json').read_text());origin=np.load(route['transition_checkpoint']);F=np.array(route['target_rotation']);delta=F@(z['blade_translation']-origin['blade_translation']);direction=np.array(route['direction_world']);state=np.array(z['x'])+[-.0225,0,.0295]
report={'status':'accepted_endpoint_assessed','checkpoint':str(cp),'route_finished':bool(m['progress']>=1),'horizontal_retreat_m':float(delta@direction),'height_change_m':float(delta[2]),'remaining_connections':int(np.sum(z['history'][:,1]<1)),'fully_failed_connections':int(np.sum(z['history'][:,1]>=1)),'reaction_force_N':float(np.linalg.norm(m['reaction'][:3])),'target_bounds_canonical_m':[state.min(0).tolist(),state.max(0).tolist()],'full_slice_success':False,'next_action':'Review endpoint clearance, interface geometry and finite-board support before planning the finishing stroke. No further simulation launched.','note':'Reaction and bounding boxes alone do not establish surface clearance or complete slice qualification.'}
(run/'endpoint_review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
