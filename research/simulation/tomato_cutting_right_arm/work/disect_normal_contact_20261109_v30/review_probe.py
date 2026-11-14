from pathlib import Path
import json,numpy as np
W=Path(__file__).resolve().parent
d=json.loads((W/'moving_probe_result.json').read_text());assert len(d['runs'])==2
a,b=d['runs'];aa={round(r['sim_s'],12):r for r in a['rows']};bb={round(r['sim_s'],12):r for r in b['rows']}
common=sorted(set(aa)&set(bb));differences=[]
for t in common:
 x,y=aa[t],bb[t]
 differences.append(abs(x['force_N']-y['force_N'])/max(y['force_N'],1e-6))
physical=all(r['stop']=='completed' and all(row['passed'] and row['damage_max']==0 and (not row.get('solver') or max(row['solver']['relative_residual'],row['solver']['inner_max_residual'])<=1e-9) for row in r['rows']) for r in d['runs'])
out={'scope':'Fresh 2 ms / 42 um nonfracturing contact component; not Gate B','operator_controls_passed':json.loads((W/'controls_result.json').read_text())['passed'],'switch_controls_passed':json.loads((W/'switch_controls_result.json').read_text())['passed'],'adapter_controls_passed':json.loads((W/'adapter_controls_result.json').read_text())['passed'],'physical_checks_passed':physical,'common_time_samples':len(common),'maximum_common_time_force_norm_relative':max(differences),'final_vector_geometry_comparison':d.get('comparison'),'peak_sampled_penetration_m':max(x['penetration_m'] for r in d['runs'] for x in r['rows']),'wall_s':[r['wall_s'] for r in d['runs']],'gate_b_passed':False}
out['passed']=bool(physical and out['operator_controls_passed'] and out['switch_controls_passed'] and out['adapter_controls_passed'] and d.get('comparison',{}).get('passed',False) and max(differences)<=.05)
(W/'fresh_probe_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if out['passed']:
 (W/'candidate_controls_gate.json').write_text(json.dumps({'passed':True,'scope':'Independent stronger normal-contact and fresh nonfracturing probe controls only','gate_b_passed':False,'normal_contact_stiffness_N_per_m':2e6},indent=2)+'\n')
assert out['passed']
