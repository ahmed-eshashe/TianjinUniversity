"""Verify saved evidence and journal a session; never starts a worker."""
import fcntl, hashlib, json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
SESSION = Path(__file__).parent

def read(path):
    return json.loads(path.read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

label = sys.argv[1]
assert label.isalnum()
state = read(SESSION / 'session.json')
assert state.get('status') != 'needs_failure_review', 'Unresolved physical failure requires stop/review'
now = datetime.now(timezone.utc)
assert now < datetime.fromisoformat(state['deadline_utc'])
locks = []
for name in ['offline_overnight.lock', 'right_arm_control.lock']:
    handle = (ROOT / 'logs' / name).open('a')
    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    locks.append(handle)
for name, sha in read(SESSION / 'source_snapshot.json').items():
    assert digest(ROOT / name) == sha, name
physical = ROOT / state['last_accepted']
summary = read(physical / 'summary.json')
audit_path = physical.parent / (physical.name + '_audit.json')
assert summary['passed'] and read(audit_path)['passed']
for name, sha in summary['source_hashes'].items():
    assert digest(ROOT / name) == sha, name
for name, sha in summary['state_hashes'].items():
    assert digest(physical / name) == sha, name
qualification_path = ROOT / 'runs/offline/tomato_global_search_01/refinement_qualification.json'
qualification = read(qualification_path)
assert qualification['passed']
assert qualification['last_accepted']['checkpoint'] == state['last_accepted']
assert qualification['source_of_qualification_sha256'] == digest(ROOT / 'runs/offline/tomato_curvature_search_01/qualification.json')
lease = read(SESSION / 'quota_lease.json')
assert 0 <= (now - datetime.fromisoformat(lease['checked_utc'])).total_seconds() <= 480
assert lease['maximum_reported_used_percent'] < 45
metrics = {key: summary[key] for key in ['depth_mm', 'swept_blade_minimum_gap_m', 'force_residual', 'relative_energy_residual', 'minimum_softening_stability_eigenvalue', 'completely_failed_patches', 'damaged_patches', 'topology', 'peak_rss_bytes']}
report = {'checked_utc': now.isoformat(), 'last_accepted': state['last_accepted'], 'next_target_mm': state['target_mm'], 'pending_candidate': state.get('pending_candidate'), 'summary_sha256': digest(physical / 'summary.json'), 'audit_sha256': digest(audit_path), 'qualification_sha256': digest(qualification_path), 'metrics': metrics, 'both_locks_free': True, 'numerical_workers_exited': True, 'reported_quota_used_percent': lease['maximum_reported_used_percent'], 'secondary_window': 'unknown', 'full_cut': False, 'independent_release': False}
state.update(status='waiting_for_scheduled_continuation', active_batch=None, last_saved_handoff=label + '_handoff.json', latest_metrics=metrics)
(SESSION / 'session.json').write_text(json.dumps(state, indent=2) + '\n')
(SESSION / (label + '_handoff.json')).write_text(json.dumps(report, indent=2) + '\n')
with (ROOT / 'docs/rl/OVERNIGHT_PROGRESS.md').open('a') as output:
    output.write('\n## Qualified session ' + label + ' — ' + now.isoformat() + '\n\n' + json.dumps(report) + '\n\nNEXT: read session.json for actual accepted predecessor, exact target and pending candidate. Verify source manifest and fresh UTC/quota/locks. The source-hashed heartbeat_driver.js runs only inside functions.exec (read source then await eval async wrapper); it uses recorded dated runners and next free indices. Afterward run recorded qualifier with one numerical thread and timeout60; then run this source-hashed finish_session.py with a fresh alphanumeric label to verify saved state/source/audit/qualification and write handoff. All physical laws/thresholds/controllers/caps remain unchanged. Fullcut/release unvalidated. Final session time and absolute deadline are recorded in session.json.\n')
print(json.dumps({'checkpoint':state['last_accepted'], 'depth_mm':summary['depth_mm'], 'next_target_mm':state['target_mm'], 'quota_remaining_percent':100-lease['maximum_reported_used_percent'], 'both_locks_free':True}))
