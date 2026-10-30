"""Bounded serial supported reclosure test, after complete withdrawal only."""
import argparse,json,os,subprocess,time,fcntl
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--previous',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--start-index',type=int,default=0);p.add_argument('--resume',type=Path);a=p.parse_args()
DRIVES=[0.,.025,.05,.025,0.,-.025,-.05,-.025,0.,0.]
assert 0<=a.start_index<len(DRIVES)
previous=a.previous.resolve();initial=json.loads((previous/'summary.json').read_text());assert initial['passed'] and initial['depth_mm']==0
out=F/a.name;out.mkdir(exist_ok=False);records=[];workers=0;stop=None;start=time.monotonic();next_index=a.start_index
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
def guard():
 now=datetime.now(timezone.utc)
 if (datetime(2026,10,26,4,54,40,tzinfo=timezone.utc)-now).total_seconds()<65:raise RuntimeError('hard_deadline')
 q=json.loads((F/'quota_lease.json').read_text());age=(now-datetime.fromisoformat(q['checked_utc'])).total_seconds()
 if not 0<=age<=480:raise RuntimeError('quota_lease_expired_or_invalid')
 if q['maximum_reported_used_percent']>=45:raise RuntimeError('quota_margin_stop')
def run(script,args,tag):
 guard();res=subprocess.run([str(R/'.venv-native/bin/python'),script,*args],cwd=R,env=ENV,capture_output=True,text=True,timeout=60);(out/(tag+'.log')).write_text(res.stdout+res.stderr);return res
with (R/'logs/offline_overnight.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  for index in range(a.start_index,len(DRIVES)):
   next_index=index;resume=a.resume.resolve() if index==a.start_index and a.resume else None;accepted=None
   for chunk in range(min(8,12-workers)):
    tag=f'phase{index:02d}_{chunk:02d}';folder=out/tag;args=['--drive-mm',str(DRIVES[index]),'--previous',str(previous),'--output',str(folder)]
    if resume:args+=['--resume',str(resume)]
    result=run('rl/offline_tomato_triangle_reclosure.py',args,tag);workers+=1;rec={'phase_index':index,'drive_mm':DRIVES[index],'returncode':result.returncode,'output':str(folder.relative_to(R))};records.append(rec)
    if result.returncode:stop='worker_resource_or_solver_stop';break
    if (folder/'summary.json').exists():
     s=json.loads((folder/'summary.json').read_text());rec.update({k:s[k] for k in ['passed','flags','runtime_s','peak_rss_bytes','reclosure_relative_energy_residual','maximum_cut_gap_m','back_cap_force_n','cut_contact_force_n']})
     if not s['passed']:stop='physical_gate_failed';break
     audit=out/(tag+'_audit.json');result=run('rl/audit_tomato_triangle_reclosure.py',['--checkpoint',str(folder),'--output',str(audit)],tag+'_audit')
     if result.returncode or not json.loads(audit.read_text())['passed']:stop='independent_audit_failed'
     else:accepted=folder
     print(rec,flush=True);break
    s=json.loads((folder/'candidate.json').read_text());assert s['optimization_only'] and not s['passed'];resume=folder;rec['optimization_only']=True;print(rec,flush=True)
   if accepted:previous=accepted;next_index=index+1
   elif not stop:stop='bounded_optimization_budget'
   if workers>=12:stop=stop or 'bounded_worker_budget'
   status={'last_accepted':str(previous.relative_to(R)),'next_index':next_index,'workers':workers,'records':records,'stop_reason':stop,'runtime_s':time.monotonic()-start,'simulator':False,'training':False,'full_cut':False};(out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
   if stop:break
 except Exception as e:stop=str(e)
 status={'last_accepted':str(previous.relative_to(R)),'next_index':next_index,'workers':workers,'records':records,'stop_reason':stop or 'supported_cycle_complete','runtime_s':time.monotonic()-start,'simulator':False,'training':False,'full_cut':False};(out/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(status,flush=True)
