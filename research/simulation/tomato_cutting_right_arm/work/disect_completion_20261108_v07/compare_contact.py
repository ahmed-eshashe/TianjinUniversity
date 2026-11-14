from pathlib import Path
import numpy as np,json
O=Path(__file__).resolve().parent;W=O.parent/'disect_precontact_20261108_v06'
a=json.loads((W/'indent_refined_result.json').read_text());b=json.loads((O/'indent_quarter_result.json').read_text());x=np.load(W/'indent_refined_trajectory.npz');y=np.load(O/'indent_quarter_trajectory.npz');assert np.array_equal(x['t'],y['t'])
err=lambda key,floor:np.linalg.norm(x[key]-y[key],axis=1)/np.maximum(np.linalg.norm(y[key],axis=1),floor)
f=err('reaction',1e-6);m=err('moment',1e-8);p=float(np.linalg.norm(x['x']-y['x'],axis=2).max());v=float(np.linalg.norm(x['v']-y['v'],axis=2).max())
out=dict(scope='Intact original-CAD contact at half/quarter original timestep; unchanged law and tolerances',position_max_error_m=p,velocity_max_error_m_s=v,force_max_relative_error=float(f.max()),moment_max_relative_error=float(m.max()),force_worst_time_s=float(x['t'][f.argmax()]),both_component_pass=bool(a['component_passed'] and b['component_passed']),quarter_wall_s_per_sim_s=b['wall_s']/b['duration_s'],runtime_budget_wall_s_per_sim_s=120)
out['contact_comparison_passed']=bool(out['both_component_pass'] and p<=1e-4 and v<=.005 and f.max()<=.05 and m.max()<=.05);out['runtime_passed']=out['quarter_wall_s_per_sim_s']<=120
(O/'contact_comparison_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
