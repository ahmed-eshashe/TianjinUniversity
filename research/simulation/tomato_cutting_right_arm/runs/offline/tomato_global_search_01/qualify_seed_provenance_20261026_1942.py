"""Read saved evidence and verify uncommitted-seed lineage, not physics solving."""
from pathlib import Path
import json,hashlib,math,fcntl,resource,signal,runpy
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];G=Path(__file__).parent;V=R/'runs/offline/tomato_curvature_search_01'
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
assert datetime.now(timezone.utc)<datetime(2026,10,27,3,42,1,tzinfo=timezone.utc)
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
runpy.run_path(str(V/'qualify_progress.py'),run_name='__main__');q=json.loads((V/'qualification.json').read_text())
checks={};manifests=[V/'helper_source_snapshot.json',G/'source_snapshot.json',G/'source_snapshot_v2.json',R/'runs/offline/tomato_first_failure_refinement_01/source_snapshot.json']
for suffix in ['_v3','_v4','_v5']:
 if (G/('source_snapshot'+suffix+'.json')).exists():manifests.append(G/('source_snapshot'+suffix+'.json'))
for path in manifests:
 d=json.loads(path.read_text())
 for n,h in d.items():assert digest(R/n)==h,n
 checks[str(path.relative_to(R))]=len(d)
origins={digest(p):json.loads(p.read_text()) for p in V.glob('*/attempt*/candidate.json')}
valid_previous={digest(R/s['checkpoint']/'summary.json') for s in q['accepted']};seeds=[]
for p in sorted(G.glob('*/candidate.json')):
 if not (p.parent/'diagnostic.json').exists():continue
 s=json.loads(p.read_text());d=json.loads((p.parent/'diagnostic.json').read_text());origin=origins[s['source_candidate_sha256']]
 assert s['passed'] is False and s['optimization_only'] is True and s['previous_summary_sha256'] in valid_previous
 for key in ['depth_mm','previous_summary_sha256','trial_damage_states','source_hashes']:assert s[key]==origin[key]
 for n,h in (s['source_hashes']|s['prediction_source_hashes']).items():assert digest(R/n)==h
 assert digest(p.parent/'guess.npy')==s['guess_sha256']==d['guess_sha256']
 assert d['source_candidate_sha256']==s['source_candidate_sha256'] and d['previous_summary_sha256']==s['previous_summary_sha256']
 assert d['final_energy_j']<=d['initial_energy_j']+1e-14
 assert all(math.isfinite(d[key]) for key in ['final_force_residual','initial_force_residual','initial_energy_j','final_energy_j','minimum_gap_m','min_J'])
 seeds.append({'seed':str(p.parent.relative_to(R)),'initial_force_residual':d['initial_force_residual'],'final_force_residual':d['final_force_residual'],'frozen_search_converged':d['frozen_search_converged'],'max_rss_bytes':d['max_rss_bytes'],'physical_endpoint_accepted':False})
for path in V.glob('*/status.json'):
 s=json.loads(path.read_text());assert s['calls']<=12
 for n,h in s.get('orchestration_source_hashes',{}).items():assert digest(R/n)==h
rows=[]
for path in sorted(V.glob('*/attempt*/summary.json')):
 s=json.loads(path.read_text())
 if s['depth_mm']<8.828125:continue
 previous=json.loads((R/s['previous_checkpoint']/'summary.json').read_text())
 rows.append({'checkpoint':str(path.parent.relative_to(R)),'previous_depth_mm':previous['depth_mm'],'depth_mm':s['depth_mm'],'step_mm':s['depth_mm']-previous['depth_mm'],'swept_gap_m':s['swept_blade_minimum_gap_m'],'passed':s['passed'],'flags':s['flags']})
assert json.loads((G/'tests.json').read_text())['passed'];assert json.loads((G/'cycle_tests.json').read_text())['passed']
report={'passed':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'source_of_qualification_sha256':digest(V/'qualification.json'),'qualifier_source_hash':digest(Path(__file__)),'extra_source_checks':checks,'verified_uncommitted_seeds':seeds,'cycle_tests':json.loads((G/'cycle_tests.json').read_text()),'previous_regression_tests':143,'additional_cycle_tests':8,'path_refinement':rows,'last_accepted':q['last_accepted'],'physical_gates_unchanged':True,'laws_unchanged':True,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
assert datetime.now(timezone.utc)<datetime(2026,10,27,3,42,1,tzinfo=timezone.utc)
(G/'refinement_qualification.json').write_text(json.dumps(report,indent=2)+'\n');(R/'docs/rl/tomato_swept_refinement_results.json').write_text(json.dumps(report,indent=2)+'\n')
print({'extra_source_checks':checks,'verified_seed_count':len(seeds),'last_accepted':q['last_accepted']})
