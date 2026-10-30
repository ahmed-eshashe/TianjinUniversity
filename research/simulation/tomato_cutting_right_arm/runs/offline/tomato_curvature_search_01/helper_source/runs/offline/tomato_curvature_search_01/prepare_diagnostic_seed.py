"""Transfer an uncommitted guess across an exactly verified hold transition."""
import json,hashlib,shutil,fcntl,resource,signal
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((F/'frozen_candidate_diagnostic.json').read_text());assert d['optimization_only'] and not d['physical_endpoint_accepted'] and d['frozen_trial_damage_only']
source=R/d['source_candidate'];s=json.loads((source/'candidate.json').read_text());assert s['optimization_only'] and not s['passed']
assert digest(source/'candidate.json')==d['source_candidate_sha256'];assert digest(F/'diagnostic_guess.npy')==d['diagnostic_guess_sha256']
for n,h in d['source_hashes'].items():assert digest(R/n)==h
hold=F/'transition_hold/attempt001';h=json.loads((hold/'summary.json').read_text());audit=json.loads((hold.parent/(hold.name+'_audit.json')).read_text());assert h['passed'] and audit['passed']
previous=R/h['previous_checkpoint'];old=json.loads((previous/'summary.json').read_text());assert digest(previous/'summary.json')==s['previous_summary_sha256']==h['previous_summary_sha256']
for key in ['depth_mm','energy_j','fracture_dissipation_j','damage_states','cumulative_blade_work_j']:assert h[key]==old[key],('Hold was not exactly identical',key)
for n in ['positions.npy','edge_hits.npy']:assert h['state_hashes'][n]==old['state_hashes'][n]
# Normal reactions were independently recomputed; they are NOT copied into
# the seed or used as committed next-step forces. The new hold is the ledger predecessor.
for n,sha in h['source_hashes'].items():assert digest(R/n)==sha
assert all(h['source_hashes'].get(n)==sha for n,sha in s['source_hashes'].items())
out=F/'adapted_seed';out.mkdir(exist_ok=False);shutil.copyfile(F/'diagnostic_guess.npy',out/'guess.npy')
report={'passed':False,'optimization_only':True,'reason':'verified_identical_hold_diagnostic_seed','depth_mm':s['depth_mm'],'previous_summary_sha256':digest(hold/'summary.json'),'guess_sha256':digest(out/'guess.npy'),'trial_damage_states':s['trial_damage_states'],'optimizer_active_rows':d['trace'][-1]['optimizer_active_rows'],'source_hashes':h['source_hashes'],'prediction_source_hashes':{str(Path(__file__).relative_to(R)):digest(Path(__file__))},'original_candidate_sha256':digest(source/'candidate.json'),'frozen_diagnostic_sha256':digest(F/'frozen_candidate_diagnostic.json'),'previous_positions_edge_history_damage_energy_work_exactly_identical':True,'multipliers_recomputed_and_independently_audited':True,'blade_resistance_difference_n':h['blade_resistance_n']-old['blade_resistance_n'],'uncommitted_trial_damage_only':True,'damage_predicted':False,'work_modified':False,'physical_trajectory_advanced':False,'simulator':False,'training':False}
(out/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared uncommitted numerical seed only')
