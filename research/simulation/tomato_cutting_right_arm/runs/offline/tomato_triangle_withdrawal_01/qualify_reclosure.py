"""Collect audited supported cycle; never equate it with full-cut release."""
from pathlib import Path
import hashlib,json,math
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
base=json.loads((F/'baseline_hashes.json').read_text())
original=json.loads((R/'runs/offline/tomato_contact_continuation_01/baseline_hashes.json').read_text())
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in original.items()),'Original preservation failure'
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in base.items())
withdrawal=json.loads((F/'qualification.json').read_text());assert withdrawal['passed'] and withdrawal['complete_withdrawal_validated']
seed=json.loads((R/withdrawal['last_accepted']/'summary.json').read_text());phases={}
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for item in v.values():finite(item)
 elif isinstance(v,list):
  for item in v:finite(item)
for batch in sorted(F.glob('reclosure_batch*')):
 if not (batch/'status.json').exists():continue
 status=json.loads((batch/'status.json').read_text())
 for rec in status['records']:
  folder=R/rec['output'];audit=folder.parent/(folder.name+'_audit.json')
  if not audit.exists():continue
  a=json.loads(audit.read_text());s=json.loads((folder/'summary.json').read_text())
  assert s['passed'] and a['passed'];finite(s);finite(a)
  for n,h in s['source_hashes'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
  for n,h in s['state_hashes'].items():assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==h
  assert s['damage_states']==seed['damage_states']
  assert s['depth_mm']==0. and s['backend']=='triangle_reclosure_v1'
  assert s['limits']=={'address_space_bytes':536870912,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}
  phases[rec['phase_index']]=(folder,s,a)
complete=set(phases)==set(range(10));checks={'ten_phases_independently_audited':complete,'damage_and_history_exactly_retained':True,'baseline_sources_unchanged':True}
if complete:
 positive=phases[2][1];negative=phases[6][1];final=phases[9][1]
 checks.update({'compression_positive_load':positive['back_cap_force_n']>0 and positive['cut_contact_force_n']>0,'compression_faces_closed':positive['maximum_cut_gap_m']<=1e-9,'compression_load_balanced':abs(positive['back_cap_force_n']-positive['cut_contact_force_n'])<=.01*max(positive['back_cap_force_n'],positive['cut_contact_force_n'],1e-4),'negative_drive_reopens_faces':negative['maximum_cut_gap_m']>1e-9,'final_faces_reclose':final['maximum_cut_gap_m']<=1e-9,'final_stored_energy_returns':abs(final['energy_j']-seed['energy_j'])<=1e-12})
last=phases[max(phases)] if phases else None
report={'passed':all(checks.values()),'checks':checks,'accepted_phases':sorted(phases),'last_accepted':str(last[0].relative_to(R)) if last else withdrawal['last_accepted'],'complete_supported_cycle':complete,'maximum_reclosure_energy_residual_fraction':max((s['reclosure_relative_energy_residual'] for _,s,_ in phases.values()),default=None),'minimum_swept_blade_gap_m':min((s['swept_blade_minimum_gap_m'] for _,s,_ in phases.values()),default=None),'maximum_opening_m':max((s['maximum_cut_gap_m'] for _,s,_ in phases.values()),default=None),'maximum_worker_rss_bytes':max((s['peak_rss_bytes'] for _,s,_ in phases.values()),default=None),'phase_metrics':[{k:s[k] for k in ['drive_mm','energy_j','back_cap_force_n','cut_contact_force_n','minimum_cut_gap_m','maximum_cut_gap_m','reclosure_relative_energy_residual']} for _,s,_ in [phases[i] for i in sorted(phases)]],'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
(F/'reclosure_qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
