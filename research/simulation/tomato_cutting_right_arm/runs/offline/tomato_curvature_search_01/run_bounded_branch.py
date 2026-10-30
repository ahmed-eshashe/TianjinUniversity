"""Serial, audited same-depth numerical-backend transition and one small step."""
import argparse,json,hashlib,os,fcntl,subprocess,time,math
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent;W=R/'runs/offline/tomato_triangle_withdrawal_01';G=R/'runs/offline/tomato_contact_continuation_01';V=R/'runs/offline/tomato_optimizer_release_01'
p=argparse.ArgumentParser();p.add_argument('--predict',action='store_true');p.add_argument('--initial-resume',type=Path);p.add_argument('--name',required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--depth-mm',type=float,required=True);a=p.parse_args()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(value):
 if isinstance(value,float):assert math.isfinite(value),'Nonfinite metric'
 elif isinstance(value,dict):
  for v in value.values():finite(v)
 elif isinstance(value,list):
  for v in value:finite(v)
def safety():
 now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc),'Deadline near'
 lease=json.loads((W/'quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480,'Stale quota';assert lease['maximum_reported_used_percent']<45
 for folder in [V,F]:
  if (folder/'stability_frontier.json').exists():assert json.loads((folder/'stability_frontier.json').read_text()).get('resolved',False),'Unresolved physical stability frontier'
 for path in [G/'baseline_hashes.json',W/'baseline_hashes.json',W/'new_source_snapshot.json',V/'source_snapshot.json',F/'source_snapshot.json']:
  for n,h in json.loads(path.read_text()).items():assert digest(R/n)==h,('Preservation failure',n)
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
check=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(check,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(check,fcntl.LOCK_UN);check.close()
safety()
for path in [F/'tests.json',W/'cleared_reclosure_qualification.json',G/'fracture_refinement.json',G/'continuation_surface/summary.json',G/'continuation_energy180.json',G/'continuation_energy360.json']:
 assert json.loads(path.read_text())['passed'],str(path)
assert json.loads((F/'tests.json').read_text())['tests']==132
previous=a.previous.resolve();old=json.loads((previous/'summary.json').read_text());assert old['passed'];assert 0<=a.depth_mm-old['depth_mm']<=.031250001
if old['backend']=='triangle_search_evolving_v1':assert a.depth_mm==old['depth_mm'],'Transition must first hold same pose'
else:assert old['backend']=='triangle_spectral_evolving_v1';assert json.loads((previous.parent/(previous.name+'_audit.json')).read_text())['passed']
batch=F/a.name;batch.mkdir(exist_ok=False);records=[];start=time.monotonic();resume=a.initial_resume;calls=0;accepted=None;reason='bounded_worker_budget'
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def call(args,log):
 global calls
 safety();assert calls<12;calls+=1
 with log.open('w') as out:
  try:proc=subprocess.run([str(R/'.venv-native/bin/python'),*args],cwd=R,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=60);return proc.returncode
  except subprocess.TimeoutExpired:return 124
if a.predict:
 assert resume is None and a.depth_mm>old['depth_mm']
 resume=batch/'prediction'
 code=call(['rl/offline_tomato_spectral_predictor.py','--previous',str(previous),'--depth-mm',str(a.depth_mm),'--output',str(resume)],batch/'prediction.log')
 assert code==0,'Predictor failed; no mechanical step launched'
for chunk in range(11):
 if calls>=11:break
 out=batch/f'attempt{chunk:03d}';args=['rl/offline_tomato_spectral_evolution.py','--depth-mm',str(a.depth_mm),'--previous',str(previous),'--output',str(out)]
 if resume:args+=['--resume',str(resume)]
 code=call(args,batch/f'worker{chunk:03d}.log');record={'chunk':chunk,'returncode':code,'output':str(out.relative_to(R))};records.append(record)
 if code:reason='worker_failed';break
 if (out/'candidate.json').exists():
  s=json.loads((out/'candidate.json').read_text());record['optimization_only']=True;record['reason']=s['reason'];resume=out
 else:
  s=json.loads((out/'summary.json').read_text());finite(s);record.update(passed=s['passed'],flags=s['flags'])
  if not s['passed']:
   reason='physical_gate_failed'
   if 'softening_stability' in s['flags']:(F/'stability_frontier.json').write_text(json.dumps({'resolved':False,'failed_depth_mm':a.depth_mm,'checkpoint':str(out.relative_to(R))},indent=2)+'\n')
   break
  audit=batch/(out.name+'_audit.json');code=call(['rl/audit_tomato_spectral_evolution.py','--checkpoint',str(out),'--output',str(audit)],batch/(out.name+'_audit.log'))
  if code:reason='independent_audit_failed';break
  audit_result=json.loads(audit.read_text());finite(audit_result)
  if not audit_result['passed']:reason='independent_audit_failed';break
  if a.depth_mm==old['depth_mm']:
   for key in ['energy_j','fracture_dissipation_j','damage_states','cumulative_blade_work_j']:assert s[key]==old[key],('Transition changed physical state',key)
  accepted=str(out.relative_to(R));reason='independently_passed';break
 report={'accepted':accepted,'stop_reason':'in_progress','depth_mm':a.depth_mm,'calls':calls,'records':records}
 (batch/'status.json').write_text(json.dumps(report,indent=2)+'\n')
safety();report={'accepted':accepted,'stop_reason':reason,'depth_mm':a.depth_mm,'physical_previous':str(previous.relative_to(R)),'calls':calls,'records':records,'runtime_s':time.monotonic()-start,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
(batch/'status.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
