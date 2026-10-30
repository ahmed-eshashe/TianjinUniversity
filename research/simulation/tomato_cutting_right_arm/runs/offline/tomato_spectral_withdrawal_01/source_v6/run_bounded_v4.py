"""One serial bounded withdrawal endpoint, no simulator or full-removal loop."""
import argparse,json,hashlib,os,fcntl,subprocess,time,sys,math
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent;W=R/'runs/offline/tomato_triangle_withdrawal_01';V=R/'runs/offline/tomato_curvature_search_01'
sys.path.insert(0,str(R/'rl'));from tomato_optimizer_cycle import restart_fingerprint
p=argparse.ArgumentParser();p.add_argument('--initial-resume',type=Path);p.add_argument('--name',required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--depth-mm',required=True,type=float);a=p.parse_args()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for x in v.values():finite(x)
 elif isinstance(v,list):
  for x in v:finite(x)
def safety():
 now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
 lease=json.loads((W/'quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480 and lease['maximum_reported_used_percent']<45
 for folder in [R/'runs/offline/tomato_optimizer_release_01',V,F]:
  if (folder/'stability_frontier.json').exists():assert json.loads((folder/'stability_frontier.json').read_text()).get('resolved',False),'Unresolved stability frontier'
 for folder in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01','tomato_optimizer_release_01','tomato_curvature_search_01','tomato_global_search_01','tomato_first_failure_refinement_01','tomato_cubic_path_diagnostic_01','tomato_spectral_withdrawal_01']:
  paths=list((R/'runs/offline'/folder).glob('*source_snapshot*.json'))
  if folder in ['tomato_contact_continuation_01','tomato_triangle_withdrawal_01']:paths.append(R/'runs/offline'/folder/'baseline_hashes.json')
  for path in paths:
   for n,h in json.loads(path.read_text()).items():assert digest(R/n)==h,n
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
check=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(check,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(check,fcntl.LOCK_UN);check.close();safety()
assert json.loads((F/'tests_v2.json').read_text())['passed'];assert json.loads((W/'cleared_reclosure_qualification.json').read_text())['passed']
previous=a.previous.resolve();old=json.loads((previous/'summary.json').read_text());assert old['passed']
assert -.031250000001<=a.depth_mm-old['depth_mm']<=0,'One bounded withdrawal interval <=0.03125mm'
if old['backend']=='triangle_spectral_evolving_v1':
 assert a.depth_mm==old['depth_mm'];assert json.loads((previous.parent/(previous.name+'_audit.json')).read_text())['passed']
else:
 assert old['backend']=='triangle_spectral_withdrawal_v1';assert json.loads((previous.parent/(previous.name+'_audit.json')).read_text())['passed']
batch=F/a.name;batch.mkdir(exist_ok=False);calls=0;records=[];accepted=None;reason='bounded_worker_budget';resume=a.initial_resume;fingerprint=None;start=time.monotonic()
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def call(args,log):
 global calls
 safety();assert calls<12;calls+=1
 with log.open('w') as out:
  try:return subprocess.run([str(R/'.venv-native/bin/python'),*args],cwd=R,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=60).returncode
  except subprocess.TimeoutExpired:return 124
if resume:
 seed=json.loads((resume/'candidate.json').read_text())
 assert seed['optimization_only'] and not seed['passed'] and seed['depth_mm']==a.depth_mm
 assert seed['previous_summary_sha256']==digest(previous/'summary.json') and seed['source_hashes']==old['source_hashes']
 assert seed['trial_damage_states']==old['damage_states'] and digest(resume/'guess.npy')==seed['guess_sha256']
 for n,h in seed['prediction_source_hashes'].items():assert digest(R/n)==h
 origin=R/seed['source_candidate_checkpoint'];original=json.loads((origin/'candidate.json').read_text())
 assert digest(origin/'candidate.json')==seed['source_candidate_sha256']
 assert original['depth_mm']==seed['depth_mm'] and original['previous_summary_sha256']==seed['previous_summary_sha256'] and original['trial_damage_states']==seed['trial_damage_states']
 fingerprint=restart_fingerprint(seed)
for i in range(11):
 out=batch/('attempt%03d'%i);args=['rl/offline_tomato_spectral_withdrawal_v2.py','--depth-mm',str(a.depth_mm),'--previous',str(previous),'--output',str(out)]
 if resume:args+=['--resume',str(resume)]
 code=call(args,batch/('worker%03d.log'%i));row={'output':str(out.relative_to(R)),'returncode':code};records.append(row)
 if code:reason='worker_failed';break
 if (out/'candidate.json').exists():
  s=json.loads((out/'candidate.json').read_text());finite(s);row.update(optimization_only=True,reason=s['reason']);resume=out;new=restart_fingerprint(s)
  if new==fingerprint:reason='repeated_uncommitted_optimizer_state';break
  fingerprint=new
 else:
  s=json.loads((out/'summary.json').read_text());finite(s);row.update(passed=s['passed'],flags=s['flags'])
  if not s['passed']:
   reason='physical_gate_failed'
   if 'softening_stability' in s['flags']:(F/'stability_frontier.json').write_text(json.dumps({'resolved':False,'checkpoint':str(out.relative_to(R)),'depth_mm':a.depth_mm},indent=2)+'\n')
   break
  audit=batch/(out.name+'_audit.json');code=call(['rl/audit_tomato_spectral_withdrawal.py','--checkpoint',str(out),'--output',str(audit)],batch/(out.name+'_audit.log'))
  if code:reason='independent_audit_failed';break
  ar=json.loads(audit.read_text());finite(ar)
  if not ar['passed']:reason='independent_audit_failed';break
  accepted=str(out.relative_to(R));reason='independently_passed';break
status={'name':a.name,'previous':str(previous.relative_to(R)),'target_depth_mm':a.depth_mm,'calls':calls,'records':records,'accepted':accepted,'stop_reason':reason,'runtime_s':time.monotonic()-start,'source_hashes':json.loads((F/'source_snapshot_v6.json').read_text()),'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
(batch/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(status,flush=True)
