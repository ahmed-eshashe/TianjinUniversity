"""Recheck immutable provenance and independently audited new numerical branch."""
from pathlib import Path
import json,hashlib,math
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent;W=R/'runs/offline/tomato_triangle_withdrawal_01'
for p in [W/'baseline_hashes.json',R/'runs/offline/tomato_contact_continuation_01/baseline_hashes.json',W/'new_source_snapshot.json']:
 assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in json.loads(p.read_text()).items())
assert json.loads((W/'cleared_reclosure_qualification.json').read_text())['passed']
if (F/'source_snapshot.json').exists():
 assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in json.loads((F/'source_snapshot.json').read_text()).items())
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for item in v.values():finite(item)
 elif isinstance(v,list):
  for item in v:finite(item)
accepted=[];stops=[];all_worker_summaries=[];failed_stability=[]
folders=[F/'transition_hold']
for batch in sorted(F.glob('search_batch*')):
 if not (batch/'status.json').exists():continue
 status=json.loads((batch/'status.json').read_text());stops.append({'batch':batch.name,'stop_reason':status['stop_reason'],'last_accepted':status['last_accepted']})
 folders.extend(R/rec['output'] for rec in status['records'] if (R/rec['output']/'summary.json').exists())
 for rec in status['records']:
  folder=R/rec['output']
  for name in ['summary.json','candidate.json']:
   if (folder/name).exists():all_worker_summaries.append(json.loads((folder/name).read_text()))
for folder in folders:
 a_path=folder.parent/(folder.name+'_audit.json');s=json.loads((folder/'summary.json').read_text())
 if not s['passed']:
  if 'softening_stability' in s['flags']:failed_stability.append({'checkpoint':str(folder.relative_to(R)),'depth_mm':s['depth_mm'],'eigenvalue':s['minimum_softening_stability_eigenvalue']})
  continue
 assert a_path.exists(),'Passing worker without audit is not qualified'
 a=json.loads(a_path.read_text());assert a['passed'];finite(s);finite(a)
 assert s['backend']=='triangle_search_evolving_v1'
 for n,h in s['source_hashes'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
 for n,h in s['state_hashes'].items():assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==h
 old=json.loads((R/s['previous_checkpoint']/'summary.json').read_text());assert hashlib.sha256((R/s['previous_checkpoint']/'summary.json').read_bytes()).hexdigest()==s['previous_summary_sha256']
 assert all(v['damage']>=p['damage'] and v['kappa_m']>=p['kappa_m'] for v,p in zip(s['damage_states'],old['damage_states']))
 assert s['limits']=={'address_space_bytes':536870912,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}
 accepted.append((folder,s,a))
assert accepted
folder,s,a=max(accepted,key=lambda v:v[1]['depth_mm']);fallbacks=sum(sum(t['search_metric']=='positive_diagonal_descent' for o in v['outer_iterations'] for t in o['trace']) for _,v,_ in accepted)
report={'passed':True,'independently_audited_endpoints':len(accepted),'last_accepted':str(folder.relative_to(R)),'last_accepted_depth_mm':s['depth_mm'],'damaged_patches':s['damaged_patches'],'completely_failed_patches':s['completely_failed_patches'],'max_damage':s['max_damage'],'topology':s['topology'],'maximum_total_work_error_fraction':max(v['relative_energy_residual'] for _,v,_ in accepted),'minimum_swept_blade_gap_m':min(v['swept_blade_minimum_gap_m'] for _,v,_ in accepted),'minimum_physical_stability_eigenvalue':min(v['minimum_softening_stability_eigenvalue'] for _,v,_ in accepted),'maximum_accepted_worker_rss_bytes':max(v['peak_rss_bytes'] for _,v,_ in accepted),'fallback_iterations_in_final_worker_chunks':fallbacks,'fallback_iterations_all_worker_chunks':sum(t['search_metric']=='positive_diagonal_descent' for v in all_worker_summaries for o in v['outer_iterations'] for t in o['trace']),'maximum_all_worker_rss_bytes':max(v['peak_rss_bytes'] for v in all_worker_summaries),'batches':stops,'rejected_stability_states':failed_stability,'resolved_stability_depths_mm':[v['depth_mm'] for v in failed_stability if any(abs(w['depth_mm']-v['depth_mm'])<=1e-12 for _,w,_ in accepted)],'physical_model_and_acceptance_limits_unchanged':True,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
(F/'qualification.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report)
p=W/'handoff.json';h=json.loads(p.read_text());h.update({'status':'qualified_search_batch_finished','last_accepted_insertion':report['last_accepted'],'last_accepted_insertion_depth_mm':report['last_accepted_depth_mm'],'insertion_backend':'triangle_search_evolving_v1','next':'Read runs/offline/tomato_optimizer_release_01/qualification.json and latest search_batch status. Use the NEW run_search_probe.py, not the old v1 launcher, to continue this explicitly versioned numerical branch with fresh quota/time lease, max12 calls, independent audits and immutable sources.','updated_utc':datetime.now(timezone.utc).isoformat()});p.write_text(json.dumps(h,indent=2)+'\n')

unresolved=[v for v in failed_stability if not any(abs(w['depth_mm']-v['depth_mm'])<=1e-12 for _,w,_ in accepted)]
if unresolved:
 frontier=min(unresolved,key=lambda v:v['depth_mm'])
 (F/'stability_frontier.json').write_text(json.dumps({'failed_depth_mm':frontier['depth_mm'],'last_accepted_depth_mm':report['last_accepted_depth_mm'],'rejected_checkpoint':frontier['checkpoint'],'advancement_beyond_failed_stability_forbidden':True},indent=2)+'\n')
 h['status']='physical_stability_frontier_requires_diagnosis'
 h['next']='Do not continue deeper than the failed stability frontier. Independently diagnose the rejected mode and bracket only BELOW the depth in runs/offline/tomato_optimizer_release_01/stability_frontier.json. Do not change physical laws or acceptance thresholds; no simulator/training.'
 p.write_text(json.dumps(h,indent=2)+'\n')

if failed_stability and not unresolved:
 (F/'stability_frontier.json').write_text(json.dumps({'resolved':True,'resolved_depths_mm':[v['depth_mm'] for v in failed_stability],'resolution_checkpoint':report['last_accepted'],'all_original_physical_gates_passed':True,'rejected_states_retained':True},indent=2)+'\n')
