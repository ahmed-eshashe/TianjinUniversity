"""Serial new-trajectory preflight; no old-contact state/work can be imported."""
import argparse,json,os,subprocess,time,fcntl
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent;G=R/'runs/offline/tomato_contact_continuation_01'
p=argparse.ArgumentParser();p.add_argument('--target-mm',type=float,default=4.);p.add_argument('--name',default='evolving_preflight');p.add_argument('--previous',type=Path);p.add_argument('--step-mm',type=float,default=.25);p.add_argument('--predict',action='store_true');a=p.parse_args()
if not 0<a.step_mm<=.25:raise ValueError('Step must be in (0, 0.25] mm')
if not 0<a.target_mm<=48:raise ValueError('Invalid target')
gate=json.loads((G/'spectral_static_probe_status.json').read_text());last=R/gate['last_accepted'];s=json.loads((last/'summary.json').read_text())
assert s['passed'] and s['depth_mm']>=8.125
assert json.loads((G/(last.name+'_audit.json')).read_text())['passed']
for n in ['tests.json','continuation_surface/summary.json','continuation_energy180.json','continuation_energy360.json']:
 assert json.loads((G/n).read_text())['passed'],n
if a.target_mm>4:assert json.loads((G/'fracture_refinement.json').read_text())['passed']
assert json.loads((F/'cleared_reclosure_qualification.json').read_text())['passed'],'Withdrawal/reclosure gate not passed'
assert a.previous is not None,'Continue a qualified insertion branch; do not concatenate unloading states'
parent_lock=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
folder=F/a.name;folder.mkdir(exist_ok=False);records=[];previous=a.previous.resolve() if a.previous else None;depth=json.loads((previous/'summary.json').read_text())['depth_mm'] if previous else 0.;target=min(depth+a.step_mm,a.target_mm) if previous else 0.;level=0;start=time.monotonic();workers=0;stop=None
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
def guarded_run(*args,**kwargs):
    now=datetime.now(timezone.utc)
    if (datetime(2026,10,26,4,54,40,tzinfo=timezone.utc)-now).total_seconds()<65:raise RuntimeError('hard_deadline')
    q=json.loads((F/'quota_lease.json').read_text());age=(now-datetime.fromisoformat(q['checked_utc'])).total_seconds()
    if not 0<=age<=480:raise RuntimeError('quota_lease_expired_or_invalid')
    if q['maximum_reported_used_percent']>=45:raise RuntimeError('quota_margin_stop')
    return subprocess.run(*args,**kwargs)
while workers<12:
    resume=None;accepted=None;flags=None
    if a.predict and previous:
        prediction=folder/f'prediction{len(records):03d}'
        result=guarded_run([str(R/'.venv-native/bin/python'),'rl/offline_tomato_evolution_predictor.py','--previous',str(previous),'--depth-mm',str(target),'--output',str(prediction)],cwd=R,env=ENV,capture_output=True,text=True,timeout=60)
        (folder/(prediction.name+'.log')).write_text(result.stdout+result.stderr)
        if result.returncode==0:resume=prediction
    for chunk in range(12):
        tag=f'attempt{len(records):03d}_{chunk:02d}';out=folder/tag
        cmd=['rl/offline_tomato_triangle_evolution.py','--depth-mm',str(target),'--output',str(out)]
        if previous:cmd+=['--previous',str(previous)]
        if resume:cmd+=['--resume',str(resume)]
        workers+=1
        result=guarded_run([str(R/'.venv-native/bin/python'),*cmd],cwd=R,env=ENV,capture_output=True,text=True,timeout=60)
        (folder/(tag+'.log')).write_text(result.stdout+result.stderr)
        rec={'depth_mm':target,'chunk':chunk,'returncode':result.returncode,'output':str(out.relative_to(R))}
        if result.returncode:stop='worker_refused_or_resource_or_solver_stop';records.append(rec);break
        if (out/'summary.json').exists():
            s=json.loads((out/'summary.json').read_text());rec.update({k:s[k] for k in ['passed','flags','runtime_s','peak_rss_bytes','relative_energy_residual','damaged_patches','completely_failed_patches']})
            flags=s['flags'];records.append(rec);print(rec,flush=True)
            if s['passed']:
                result=guarded_run([str(R/'.venv-native/bin/python'),'rl/audit_tomato_triangle_evolution.py','--checkpoint',str(out),'--output',str(folder/(tag+'_audit.json'))],cwd=R,env=ENV,capture_output=True,text=True,timeout=60)
                (folder/(tag+'_audit.log')).write_text(result.stdout+result.stderr)
                if result.returncode or not json.loads((folder/(tag+'_audit.json')).read_text())['passed']:stop='independent_audit_failed'
                else:accepted=out
            break
        s=json.loads((out/'candidate.json').read_text());assert s['optimization_only'] and not s['passed'];resume=out
        rec.update({'optimization_only':True,'runtime_s':s['runtime_s'],'peak_rss_bytes':s['peak_rss_bytes']});records.append(rec);print(rec,flush=True)
        if workers>=12:stop='bounded_worker_budget';break
    if accepted:
        previous=accepted;depth=target;level=0
        if depth>=a.target_mm:stop='requested_preflight_depth_reached'
        target=min(depth+a.step_mm,a.target_mm)
    elif flags and set(flags)<=set(['contact','cumulative_work_balance','incremental_work_balance']) and previous and level<10:
        level+=1;target=(depth+target)/2
    elif stop is None:stop='unaccepted_endpoint_or_optimization_budget'
    report={'last_accepted':str(previous.relative_to(R)) if previous else None,'last_accepted_depth_mm':depth,'target_depth_mm':a.target_mm,'initial_checkpoint':str(a.previous) if a.previous else None,'maximum_base_step_mm':a.step_mm,'positions_only_predictor_enabled':a.predict,'stop_reason':stop,'records':records,
            'workers':workers,'runtime_s':time.monotonic()-start,'fresh_undamaged_trajectory':True,'validation_branches_separate':True,'withdrawal_trajectory_concatenated':False,'old_contact_states_used':False,'independent_release_validated':False,'full_cut':False,'simulator':False,'training':False}
    (folder/'status.json').write_text(json.dumps(report,indent=2)+'\n')
    if stop:break
if workers>=12 and report['stop_reason'] is None:
    report['stop_reason']='bounded_worker_budget'
    (folder/'status.json').write_text(json.dumps(report,indent=2)+'\n')
print(report,flush=True)
