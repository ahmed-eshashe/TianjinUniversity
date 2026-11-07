from pathlib import Path
import json,hashlib
import numpy as np
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');run=R/'runs/native/corrected_exchange_operator_20261102_01';out=R/'work/corrected_contact_exchange_20261102/independent_readback01';out.mkdir(exist_ok=False);m=json.loads((run/'measurements.json').read_text());s=json.loads((run/'supervisor_result.json').read_text());assert s['passed']and s['worker']['controlled_steps']==0 and s['worker']['deformable_steps']==0 and not s['remaining_live_group_members'];maximum=0.;results=[]
for case in m['cases']:
 label=case['case'];z=np.load(run/(label+'_operator.npz'));x=z['x_world'];f=z['force'];cp=z['geometry_com'];cn=z['native_com'];expected=np.r_[-f.sum(0),-np.cross(x-cn,f).sum(0)];w=z['requested_native_wrench'];err=float(abs(w-expected).max());maximum=max(maximum,err);assert err<1e-10
 assert np.array_equal(z['float32_queue_wrench'],w.astype(np.float32).astype(float));assert np.linalg.norm(w[:3])<=.01 and np.linalg.norm(w[3:])<=.0002 and case['maximum_penetration_m']<=.0001
 expected_at_origin=np.r_[-f.sum(0),-np.cross(x,f).sum(0)];world_origin=np.r_[w[:3],w[3:]+np.cross(cn,w[:3])];assert abs(world_origin-expected_at_origin).max()<1e-10
 request=case['request'];dt=request['time_end_s']-request['time_start_s'];assert request['target_steps']==2 and abs(dt-1/38400)<1e-15
 assert abs(np.array(request['reaction_impulse_world'])-z['reaction_geometry_COM']*dt).max()<1e-15
 assert case['cleared_before_physics']
 if label=='clear':assert not np.any(f)and not np.any(w)and case['clear_CAD_bound_gap_m']>.015 and not case['queued_not_stepped']
 else:assert case['pressure_samples']==20736 and np.linalg.norm(w[:3])>1e-4 and case['queued_not_stepped']and case['packet_domain_motion_m']<=5e-6
 results.append(dict(case=label,resultant_force_n=float(np.linalg.norm(w[:3])),native_COM_moment_nm=float(np.linalg.norm(w[3:])),independent_reaction_error_n_nm=err,queued_not_stepped=case['queued_not_stepped']))
a=np.load(run/'positive_operator.npz');b=np.load(run/'replay_operator.npz');assert np.array_equal(a['requested_native_wrench'],b['requested_native_wrench'])and np.max(abs(a['force']-b['force']))<1e-12
pins=json.loads((run/'source_closure.json').read_text())['source_sha256'];assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items())
report=dict(passed=True,cases=results,maximum_reaction_error_n_nm=maximum,verified_source_files=len(pins),physical_steps=0,deformable_steps=0,scope='Frozen CAD/reaction/subcycle accumulator/origin shift/float32 Native queue request. Synthetic interval weights; no physical time or impulse application, no dynamic force balance, energy/work, continuous approach, touch or fracture qualification.',source_sha256={str(run/p):hashlib.sha256((run/p).read_bytes()).hexdigest()for p in ['measurements.json','supervisor_result.json','positive_operator.npz','replay_operator.npz','clear_operator.npz','source_closure.json']});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
