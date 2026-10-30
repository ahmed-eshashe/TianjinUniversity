"""Verify new deeper insertion branch without joining validation trajectories."""
from pathlib import Path
import hashlib,json,math
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
for manifest in [F/'baseline_hashes.json',R/'runs/offline/tomato_contact_continuation_01/baseline_hashes.json']:
 assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in json.loads(manifest.read_text()).items())
assert json.loads((F/'cleared_reclosure_qualification.json').read_text())['passed']
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for item in v.values():finite(item)
 elif isinstance(v,list):
  for item in v:finite(item)
accepted=[];stops=[]
for batch in sorted(F.glob('insertion_batch*')):
 if not (batch/'status.json').exists():continue
 status=json.loads((batch/'status.json').read_text());stops.append({'batch':batch.name,'stop_reason':status['stop_reason'],'last_accepted':status['last_accepted']})
 for rec in status['records']:
  folder=R/rec['output'];ap=folder.parent/(folder.name+'_audit.json')
  if not ap.exists():continue
  s=json.loads((folder/'summary.json').read_text());a=json.loads(ap.read_text());assert s['passed'] and a['passed'];finite(s);finite(a)
  assert s['backend']=='triangle_evolving_v1'
  for n,h in s['source_hashes'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
  for n,h in s['state_hashes'].items():assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==h
  previous=R/s['previous_checkpoint'];old=json.loads((previous/'summary.json').read_text())
  assert hashlib.sha256((previous/'summary.json').read_bytes()).hexdigest()==s['previous_summary_sha256']
  assert all(v['damage']>=w['damage'] and v['kappa_m']>=w['kappa_m'] for v,w in zip(s['damage_states'],old['damage_states']))
  assert s['limits']=={'address_space_bytes':536870912,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}
  accepted.append((folder,s,a))
assert accepted
folder,s,a=max(accepted,key=lambda v:v[1]['depth_mm'])
report={'passed':True,'independently_audited_endpoints':len(accepted),'last_accepted':str(folder.relative_to(R)),'last_accepted_depth_mm':s['depth_mm'],'damaged_patches':s['damaged_patches'],'completely_failed_patches':s['completely_failed_patches'],'max_damage':s['max_damage'],'topology':s['topology'],'maximum_total_work_error_fraction':max(v['relative_energy_residual'] for _,v,_ in accepted),'minimum_swept_blade_gap_m':min(v['swept_blade_minimum_gap_m'] for _,v,_ in accepted),'maximum_accepted_worker_rss_bytes':max(v['peak_rss_bytes'] for _,v,_ in accepted),'batches':stops,'validation_branches_separate':True,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
(F/'insertion_qualification.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
p=F/'handoff.json';h=json.loads(p.read_text());h.update({'last_accepted_insertion':report['last_accepted'],'last_accepted_insertion_depth_mm':report['last_accepted_depth_mm'],'last_insertion_stop':stops[-1],'status':'qualified_insertion_batch_finished','updated_utc':datetime.now(timezone.utc).isoformat()});p.write_text(json.dumps(h,indent=2)+'\n');print(report)
