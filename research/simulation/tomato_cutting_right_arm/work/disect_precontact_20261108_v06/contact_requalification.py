from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'backend'))
from numerics import tensor,load_arrays
from contact_numerics import ContactBulk
sys.path.insert(0,str(W))
from contact_control import small
# With damping=0 and zero elastic force at rest, each contacted tangential DOF
# has the independent closed-form regularized Coulomb backward-Euler solution.
z={k:np.copy(v) if isinstance(v,np.ndarray) else v for k,v in small.items()};z['tet_mu'][:]=0;z['tet_lambda'][:]=1;z['tet_damping'][:]=0;z['gravity'][:]=0
b=ContactBulk(z);velocity=np.zeros_like(z['x']);velocity[1]=[.002,0,-.002];b.v.copy_(tensor(velocity));h=7.462686567164179e-6;info=b.implicit(h);q,v=b.arrays();fn=1000*max(.001-z['x'][1,1],0);limit=.2*fn;mass=z['physical_mass'][1];star=abs(velocity[1,0]);expected=max(star/(1+h*1000/mass),star-h*limit/mass);error=max(abs(v[1,0]-expected),abs(v[1,2]+expected));b.reset();reset=all(bool((getattr(b,n)==0).all().item()) for n in ['v','guess','last_friction','last_normal','last_force'])
a=np.load(W/'contact_segment_trajectory.npz');r=np.load(W/'contact_segment_refined_trajectory.npz');ar=json.loads((W/'contact_segment_result.json').read_text());rr=json.loads((W/'contact_segment_refined_result.json').read_text());assert np.array_equal(a['t'],r['t'])
pe=float(np.linalg.norm(a['x']-r['x'],axis=2).max());ve=float(np.linalg.norm(a['v']-r['v'],axis=2).max());fe=max(float(np.linalg.norm(aa-bb)/max(np.linalg.norm(bb),1e-6)) for aa,bb in zip(a['f'],r['f']));re=max(float(np.linalg.norm(aa-bb)/max(np.linalg.norm(bb),1e-6)) for aa,bb in zip(a['reaction'],r['reaction']));passed=bool(json.loads((W/'contact_control_result.json').read_text())['passed'] and ar['admissible'] and rr['admissible'] and error<1e-8 and reset and pe<=1e-4 and ve<=.005 and fe<=.05 and re<=.05)
out={'scope':'Independent analytic friction plus 10ms fullmesh continuation/refinement; permission for fresh bounded hold only','analytic_tangential_velocity_m_s':expected,'analytic_velocity_error_m_s':float(error),'reset_cleared_all_added_force_diagnostics':reset,'position_max_error_m':pe,'velocity_max_error_m_s':ve,'material_force_max_relative_or_floor_error':fe,'support_reaction_max_relative_or_floor_error':re,'segment_initial_max_speed_m_s':ar['rows'][0]['maximum_speed_m_s'],'segment_final_max_speed_m_s':ar['rows'][-1]['maximum_speed_m_s'],'refined_segment_final_max_speed_m_s':rr['rows'][-1]['maximum_speed_m_s'],'maximum_coupled_residual':max(ar['max_residual'],rr['max_residual']),'fresh_hold_authorized_by_checks':passed,'fresh_settling_passed':False}
(W/'contact_requalification_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert passed
