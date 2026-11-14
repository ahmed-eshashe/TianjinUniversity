from pathlib import Path
import numpy as np,json
W=Path(__file__).resolve().parent;contract=json.loads((W.parent/'contract.json').read_text())
def compare(a,b):
    a=np.load(W/f'{a}_trajectory.npz');b=np.load(W/f'{b}_trajectory.npz');assert np.array_equal(a['t'],b['t']);rows=[]
    for i,t in enumerate(a['t']):
        def force(key):
            error=float(np.linalg.norm(a[key][i]-b[key][i]));norm=float(np.linalg.norm(b[key][i]));return {'reference_norm_N':norm,'error_N':error,'relative_or_floor_scaled_error':error/max(norm,1e-6)}
        rows.append({'sim_s':float(t),'position_max_error_m':float(np.linalg.norm(a['x'][i]-b['x'][i],axis=1).max()),'velocity_max_error_m_s':float(np.linalg.norm(a['v'][i]-b['v'][i],axis=1).max()),'material_force':force('f'),'support_reaction':force('reaction')})
    return {'max_position_error_m':max(r['position_max_error_m'] for r in rows),'max_velocity_error_m_s':max(r['velocity_max_error_m_s'] for r in rows),'max_material_force_relative_or_floor_error':max(r['material_force']['relative_or_floor_scaled_error'] for r in rows),'max_support_reaction_relative_or_floor_error':max(r['support_reaction']['relative_or_floor_scaled_error'] for r in rows),'rows':rows}
ref=compare('reference','refined');ref['passed']=bool(ref['max_position_error_m']<=1e-5 and ref['max_material_force_relative_or_floor_error']<=.01 and ref['max_support_reaction_relative_or_floor_error']<=.01)
out={'scope':'Section 2 numerical qualification only; forward intact bulk, no robot/blade/fracture/autograd qualification','reference_refinement':ref,'candidates':{}}
for name in ['candidate','candidate_fused']:
    if not (W/f'{name}_result.json').exists():continue
    c=compare(name,'refined');r=json.loads((W/f'{name}_result.json').read_text());c['accuracy_passed']=bool(ref['passed'] and r['stable'] and c['max_position_error_m']<=.0001 and c['max_velocity_error_m_s']<=.005 and c['max_material_force_relative_or_floor_error']<=.05 and c['max_support_reaction_relative_or_floor_error']<=.05 and r['pcg_max_relative_residual']<=1e-9);c['wall_s_per_sim_s']=r['stepping_and_sampling_wall_s_per_sim_s'];c['practical_short_bulk_cost_passed']=bool(c['wall_s_per_sim_s']<=120);c['full_numeric_and_cost_passed']=c['accuracy_passed'] and c['practical_short_bulk_cost_passed'];out['candidates'][name]=c
if 'candidate_fused' in out['candidates']:
    eq=compare('candidate_fused','candidate');eq['passed']=eq['max_position_error_m']<=1e-10 and eq['max_velocity_error_m_s']<=1e-8;out['fused_vs_adaptive_equivalence']=eq
out['component_checks']={name:json.loads((W/f'{name}_result.json').read_text())['passed'] for name in ['controls','implicit_control','graph_control','gather_control','fused_control'] if (W/f'{name}_result.json').exists()}
out['accepted_for_next_settling_check']=bool(all(out['component_checks'].values()) and out['candidates'].get('candidate_fused',{}).get('full_numeric_and_cost_passed',False) and out.get('fused_vs_adaptive_equivalence',{}).get('passed',False))
(W/'comparison_result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['candidates','reference_refinement','fused_vs_adaptive_equivalence']},indent=2))
for k,c in out['candidates'].items():print(k,json.dumps({a:v for a,v in c.items() if a!='rows'}))
