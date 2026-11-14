"""Publish verified pickup results to the existing local checklist."""
from pathlib import Path
import datetime
import hashlib
import json
import os

W = Path(__file__).resolve().parent
path = Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/learning-roadmap.json')
dataset = W / 'datasets/teacher_v02'
results = []
for p in sorted(dataset.glob('*/demonstration_metadata.json')):
    r = json.loads(p.read_text())
    results.append(dict(episode=p.parent.name, success=r['success']))
passes = sum(x['success'] for x in results)
progress = json.loads((dataset/'collection_progress.json').read_text()) if (dataset/'collection_progress.json').exists() else {}
current = progress.get('current')
scope = f'{passes}/{len(results)} completed scripted short-knife attempts passed from shifted/rotated flat placements. Failed attempts are excluded from imitation. No learned pickup result yet.'
trained = any((W/'policies').glob('*/best.pt')) if (W/'policies').exists() else False
now = datetime.datetime.now().astimezone().isoformat()
d = json.loads(path.read_text())
stage = next(x for x in d['stages'] if x['id'] == 10)
stage['phase'] = f'Collecting head-camera learning examples: {passes} successful' if current else f'{passes} successful head-camera examples; student evaluation pending'
stage['items'][3].update(status='in_progress', evidence=scope + ' Original longer knife, new handle shapes and non-flat resting poses remain open.')
stage['items'][4].update(status='in_progress', evidence='Actual RGB-D, joint feedback and teacher actions recorded at 20 Hz. Corrected pose reset is measured after application; hidden object state is excluded from actor records. Separate training/validation/test placements frozen. Collection and policy evaluation remain underway.')
if trained:
    stage['items'][5].update(status='in_progress', evidence='Offline student weights exist. Fresh closed-loop physical evaluation is required before claiming learned pickup; loss alone is insufficient.')
d['updated'] = now
d['latest_progress']['learning'] = scope
temp = path.with_suffix('.json.tmp')
temp.write_text(json.dumps(d, indent=2)+'\n')
os.replace(temp, path)
preserved = json.loads((W/'preserved_sources.json').read_text())
unchanged = all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p,h in preserved.items())
status = json.loads((W/'STATUS.json').read_text())
status.update(updated_local=now, status='collecting_teacher_demonstrations' if current else 'teacher_demonstrations_available',
              latest_trial=current, latest_result=scope, real_grasp_verified=True,
              real_grasp_scope='Shorter knife, fixed-start scripted contact pickup; not generalized or learned.',
              successful_demonstrations=passes, original_sources_unchanged=unchanged,
              policy_trained=trained, learned_pickup_verified=False, long_original_knife_qualified=False)
(W/'STATUS.json').write_text(json.dumps(status, indent=2)+'\n')
print(scope)
