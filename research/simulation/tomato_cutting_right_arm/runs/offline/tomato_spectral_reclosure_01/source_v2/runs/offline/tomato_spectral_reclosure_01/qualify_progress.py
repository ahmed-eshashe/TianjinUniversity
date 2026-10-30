"""Capped saved-evidence checks for the damage-specific supported cycle."""
import json,hashlib,math,resource,signal,fcntl,re
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
q=json.loads((R/'runs/offline/tomato_triangle_withdrawal_01/quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(q['checked_utc'])).total_seconds()<=480 and q['maximum_reported_used_percent']<45
hs=[]
for n in ['logs/offline_overnight.lock','logs/right_arm_control.lock']:
 h=(R/n).open('a');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);hs.append(h)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for x in v.values():finite(x)
 elif isinstance(v,list):
  for x in v:finite(x)
for folder in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01','tomato_optimizer_release_01','tomato_curvature_search_01','tomato_global_search_01','tomato_first_failure_refinement_01','tomato_cubic_path_diagnostic_01','tomato_spectral_withdrawal_01','tomato_spectral_reclosure_01']:
 paths=list((R/'runs/offline'/folder).glob('*source_snapshot*.json'))
 if folder in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01']:paths.append(R/'runs/offline'/folder/'baseline_hashes.json')
 for m in paths:
  for n,h in json.loads(m.read_text()).items():assert digest(R/n)==h,n
assert json.loads((F/'tests.json').read_text())=={'passed':True,'tests':13,'failures':0,'errors':0,'forbidden_imports':[]}
Z=R/'runs/offline/tomato_spectral_withdrawal_01/zero_depth_chain_qualification.json';z=json.loads(Z.read_text());assert z['passed'] and z['withdrawal_to_zero_depth_validated'];p=R/z['last_accepted']['checkpoint'];seed=json.loads((p/'summary.json').read_text());assert digest(p/'summary.json')==z['last_accepted']['summary_sha256'];prev=p
DRIVES=[0.,.025,.05,.025,0.,-.025,-.05,-.025,0.,0.];rows=[]
for sf in sorted(F.glob('phase*/status.json')):
 status=json.loads(sf.read_text());finite(status);assert status['calls']<=12
 if not status['accepted']:continue
 idx=int(re.match(r'phase(\d+)',sf.parent.name).group(1));assert idx==len(rows)
 cp=R/status['accepted'];s=json.loads((cp/'summary.json').read_text());a=json.loads((cp.parent/(cp.name+'_audit.json')).read_text());assert s['passed'] and a['passed'];assert s['drive_mm']==DRIVES[idx];assert s['previous_checkpoint']==str(prev.relative_to(R)) and s['previous_summary_sha256']==digest(prev/'summary.json');assert s['damage_states']==seed['damage_states'];assert s['reclosure_anchor']['summary_sha256']==digest(p/'summary.json')
 for blob in [s,a]:
  gap=blob['independent_polygon_minimum_gap_m']
  if not math.isfinite(gap):assert gap==math.inf and a['polygon_vertices']==0 and s['minimum_blade_clearance_m']>=.0005 and s['maximum_blade_multiplier_n']==0.
  finite({k:v for k,v in blob.items() if k!='independent_polygon_minimum_gap_m'})
 for base,mapping in [(R,s['source_hashes']),(cp,s['state_hashes'])]:
  for n,h in mapping.items():assert digest(base/n)==h
 assert s['minimum_blade_clearance_m']>=.0005 and s['maximum_blade_multiplier_n']==0.
 assert s['limits']=={'address_space_bytes':536870912,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}
 rows.append({'checkpoint':status['accepted'],'summary_sha256':digest(cp/'summary.json'),**{k:s[k] for k in ['drive_mm','energy_j','back_cap_force_n','cut_contact_force_n','minimum_cut_gap_m','maximum_cut_gap_m','minimum_blade_clearance_m','maximum_blade_multiplier_n','force_residual','minimum_softening_stability_eigenvalue','swept_blade_minimum_gap_m','reclosure_relative_energy_residual','peak_rss_bytes']}});prev=cp
checks={'all_accepted_sources_states_audits_history_checked':True};complete=len(rows)==10
if complete:
 pos,neg,final=rows[2],rows[6],rows[9]
 checks.update(compression_positive_load=pos['back_cap_force_n']>0 and pos['cut_contact_force_n']>0,compression_faces_closed=pos['maximum_cut_gap_m']<=1e-9,compression_load_balanced=abs(pos['back_cap_force_n']-pos['cut_contact_force_n'])<=.01*max(pos['back_cap_force_n'],pos['cut_contact_force_n'],1e-4),negative_drive_reopens_faces=neg['maximum_cut_gap_m']>1e-9,final_faces_reclose=final['maximum_cut_gap_m']<=1e-9,final_stored_energy_returns=abs(final['energy_j']-seed['energy_j'])<=1e-12)
report={'passed':all(checks.values()),'checked_utc':now.isoformat(),'checks':checks,'accepted':rows,'complete_supported_cycle':complete,'blade_cleared':bool(rows),'cleared_reclosure_validated':complete and all(checks.values()),'withdrawal_zero_chain_sha256':digest(Z),'tests':13,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False,'qualifier_sha256':digest(Path(__file__))};(F/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
