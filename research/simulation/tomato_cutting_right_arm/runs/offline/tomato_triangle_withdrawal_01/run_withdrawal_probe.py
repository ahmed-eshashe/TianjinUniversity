"""Short serial batches. Quota lease must be refreshed from actual app readings."""
import argparse,json,os,subprocess,time,fcntl
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--previous',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--target-mm',type=float,default=0.);p.add_argument('--step-mm',type=float,default=.125);p.add_argument('--workers',type=int,default=12);a=p.parse_args()
assert 0<a.step_mm<=.25 and 1<=a.workers<=12
previous=a.previous.resolve();depth=json.loads((previous/'summary.json').read_text())['depth_mm'];assert 0<=a.target_mm<depth
out=F/a.name;out.mkdir(exist_ok=False);records=[];workers=0;stop=None;start=time.monotonic();target=max(a.target_mm,depth-a.step_mm);level=0
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
DEADLINE=datetime(2026,10,26,4,54,40,tzinfo=timezone.utc)
def guard():
    now=datetime.now(timezone.utc)
    if (DEADLINE-now).total_seconds()<65:raise RuntimeError('hard_deadline')
    q=json.loads((F/'quota_lease.json').read_text());age=(now-datetime.fromisoformat(q['checked_utc'])).total_seconds()
    if not 0<=age<=480:raise RuntimeError('quota_lease_expired_or_invalid')
    if q['maximum_reported_used_percent']>=45:raise RuntimeError('quota_margin_stop')
def run(script,args,tag):
    guard();res=subprocess.run([str(R/'.venv-native/bin/python'),script,*args],cwd=R,env=ENV,capture_output=True,text=True,timeout=60)
    (out/(tag+'.log')).write_text(res.stdout+res.stderr);return res
with (R/'logs/offline_overnight.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:
        while workers<a.workers and not stop:
            resume=None;accepted=None;flags=None
            old=json.loads((previous/'summary.json').read_text());ancestor=R/old['previous_checkpoint'];ancestor_state=json.loads((ancestor/'summary.json').read_text())
            if old['previous_checkpoint']:
                prediction=out/f'prediction{workers:03d}'
                result=run('rl/offline_tomato_withdrawal_predictor.py',['--previous',str(previous),'--depth-mm',str(target),'--output',str(prediction)],prediction.name)
                if result.returncode:raise RuntimeError('predictor_refused')
                resume=prediction
            for chunk in range(min(12,a.workers-workers)):
                tag=f'attempt{workers:03d}_{chunk:02d}';folder=out/tag;args=['--depth-mm',str(target),'--previous',str(previous),'--output',str(folder)]
                if resume:args+=['--resume',str(resume)]
                result=run('rl/offline_tomato_triangle_withdrawal.py',args,tag);workers+=1
                record={'output':str(folder.relative_to(R)),'depth_mm':target,'returncode':result.returncode};records.append(record)
                if result.returncode:stop='worker_resource_or_solver_stop';break
                if (folder/'summary.json').exists():
                    s=json.loads((folder/'summary.json').read_text());record.update({k:s[k] for k in ['passed','flags','runtime_s','peak_rss_bytes','withdrawal_relative_energy_residual','damaged_patches','completely_failed_patches']});flags=s['flags']
                    if s['passed']:
                        audit=out/(tag+'_audit.json');result=run('rl/audit_tomato_triangle_withdrawal.py',['--checkpoint',str(folder),'--output',str(audit)],tag+'_audit')
                        if result.returncode or not json.loads(audit.read_text())['passed']:stop='independent_audit_failed'
                        else:accepted=folder
                    print(record,flush=True);break
                s=json.loads((folder/'candidate.json').read_text());assert s['optimization_only'] and not s['passed'];resume=folder
                record.update({'optimization_only':True,'runtime_s':s['runtime_s'],'peak_rss_bytes':s['peak_rss_bytes']});print(record,flush=True)
            if accepted:
                previous=accepted;depth=target;level=0
                if depth<=a.target_mm:stop='requested_depth_reached'
                target=max(a.target_mm,depth-a.step_mm)
            elif flags and set(flags)<=set(['contact','cumulative_work_balance','incremental_work_balance','withdrawal_work_balance']) and level<10:
                level+=1;target=(depth+target)/2
            elif not stop:stop='bounded_optimization_budget'
            status={'last_accepted':str(previous.relative_to(R)),'last_accepted_depth_mm':depth,'target_mm':a.target_mm,'workers':workers,'records':records,'stop_reason':stop,'runtime_s':time.monotonic()-start,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
            (out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    except Exception as e:stop=str(e)
    status={'last_accepted':str(previous.relative_to(R)),'last_accepted_depth_mm':depth,'target_mm':a.target_mm,'workers':workers,'records':records,'stop_reason':stop or 'bounded_worker_budget','runtime_s':time.monotonic()-start,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
    (out/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(status,flush=True)
