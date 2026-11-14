"""Read-only physical evidence review. Never promotes a loading prefix to Gate B."""
from pathlib import Path
import argparse,datetime,hashlib,json,numpy as np
W=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();name=a.name
r=json.loads((W/f'{name}_result.json').read_text());z=np.load(W/f'{name}_trajectory.npz');f=np.load(W/f'{name}_final.npz');i=np.load(W/f'{name}_initial.npz');contract=json.loads((W/'execution_contract.json').read_text());rows=r['rows']
assert len(rows)==len(z['t'])==len(z['history'])
assert np.allclose(z['t'],[row['sim_s'] for row in rows],atol=1e-12,rtol=0)
assert abs(float(f['step'])*float(f['dt'])-r['duration_s'])<1e-12
assert all(np.isfinite(z[k]).all() for k in ['x','v','history','reaction','moment'])
assert np.array_equal(f['x'],z['x'][-1]) and np.array_equal(f['v'],z['v'][-1]) and np.array_equal(f['history'],z['history'][-1])
h=z['history'];no_healing=bool(np.all(np.diff(h,axis=0)>=-1e-12));assert no_healing
frozen=all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in contract['sources'].items());assert frozen
source=np.load(contract['source_initial_state']);fresh=bool(int(i['step'])==0 and np.array_equal(i['x'],source['x']) and np.array_equal(i['v'],source['v']) and np.max(i['history'])==0) if r['start_step']==0 else None
if r['start_step']==0:assert fresh
cert=json.loads((W/f'{name}_whole_volume_certificates.json').read_text());times=z['t'];walls=np.array([row['wall_s'] for row in rows]);lo=max(0,len(rows)-11);recent_sim=times[-1]-times[lo];recent_wall=walls[-1]-walls[lo];cost=float(recent_wall/recent_sim) if recent_sim>0 else None
out={'scope':'Bounded damage-enabled loading prefix, not controlled withdrawal or a Gate B pass','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stop':r['stop'],'last_accepted_time_s':r['duration_s'],'requested_horizon_s':r['window_until_s'],'all_accepted_sample_guards_passed':all(row['admissible'] for row in rows),'fresh_initial_identity':fresh,'frozen_sources_unchanged':frozen,'checkpoint_trajectory_identity':True,'history_no_healing':no_healing,'maximum_damage':float(h[:,:,1].max()),'maximum_opening_m':float(h[:,:,0].max()),'maximum_fracture_dissipation_J':max(row['fracture_dissipation_J'] for row in rows),'peak_sum_force_N':max(row['sum_force_N'] for row in rows),'maximum_sampled_penetration_m':max(row['CAD_penetration_m'] for row in rows),'minimum_volume_ratio':min(row['minimum_volume_ratio'] for row in rows),'mass_kg':r['mass_kg'],'mass_matches_frozen_reference':abs(r['mass_kg']-.1216712654796547)<1e-14,'initial_clearance_certified':bool(cert['initial_clearance']['passed']) if cert['initial_clearance'] else None,'certificate_attempt_count':len(cert['records']),'certificate_failed_attempts_not_necessarily_physical_failures':sum(not v['passed'] for v in cert['records']),'original_whole_volume_guard_limit_m':.0001,'wall_s':r['wall_s'],'peak_RSS_KiB':r['peak_RSS_KiB'],'recent_window_sim_s':float(recent_sim),'recent_window_wall_s':float(recent_wall),'recent_wall_s_per_sim_s':cost,'estimated_next_5ms_wall_s':None if cost is None else cost*.005,'independent_damage_refinement_pending':True,'controlled_withdrawal_pending':True,'gate_b_passed':False,'separation_qualified':False,'speed':'deferred, not passed','experimental_validation':'pending'}
(W/f'{name}_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
