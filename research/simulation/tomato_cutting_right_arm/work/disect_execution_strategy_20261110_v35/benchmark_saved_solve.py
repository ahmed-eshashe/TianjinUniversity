from pathlib import Path
import sys,json,time,hashlib,numpy as np,numba
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;R=W.parents[1];V=W.parent/'disect_bevel_reference_20261109_v33';sys.path.insert(0,str(W.parent/'disect_contact_linesearch_20261109_v32'))
from stable_blade import StableBlade,s,m,torch,tensor
import tomato_compiled_blade_query as query_module
from fast_cad_query import fast_query
sys.path.insert(0,str(W.parent/'disect_section4_completion_20261109_v29'))
from volume_guard_limit_resolution import WholeVolumeGuard
assert json.loads((W/'query_benchmark_result.json').read_text())['passed'] and json.loads((W/'fast_geometry_controls_result.json').read_text())['passed'];numba.set_num_threads(4);original=query_module._query;source=V/'centered0080_resume_final.npz';sha=hashlib.sha256(source.read_bytes()).hexdigest();z=np.load(source);t0=float(z['step']*z['dt']);h=float(z['dt']);plan=json.loads((V/'correction_plan.json').read_text());curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T)
def pose(t):
 u=t/plan['durations_s'][0];r=10*u**3-15*u**4+6*u**5;dr=30*u*u-60*u**3+30*u**4;d=plan['downward_stroke_m']*r;speed=plan['downward_stroke_m']*dr/plan['durations_s'][0]
 return np.array(plan['selected']['translation_m'])+[float(curve(d)),-d,0],np.array([float(curve.derivative()(d))*speed,-speed,0])
(W/'solve_benchmark_contract.json').write_text(json.dumps({'scope':'One existing physical model, h and state; only query implementation changes. One warm and three measured uncommitted solve trials, two cold full-volume queries; no accepted step, damage commit or new physical sampling adoption. Coverage candidate remains separate.','source':str(source),'sha256':sha,'wall_cap_s':120,'max_solve_trials':4,'comparison_limits':{'position_m':1e-10,'velocity_m_s':1e-7,'actual_force_N':1e-8,'moment_Nm':1e-8,'true_solver_residual':1e-9}},indent=2)+'\n')
start=time.perf_counter();b=StableBlade();b.blade_enabled=True;mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'));base=b.mask.clone()
def solve(query):
 query_module._query=query;b.x.copy_(tensor(z['x']));b.v.copy_(tensor(z['v']));b.fracture.load_state_dict({'history':z['history']});b.eligibility_override=None;b.blade_translation,b.blade_velocity=pose(t0);world=b.x@tensor(mapping['rotation']).T+tensor(mapping['translation']);H=tensor(mapping['halfspaces']);b.mask=base*torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1);oldq=b.x.clone();oldv=b.v.clone();torch.cuda.synchronize();tic=time.perf_counter()
 for coupling in range(4):
  info=b.implicit(h);actual=b.blade_sample['force']+b.last_blade_dashpot.cpu().numpy();eligible=s.eligibility_from_contact(actual)
  if np.array_equal(eligible,b.eligibility):break
  b.x.copy_(oldq);b.v.copy_(oldv);b.eligibility_override=eligible
 else:raise RuntimeError('Eligibility failed')
 torch.cuda.synchronize();wall=time.perf_counter()-tic;q,v=b.arrays();com=b.cad.com_local@b.cad.rotation.T+b.blade_translation;moment=-np.cross(z['x']-com,actual).sum(0);assert np.array_equal(z['history'],b.fracture.state_dict()['history']);assert max(info['relative_residual'],info['inner_max_residual'])<=1e-9
 return {'wall_s':wall,'solver':info,'coupling_rounds':coupling+1},(q,v,actual,moment)
solve(original);fast_query(b.cad.vertices@b.cad.rotation.T+z['blade_translation'],b.cad.triangles,z['x'][:16]);reference,arrays=solve(original);optimized=[]
for repetition in range(2):
 info,values=solve(fast_query);diff={k:float(np.max(abs(a-v))) for k,a,v in zip(['position_m','velocity_m_s','actual_force_N','moment_Nm'],arrays,values)};assert diff['position_m']<1e-10 and diff['velocity_m_s']<1e-7 and diff['actual_force_N']<1e-8 and diff['moment_Nm']<1e-8;optimized.append(dict(**info,differences=diff));assert time.perf_counter()-start<120
T,_=pose(t0+h);guards=[]
for name,query in [('reference',original),('candidate',fast_query)]:
 query_module._query=query;guard=WholeVolumeGuard(b.cad,m['tets']);tic=time.perf_counter();proof=guard.check(arrays[0],T);elapsed=time.perf_counter()-tic;assert proof['passed'];guards.append({'name':name,'wall_s':elapsed,'passed':proof['passed'],'attempts':guard.records})
query_module._query=original;assert hashlib.sha256(source.read_bytes()).hexdigest()==sha;assert np.array_equal(z['history'],b.fracture.state_dict()['history'])
out={'scope':'Same old physical operator and saved state, changed CPU query implementation only; no accepted physical advance or history commit. Local equivalence and cost result only; new edge-coverage candidate still needs fresh coupled/half-step qualification.','passed':True,'reference':reference,'candidate_repetitions':optimized,'saved_solve_speedup':reference['wall_s']/np.mean([r['wall_s'] for r in optimized]),'cold_volume_guards':guards,'cold_volume_guard_speedup':guards[0]['wall_s']/guards[1]['wall_s'],'history_and_source_checkpoint_unchanged':True,'wall_s':time.perf_counter()-start,'backend_candidate_not_yet_adopted':True,'full_trajectory_comparison_pending':True};(W/'saved_solve_benchmark_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='cold_volume_guards'},indent=2))
