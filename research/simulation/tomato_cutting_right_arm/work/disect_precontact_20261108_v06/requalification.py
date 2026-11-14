from pathlib import Path
import json,sys,numpy as np
W=Path(__file__).resolve().parent;B=W/'backend';sys.path.insert(0,str(B))
from analyze import compare
r=compare('reference','refined');c=compare('candidate_refined','refined');result=json.loads((B/'candidate_refined_result.json').read_text());checks={name:json.loads((path).read_text())['passed'] for name,path in [('rotation',W/'corrected_preflight_result.json'),('energy',W/'energy_control_result.json'),('numerics',B/'controls_result.json'),('dense_implicit',B/'implicit_control_result.json')]}
refok=r['max_position_error_m']<=1e-5 and r['max_material_force_relative_or_floor_error']<=.01 and r['max_support_reaction_relative_or_floor_error']<=.01
ok=all(checks.values()) and refok and result['stable'] and c['max_position_error_m']<=1e-4 and c['max_velocity_error_m_s']<=.005 and c['max_material_force_relative_or_floor_error']<=.05 and c['max_support_reaction_relative_or_floor_error']<=.05 and result['pcg_max_relative_residual']<=1e-9
out={'scope':'Approved corrected material law: short-interval requalification for slow section3 stability investigation only; cost gate remains failed','component_checks':checks,'reference_refinement_passed':bool(refok),'candidate':{k:v for k,v in c.items() if k!='rows'},'selected_dt_s':result['dt_s'],'observed_wall_s_per_sim_s':result['stepping_and_sampling_wall_s_per_sim_s'],'accepted_for_bounded_settling_only':bool(ok),'speed_gate_passed':False};(W/'requalification_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert ok
