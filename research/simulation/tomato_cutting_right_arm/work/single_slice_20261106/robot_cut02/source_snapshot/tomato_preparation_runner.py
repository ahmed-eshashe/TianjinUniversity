"""Fixed-suite serial offline runner. Actual quota tools remain mandatory outside.

A receipt is bookkeeping, not an authenticated account API response. The caller
must obtain actual bounded usage before AND after each invocation. This runner
never imports native engines or executes an arbitrary test module.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time
import unittest

GROUPS={
 'integrity':(['test_tomato_evidence_bundle','test_tomato_journal_verify','test_tomato_staged_evaluator','test_tomato_preparation_runner','test_tomato_preparation_reconcile'],0),
 'learning':(['test_tomato_learning_contract','test_tomato_learning_episode'],0),
 'native_source':(['test_tomato_native_worker','test_tomato_native_step','test_tomato_coupon_segment','test_tomato_segment_metadata','test_tomato_kinematic_interval','test_tomato_reaction_metadata'],0),
 'contact_geometry':(['test_tomato_contact_coverage','test_tomato_sdf_diagnostics','test_tomato_two_piece_coupon'],0),
 'supervision':(['test_tomato_resource_supervisor','test_tomato_preupgrade_guard'],0),
 'cohesive_patch':(['test_tomato_cohesive_adapter_reference'],6),
 'cohesive_evolution':(['test_tomato_cohesive_evolution_reference'],12),
 'cohesive_assembly':(['test_tomato_cohesive_assembly'],4),
}


def utc(text):return dt.datetime.fromisoformat(text.replace('Z','+00:00'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def atomic(path,value):
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)


def quota_receipt_ok(receipt,now):
    checked=utc(receipt['checked_utc'])
    if checked.utcoffset()!=dt.timedelta(0) or not 0<=(now-checked).total_seconds()<=30:raise ValueError('Fresh actual-tool receipt required (<=30 seconds)')
    windows=receipt.get('windows')
    if not isinstance(windows,list) or not windows:raise ValueError('Reported quota window required; missing windows remain unknown')
    for w in windows:
        used=w.get('usedPercent')
        if type(used) not in (int,float) or not math.isfinite(used) or not 0<=used<45:raise ValueError('Quota stop or unreadable window')
    return True


def run(root,evidence,*,group,label,receipt_path,session_start_utc):
    if group not in GROUPS or not label or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in label):raise ValueError('Fixed group and fresh safe label required')
    root=Path(root).resolve();evidence=Path(evidence).resolve()
    if not evidence.is_relative_to(root/'runs/offline'):raise ValueError('Preparation evidence root required')
    now=dt.datetime.now(dt.timezone.utc);session=json.loads((evidence/'session.json').read_text())
    if now>=utc(session['computational_stop_utc']) or now>=utc(session_start_utc)+dt.timedelta(seconds=180):raise ValueError('Insufficient reserved worker/session margin')
    if session.get('active_task') is not None:raise ValueError('Reconcile saved active task before another batch')
    if any(os.environ.get(k)!='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')):raise ValueError('One-thread environment required')
    receipt_path=Path(receipt_path);receipt=json.loads(receipt_path.read_text());quota_receipt_ok(receipt,now)
    output=evidence/(label+'_tests.json')
    if output.exists():raise ValueError('Used result label refuses rerun')
    locks=[]
    for name in ('logs/offline_overnight.lock','logs/right_arm_control.lock'):
        handle=(root/name).open('a');fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(handle)
    for name,base in [('baseline_sources.json',root),('new_sources.json',root),('artifact_hashes.json',evidence)]:
        for file,digest in json.loads((evidence/name).read_text()).items():
            if sha(base/file)!=digest:raise ValueError('Source/artifact mismatch: '+file)
    # Exclusive receipt-use marker prevents accidentally reusing one probe twice.
    marker=evidence/('quota_receipt_used_'+sha(receipt_path))
    with marker.open('x') as f:f.write(label+'\n')
    snapshot={str(p.relative_to(root)):sha(p) for p in sorted((root/'rl').glob('*.py'))}
    for m in GROUPS[group][0]:
        p=root/'rl/tests'/(m+'.py');snapshot[str(p.relative_to(root))]=sha(p)
    snapshot_hash=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
    session['active_task']={'source_snapshot_sha256':snapshot_hash,'quota_before_receipt_sha256':sha(receipt_path),'id':group,'label':label,'started_utc':now.isoformat(),'result_path':str(output),'status':'testing','runner_sha256':sha(Path(__file__))}
    atomic(evidence/'session.json',session)
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    sys.path[:0]=[str(root/'rl'),str(root/'rl/tests')]
    modules,calls=GROUPS[group]
    stream=io.StringIO();started=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(m) for m in modules))
    forbidden=sorted(k for k in sys.modules if k.split('.')[0] in {'isaacsim','isaaclab','newton','warp','torch','omni','pxr'})
    report={'label':label,'source_snapshot':snapshot,'source_snapshot_sha256':snapshot_hash,'group':group,'started_utc':now.isoformat(),'tests':result.testsRun,'passed':result.wasSuccessful() and not forbidden,
        'output':stream.getvalue(),'elapsed_s':time.monotonic()-started,'mechanical_calls_budget':calls,
        'native_runtime_validated':False,'forbidden_imports':forbidden,'runner_sha256':sha(Path(__file__)),
        'quota_before_receipt_sha256':sha(receipt_path),'quota_after_required':True,
        'test_source_sha256':{m:sha(root/'rl/tests'/(m+'.py')) for m in modules}}
    with output.open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
    # Leave active_task until caller records actual after-quota and reconciles
    # exact saved result/source hashes. No automatic retry or acceptance.
    print(json.dumps({k:v for k,v in report.items() if k!='output'}))
    return 0 if report['passed'] else 1


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('root','evidence','group','label','receipt','session-start-utc'):p.add_argument('--'+name,required=True)
    a=p.parse_args();raise SystemExit(run(a.root,a.evidence,group=a.group,label=a.label,receipt_path=a.receipt,session_start_utc=a.session_start_utc))
if __name__=='__main__':main()
