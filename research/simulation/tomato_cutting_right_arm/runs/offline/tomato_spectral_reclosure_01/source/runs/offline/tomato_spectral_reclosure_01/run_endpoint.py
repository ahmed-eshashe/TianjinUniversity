"""One bounded serial supported-reclosure endpoint with independent audit."""
import argparse,json,hashlib,os,fcntl,subprocess,time,sys
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent;W=R/'runs/offline/tomato_triangle_withdrawal_01'
sys.path.insert(0,str(R/'rl'));from tomato_optimizer_cycle import restart_fingerprint
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--drive-mm',type=float,required=True);a=p.parse_args();assert abs(a.drive_mm)<=.05
hs=[]
for n in ['logs/offline_overnight.lock','logs/right_arm_control.lock']:
 h=(R/n).open('a');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);hs.append(h)
fcntl.flock(hs[-1],fcntl.LOCK_UN);hs[-1].close()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safety():
 now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
 q=json.loads((W/'quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(q['checked_utc'])).total_seconds()<=480 and q['maximum_reported_used_percent']<45
 for folder in (R/'runs/offline').iterdir():
  if not folder.is_dir():continue
  if (folder/'stability_frontier.json').exists():assert json.loads((folder/'stability_frontier.json').read_text()).get('resolved',False)
 for name in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01','tomato_optimizer_release_01','tomato_curvature_search_01','tomato_global_search_01','tomato_first_failure_refinement_01','tomato_cubic_path_diagnostic_01','tomato_spectral_withdrawal_01','tomato_spectral_reclosure_01']:
  folder=R/'runs/offline'/name;paths=list(folder.glob('*source_snapshot*.json'))
  if name in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01']:paths.append(folder/'baseline_hashes.json')
  for manifest in paths:
   for n,h in json.loads(manifest.read_text()).items():assert digest(R/n)==h,n
safety();assert json.loads((F/'tests.json').read_text())['passed']
previous=a.previous.resolve();old=json.loads((previous/'summary.json').read_text());assert old['passed'] and old['depth_mm']<=0.
assert json.loads((previous.parent/(previous.name+'_audit.json')).read_text())['passed']
from tomato_reclosure_provenance import ANCHOR,ANCHOR_SHA
if old['backend']=='triangle_spectral_withdrawal_v1':assert previous==R/ANCHOR and digest(previous/'summary.json')==ANCHOR_SHA and a.drive_mm==0.
else:assert old['backend']=='triangle_spectral_cleared_reclosure_v1' and abs(a.drive_mm-old['drive_mm'])<=.025000001
batch=F/a.name;batch.mkdir(exist_ok=False);calls=0;records=[];accepted=None;reason='bounded_worker_budget';resume=None;fingerprint=None;start=time.monotonic()
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def call(args,path):
 global calls
 safety();assert calls<12;calls+=1
 with path.open('w') as log:
  try:return subprocess.run([str(R/'.venv-native/bin/python'),*args],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60).returncode
  except subprocess.TimeoutExpired:return 124
for i in range(11):
 out=batch/('attempt%03d'%i);args=['rl/offline_tomato_spectral_reclosure.py','--drive-mm',str(a.drive_mm),'--previous',str(previous),'--output',str(out)]
 if resume:args+=['--resume',str(resume)]
 code=call(args,batch/('worker%03d.log'%i));row={'output':str(out.relative_to(R)),'returncode':code};records.append(row)
 if code:reason='worker_failed';break
 if (out/'candidate.json').exists():
  s=json.loads((out/'candidate.json').read_text());assert s['optimization_only'] and not s['passed'];assert s['trial_damage_states']==old['damage_states'];row['optimization_only']=True;new=restart_fingerprint(s)
  if new==fingerprint:reason='repeated_uncommitted_optimizer_state';break
  fingerprint=new;resume=out
 else:
  s=json.loads((out/'summary.json').read_text());row.update(passed=s['passed'],flags=s['flags'])
  if not s['passed']:
   reason='physical_gate_failed'
   if 'softening_stability' in s['flags']:(F/'stability_frontier.json').write_text(json.dumps({'resolved':False,'checkpoint':str(out.relative_to(R))}))
   break
  assert s['damage_states']==old['damage_states']
  audit=batch/(out.name+'_audit.json');code=call(['rl/audit_tomato_spectral_reclosure.py','--checkpoint',str(out),'--output',str(audit)],batch/(out.name+'_audit.log'))
  if code or not json.loads(audit.read_text())['passed']:reason='independent_audit_failed';break
  accepted=str(out.relative_to(R));reason='independently_passed';break
status={'accepted':accepted,'stop_reason':reason,'previous':str(previous.relative_to(R)),'drive_mm':a.drive_mm,'calls':calls,'records':records,'runtime_s':time.monotonic()-start,'source_hashes':json.loads((F/'source_snapshot.json').read_text()),'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False};(batch/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(status)
