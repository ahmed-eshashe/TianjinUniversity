"""Read-only active-test disposition. Never reruns or clears a task/quota wait."""
import datetime as dt
import hashlib
import json
from pathlib import Path
from tomato_preparation_runner import sha,quota_receipt_ok


def inspect_active(root,evidence,*,fresh_quota,now):
    root=Path(root).resolve();evidence=Path(evidence).resolve()
    quota_receipt_ok(fresh_quota,now)
    s=json.loads((evidence/'session.json').read_text());active=s.get('active_task')
    if active is None:return {'status':'no_active_task','rerun_authorized':False,'files_modified':False}
    path=Path(active['result_path'])
    if not path.is_relative_to(evidence) or path.is_symlink():raise ValueError('Owned result path required')
    if not path.exists():return {'status':'missing_result_preserve_active','rerun_authorized':False,'files_modified':False}
    try:
        if path.stat().st_size>4*1024**2:raise ValueError('Result too large')
        report=json.loads(path.read_text())
    except (OSError,ValueError):return {'status':'partial_result_preserve_active','rerun_authorized':False,'files_modified':False}
    if report.get('label')!=active['label'] or report.get('group')!=active['id'] or report.get('runner_sha256')!=active['runner_sha256']:
        raise ValueError('Active/result identity mismatch')
    snapshot=report.get('source_snapshot')
    if not isinstance(snapshot,dict) or not snapshot:raise ValueError('Full source snapshot absent')
    h=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
    if h!=report.get('source_snapshot_sha256') or h!=active.get('source_snapshot_sha256'):raise ValueError('Snapshot binding mismatch')
    if sha(root/'rl/tomato_preparation_runner.py')!=report['runner_sha256']:raise ValueError('Runner changed after batch')
    for relative,digest in snapshot.items():
        p=root/relative
        if Path(relative).is_absolute() or '..' in Path(relative).parts or p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root) or sha(p)!=digest:raise ValueError('Changed/outside/missing source snapshot entry')
    if report.get('quota_before_receipt_sha256')!=active.get('quota_before_receipt_sha256'):raise ValueError('Before-quota binding mismatch')
    if now<dt.datetime.fromisoformat(report['started_utc']):raise ValueError('Quota reconciliation precedes batch')
    if report.get('forbidden_imports') or report.get('native_runtime_validated') is not False:raise ValueError('Unexpected native/import claim')
    status='passed_result_requires_recorded_disposition' if report.get('passed') is True else 'failed_result_review_required'
    return {'status':status,'result_sha256':sha(path),'source_snapshot_sha256':h,
        'rerun_authorized':False,'files_modified':False,'fresh_quota_checked_utc':fresh_quota['checked_utc']}
