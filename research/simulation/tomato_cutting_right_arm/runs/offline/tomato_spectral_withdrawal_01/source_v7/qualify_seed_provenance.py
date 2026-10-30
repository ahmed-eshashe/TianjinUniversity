"""Saved seed provenance only; no mechanical solve or state acceptance."""
import json,hashlib,math,resource,signal,fcntl
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
lease=json.loads((R/'runs/offline/tomato_triangle_withdrawal_01/quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480 and lease['maximum_reported_used_percent']<45
handles=[]
for n in ['logs/offline_overnight.lock','logs/right_arm_control.lock']:
 h=(R/n).open('a');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);handles.append(h)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for manifest in F.glob('*source_snapshot*.json'):
 for n,h in json.loads(manifest.read_text()).items():assert digest(R/n)==h,n
q=json.loads((F/'qualification.json').read_text());assert q['passed'];valid={s['summary_sha256'] for s in q['accepted']}
rows=[]
for p in F.glob('*/candidate.json'):
 if not (p.parent/'diagnostic.json').exists():continue
 s=json.loads(p.read_text());d=json.loads((p.parent/'diagnostic.json').read_text())
 assert s['optimization_only'] and not s['passed'] and s['physical_endpoint_accepted'] is False
 assert s['damage_modified'] is False and s['work_modified'] is False and s['physical_trajectory_advanced'] is False
 origin=R/s['source_candidate_checkpoint'];o=json.loads((origin/'candidate.json').read_text())
 assert digest(origin/'candidate.json')==s['source_candidate_sha256']==d['source_candidate_sha256']
 assert not o['passed'] and o['optimization_only']
 for k in ['source_hashes','depth_mm','previous_summary_sha256','trial_damage_states']:assert o[k]==s[k]
 assert s['previous_summary_sha256'] in valid and d['previous_summary_sha256']==s['previous_summary_sha256']
 prevs=[r for r in q['accepted'] if r['summary_sha256']==s['previous_summary_sha256']];assert len(prevs)==1
 prev=R/prevs[0]['checkpoint'];old=json.loads((prev/'summary.json').read_text())
 assert digest(prev/'summary.json')==s['previous_summary_sha256'] and old['backend']=='triangle_spectral_withdrawal_v1'
 assert old['damage_states']==s['trial_damage_states'] and old['source_hashes']==s['source_hashes']
 assert -.031250000001<=s['depth_mm']-old['depth_mm']<0
 for n,h in old['state_hashes'].items():assert digest(prev/n)==h
 for n,h in (s['source_hashes']|s['prediction_source_hashes']).items():assert digest(R/n)==h
 for n,h in d['source_hashes'].items():assert digest(R/n)==h
 assert digest(p.parent/'guess.npy')==s['guess_sha256']==d['guess_sha256']
 assert d['final_energy_j']<=d['initial_energy_j']+1e-14
 assert all(math.isfinite(d[k]) for k in ['initial_force_residual','final_force_residual','initial_energy_j','final_energy_j','minimum_gap_m','min_J'])
 rows.append({'seed':str(p.parent.relative_to(R)),'source_candidate':s['source_candidate_checkpoint'],'previous_checkpoint':str(prev.relative_to(R)),'depth_mm':s['depth_mm'],'initial_force_residual':d['initial_force_residual'],'final_force_residual':d['final_force_residual'],'frozen_search_converged':d['frozen_search_converged'],'energy_decreased':True,'physical_endpoint_accepted':False,'runtime_s':d['runtime_s'],'max_rss_bytes':d['max_rss_bytes']})
assert rows
report={'passed':True,'seeds':rows,'physical_qualification_sha256':digest(F/'qualification.json'),'qualifier_sha256':digest(Path(__file__)),'states_or_work_or_damage_changed':False,'simulator':False,'training':False}
(F/'seed_qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
