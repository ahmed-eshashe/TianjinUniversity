"""Copy only an uncommitted numerical guess; never transfer physical history."""
import json,hashlib,shutil,fcntl,resource,signal
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
dpath=F/'frozen_candidate_diagnostic30.json';d=json.loads(dpath.read_text());assert d['optimization_only'] and not d['physical_endpoint_accepted'] and d['frozen_trial_damage_only']
source=R/d['source_candidate'];s=json.loads((source/'candidate.json').read_text());assert s['optimization_only'] and not s['passed'] and s['depth_mm']==d['depth_mm']
assert digest(source/'candidate.json')==d['source_candidate_sha256'];assert digest(F/'diagnostic_guess30.npy')==d['diagnostic_guess_sha256']
for n,h in d['source_hashes'].items():assert digest(R/n)==h
previous=R/'runs/offline/tomato_curvature_search_01/insertion04_predicted/attempt008';old=json.loads((previous/'summary.json').read_text());audit=json.loads((previous.parent/(previous.name+'_audit.json')).read_text());assert old['passed'] and audit['passed']
assert digest(previous/'summary.json')==s['previous_summary_sha256']==d['previous_summary_sha256']
assert old['source_hashes']==s['source_hashes']
for n,h in old['state_hashes'].items():assert digest(previous/n)==h
out=F/'global_seed';out.mkdir(exist_ok=False);shutil.copyfile(F/'diagnostic_guess30.npy',out/'guess.npy')
report={'passed':False,'optimization_only':True,'reason':'global_search_positions_only_numerical_guess','depth_mm':s['depth_mm'],'previous_summary_sha256':s['previous_summary_sha256'],'guess_sha256':digest(out/'guess.npy'),'trial_damage_states':s['trial_damage_states'],'optimizer_active_rows':d['trace'][-1]['optimizer_active_rows'],'source_hashes':s['source_hashes'],'prediction_source_hashes':{**{n:h for n,h in d['source_hashes'].items() if n not in s['source_hashes']},str(Path(__file__).relative_to(R)):digest(Path(__file__))},'original_candidate_sha256':digest(source/'candidate.json'),'frozen_diagnostic_sha256':digest(dpath),'uncommitted_trial_damage_only':True,'frozen_force_residual':d['final_force_residual'],'frozen_search_converged':d['frozen_search_converged'],'physical_endpoint_accepted':False,'damage_modified':False,'work_modified':False,'physical_trajectory_advanced':False,'simulator':False,'training':False}
(out/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print('Uncommitted seed prepared; coupled consistency and all physical audits still required')
