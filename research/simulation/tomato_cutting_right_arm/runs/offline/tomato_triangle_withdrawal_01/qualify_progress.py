"""Metadata-only collection of independently audited withdrawal evidence."""
from pathlib import Path
import hashlib,json,math
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
base=json.loads((F/'baseline_hashes.json').read_text())
original=json.loads((R/'runs/offline/tomato_contact_continuation_01/baseline_hashes.json').read_text())
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in original.items()),'Original preservation failure';changed=[n for n,h in base.items() if hashlib.sha256((R/n).read_bytes()).hexdigest()!=h]
assert not changed,changed
anchor=R/'runs/offline/tomato_contact_continuation_01/evolving_cap_extension/attempt045_01';seed=json.loads((anchor/'summary.json').read_text());accepted=[];rejected=[];candidate_count=0
for folder in sorted([F/'repeat',*F.glob('withdrawal_batch*/attempt*')]):
 if not folder.is_dir():continue
 if (folder/'candidate.json').exists():candidate_count+=1
 if not (folder/'summary.json').exists():continue
 s=json.loads((folder/'summary.json').read_text());audit=folder.parent/(folder.name+'_audit.json')
 if not s['passed']:rejected.append(str(folder.relative_to(R)));continue
 assert audit.exists(),f'Missing audit {folder}'
 a=json.loads(audit.read_text());assert a['passed'],a
 for n,h in s['source_hashes'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
 for n,h in s['state_hashes'].items():assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==h
 assert s['limits']=={'address_space_bytes':536870912,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}
 accepted.append((folder,s,a))
assert accepted
def finite(v):
 if isinstance(v,float):assert math.isfinite(v),'Nonfinite archived metric'
 elif isinstance(v,dict):
  for item in v.values():finite(item)
 elif isinstance(v,list):
  for item in v:finite(item)
for _,state,audit in accepted:finite(state);finite(audit)
last=min(accepted,key=lambda item:item[1]['depth_mm']);folder,s,a=last
report={'passed':True,'existing_files_unchanged':len(base),'independently_audited_endpoints':len(accepted),'last_accepted':str(folder.relative_to(R)),'last_accepted_depth_mm':s['depth_mm'],'damage_and_history_exactly_unchanged_from_seed':all(v['damage_states']==seed['damage_states'] for _,v,_ in accepted),'maximum_withdrawal_energy_residual_fraction':max(v['withdrawal_relative_energy_residual'] for _,v,_ in accepted),'minimum_cut_gap_m':min(v['minimum_cut_gap_m'] for _,v,_ in accepted),'minimum_swept_blade_gap_m':min(v['swept_blade_minimum_gap_m'] for _,v,_ in accepted),'maximum_worker_rss_bytes':max(v['peak_rss_bytes'] for _,v,_ in accepted),'optimization_only_candidates':candidate_count,'rejected_endpoints':rejected,'complete_withdrawal_validated':s['depth_mm']==0,'supported_reclosure_validated':False,'independent_release_validated':False,'full_cut':False,'simulator':False,'training':False}
(F/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

from datetime import datetime,timezone
handoff_path=F/'handoff.json'
handoff=json.loads(handoff_path.read_text()) if handoff_path.exists() else {}
handoff.update(report)
handoff['status']='qualified_batch_complete'
handoff['next']=('Refresh actual quota/time and continue withdrawal in a fresh bounded batch.' if s['depth_mm']>0 else 'Complete withdrawal qualified. Refresh actual quota/time and test separate supported reclosure worker; it has not yet been validated.')
handoff['updated_utc']=datetime.now(timezone.utc).isoformat()
handoff_path.write_text(json.dumps(handoff,indent=2)+'\n')
