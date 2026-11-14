from pathlib import Path
import json,hashlib,datetime,numpy as np
W=Path(__file__).resolve().parents[1];run=W/'runs'
import sys;sys.path.insert(0,str(W/'src'))
from compiled_body import Body
b=Body(n=2,h=.003)
def compare(A,B):
 a=json.loads((run/A/'result.json').read_text());c=json.loads((run/B/'result.json').read_text());sa=np.load(run/A/'trajectory.npz');sc=np.load(run/B/'trajectory.npz');fa=np.array([r['reaction'] for r in a['rows']]);fc=np.array([r['reaction'] for r in c['rows']]);fe=np.linalg.norm(fa-fc,axis=1)/np.maximum(np.linalg.norm(fc,axis=1),1e-4)
 dx=sa['q']-sc['q'];dv=sa['v']-sc['v'];local=np.linalg.norm(dv[:,b.ids],axis=3).max(axis=2);vrms=np.sqrt(np.sum(local**2*b.V,axis=1)/sum(b.V))
 def rel(key, floor):
  aa=np.array([r[key] for r in a['rows']]);cc=np.array([r[key] for r in c['rows']]);return float(np.max(np.linalg.norm(aa-cc,axis=1)/np.maximum(np.linalg.norm(cc,axis=1),floor))) if aa.ndim>1 else float(np.max(abs(aa-cc)/np.maximum(abs(cc),floor)))
 metrics={'position_m':float(np.linalg.norm(dx,axis=2).max()),'velocity_material_weighted_upper_RMS_m_s':float(vrms.max()),'velocity_max_pointwise_m_s':float(np.linalg.norm(dv,axis=2).max()),'force_relative_max':float(fe.max()),'force_absolute_max_N':float(np.linalg.norm(fa-fc,axis=1).max()),'impulse_relative_max':rel('material_impulse',1e-7),'tool_work_relative_max':rel('tool_work_J',1e-8),'friction_work_relative_max':rel('friction_J',1e-8)}
 checks={'positions':metrics['position_m']<=1e-4,'velocity':metrics['velocity_material_weighted_upper_RMS_m_s']<=.005,'force':metrics['force_relative_max']<=.05,'impulse':metrics['impulse_relative_max']<=.05,'tool_work':metrics['tool_work_relative_max']<=.05,'friction_work':metrics['friction_work_relative_max']<=.05}
 return {'a':A,'b':B,'metrics':metrics,'checks':checks,'passed':all(checks.values()),'worst_force_time_s':a['rows'][int(fe.argmax())]['t'],'worst_force_A_N':fa[int(fe.argmax())].tolist(),'worst_force_B_N':fc[int(fe.argmax())].tolist()}
comparisons={'coarse_time':compare('precise_edge_d1_s500','precise_edge_half_d1_s500'),'refined_time':compare('parallel_edge_d2_s125','parallel_edge_d4_s125'),'spatial_125_62':compare('parallel_edge_d4_s125','parallel_edge_d4_s62'),'spatial_62_31':compare('culled_edge_d4_s62','culled_edge_d4_s31'),'broadphase_equivalence':compare('parallel_edge_d4_s62','culled_edge_d4_s62'),'final_profile_equivalence':compare('culled_edge_d4_s62','profile_edge_d4_s62')}
(W/'comparisons.json').write_text(json.dumps(comparisons,indent=2))
pre=json.loads((W/'preflight_precise.json').read_text());mech=json.loads((W/'mechanics_controls_precise.json').read_text());prof=json.loads((run/'profile_edge_d4_s62/result.json').read_text());checks={**{'geometry_'+k:v for k,v in pre['checks'].items()},**mech['checks']}
assert all(checks.values()),[k for k,v in checks.items() if not v]
assert comparisons['broadphase_equivalence']['passed']
assert comparisons['final_profile_equivalence']['passed']
assert comparisons['refined_time']['passed'],comparisons['refined_time']
protected=json.loads((W/'manifest.json').read_text())['protected'];changed=[]
for name,expected in protected.items():
 p=Path(name)
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:changed.append(name)
assert not changed,changed
preservation={'checked':len(protected),'changed':changed,'all_unchanged':not changed};(W/'preservation.json').write_text(json.dumps(preservation,indent=2))
now=datetime.datetime.now().astimezone().isoformat()
qualified={'updated':now,'decision':'contact_operator_components_pass_spatial_force_refinement_fails_no_physical_cut_or_RL_qualification','component_checks_passed':len(checks),'component_checks':checks,'comparisons':comparisons,'scope':'6 mm intact supported cube, 48 affine tetrahedra, h=3 mm, actual saved CAD. v22 material and v02 contact/work laws. This is neither a tomato nor a fracture trajectory.','physics_laws_changed':False,'material_constants_changed':False,'accuracy_limits_changed':False,'production_timestep_changed':False,'diagnostic_timesteps_s':[12.5e-6,6.25e-6,3.125e-6],'separation_enabled':False,'physical_cut':False,'physical_tomato_model_completed':False,'rl_ready':False,'actual_RL_speed_qualified':False,'experimental_validation':'pending','current_setup_changed':False,'simulation_running':False,'performance':{'scope':'one 13 ms contact-only coupon cycle including checks/output; not complete RL steps','selected_profile_wall_s':prof['wall_s'],'simulated_s':.013,'wall_seconds_per_sim_second':prof['wall_s']/.013,'categories_s':{k:sum(r['cost'][k] for r in prof['rows']) for k in prof['rows'][0]['cost']},'tracked_GPU_bytes':prof['tracked_device_bytes'],'peak_process_RSS_KiB':prof['peak_process_RSS_KiB'],'reference_no_broadphase_wall_s':json.loads((run/'parallel_edge_d4_s62/result.json').read_text())['wall_s'],'matched_broadphase_wall_s':json.loads((run/'culled_edge_d4_s62/result.json').read_text())['wall_s']},'preservation':preservation}
(W/'qualification.json').write_text(json.dumps(qualified,indent=2));(W/'status.json').write_text(json.dumps({k:v for k,v in qualified.items() if k not in ['component_checks','comparisons']},indent=2))
print(json.dumps({'checked':len(protected),'components':len(checks),'temporal':comparisons['refined_time']['metrics'],'spatial':comparisons['spatial_62_31']['metrics'],'performance':qualified['performance']},indent=2))
