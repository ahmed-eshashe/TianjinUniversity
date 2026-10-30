"""Capped saved-evidence qualification, no mechanics solve or state repair."""
import json,hashlib,resource,signal,fcntl,math
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
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for x in v.values():finite(x)
 elif isinstance(v,list):
  for x in v:finite(x)
for folder in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01','tomato_optimizer_release_01','tomato_curvature_search_01','tomato_global_search_01','tomato_first_failure_refinement_01','tomato_cubic_path_diagnostic_01','tomato_spectral_withdrawal_01']:
 paths=list((R/'runs/offline'/folder).glob('*source_snapshot*.json'))
 if folder in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01']:paths.append(R/'runs/offline'/folder/'baseline_hashes.json')
 for path in paths:
  for n,h in json.loads(path.read_text()).items():assert digest(R/n)==h,n
anchor_path=R/'runs/offline/tomato_curvature_search_01/insertion26_small_global/attempt004';anchor=json.loads((anchor_path/'summary.json').read_text())
for base,mapping in [(R,anchor['source_hashes']),(anchor_path,anchor['state_hashes'])]:
 for n,h in mapping.items():assert digest(base/n)==h,n
assert anchor['passed'];assert json.loads((anchor_path.parent/(anchor_path.name+'_audit.json')).read_text())['passed']
rows=[];failed=[]
for p in sorted(F.glob('*/status.json')):
 status=json.loads(p.read_text());finite(status);assert status['calls']<=12
 for n,h in status['source_hashes'].items():assert digest(R/n)==h
 if not status['accepted']:
  evidence=[]
  for row in status['records']:
   cp=R/row['output']
   if not (cp/'summary.json').exists():continue
   rejected=json.loads((cp/'summary.json').read_text());finite(rejected)
   for base,mapping in [(R,rejected['source_hashes']),(cp,rejected['state_hashes'])]:
    for n,h in mapping.items():assert digest(base/n)==h,n
   prev=R/rejected['previous_checkpoint'];old=json.loads((prev/'summary.json').read_text())
   assert old['passed'] and digest(prev/'summary.json')==rejected['previous_summary_sha256']
   assert rejected['withdrawal_anchor']['summary_sha256']==digest(anchor_path/'summary.json')
   evidence.append({'checkpoint':row['output'],'summary_sha256':digest(cp/'summary.json'),'physical_worker_passed':rejected['passed'],'flags':rejected['flags'],'swept_gap_m':rejected['swept_blade_minimum_gap_m'],'accepted':False})
  failed.append({'batch':p.parent.name,'reason':status['stop_reason'],'verified_endpoint_evidence':evidence});continue
 cp=R/status['accepted'];s=json.loads((cp/'summary.json').read_text());finite(s);assert s['passed']
 for base,mapping in [(R,s['source_hashes']),(cp,s['state_hashes'])]:
  for n,h in mapping.items():assert digest(base/n)==h,n
 prev=R/s['previous_checkpoint'];old=json.loads((prev/'summary.json').read_text())
 assert digest(prev/'summary.json')==s['previous_summary_sha256'] and old['passed']
 assert s['damage_states']==old['damage_states']==anchor['damage_states']
 assert s['withdrawal_anchor']['summary_sha256']==digest(anchor_path/'summary.json')
 audit=json.loads((cp.parent/(cp.name+'_audit.json')).read_text());finite(audit);assert audit['passed'] and Path(audit['checkpoint']).resolve()==cp.resolve()
 assert -.25000001<=s['depth_mm']-old['depth_mm']<=0
 if old['backend']=='triangle_spectral_evolving_v1':
  assert s['depth_mm']==old['depth_mm'] and s['energy_j']==old['energy_j']
  assert s['state_hashes']['positions.npy']==old['state_hashes']['positions.npy']
  assert s['cumulative_blade_work_j']==old['cumulative_blade_work_j']
 else:assert old['source_hashes']==s['source_hashes']
 rows.append({'checkpoint':status['accepted'],'depth_mm':s['depth_mm'],'summary_sha256':digest(cp/'summary.json'),'damage_and_history_exactly_unchanged':True,'force_residual':s['force_residual'],'physical_stability':s['minimum_softening_stability_eigenvalue'],'swept_gap_m':s['swept_blade_minimum_gap_m'],'phase_work_j':s['withdrawal_blade_work_j'],'phase_relative_energy_residual':s['withdrawal_relative_energy_residual'],'peak_rss_bytes':s['peak_rss_bytes']})
assert len(rows)>=2 and json.loads((F/'tests_v2.json').read_text())['passed']
report={'passed':True,'checked_utc':now.isoformat(),'accepted':rows,'failed_attempts_preserved':failed,'tests':json.loads((F/'tests_v2.json').read_text()),'main_insertion_checkpoint':str(anchor_path.relative_to(R)),'main_depth_mm':anchor['depth_mm'],'last_accepted_withdrawal':min(rows,key=lambda r:r['depth_mm']),'damage_specific_complete_withdrawal_validated':False,'damage_specific_cleared_reclosure_validated':False,'independent_release_validated':False,'full_cut':False,'simulator':False,'training':False,'qualifier_sha256':digest(Path(__file__))}
(F/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
