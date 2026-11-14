"""Sequential, resumable physical demonstration collection; one Isaac worker."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import time

W = Path(__file__).resolve().parent
PYTHON = '/home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python'
a = argparse.ArgumentParser()
a.add_argument('--ids', nargs='+', required=True)
a.add_argument('--tag', default='teacher_v01')
a.add_argument('--record', action='store_true')
a.add_argument('--render', action='store_true')
a.add_argument('--policy', type=Path)
a.add_argument('--scene', type=Path)
a.add_argument('--physics-hz', type=int, default=1920)
a.add_argument('--manifest', type=Path, default=W/'curriculum_split_v01.json')
a.add_argument('--vision-ablation', choices=['none', 'blank'], default='none')
args = a.parse_args()
assert not (args.record and args.policy), 'Keep teacher demonstrations separate from student evaluation'
manifest = json.loads(args.manifest.read_text())
episodes = {x['id']: x for x in manifest['episodes']}
out = W / 'datasets' / args.tag
out.mkdir(parents=True, exist_ok=True)
results = []
failures = 0
for case in args.ids:
    item = episodes[case]
    episode = out / case
    if episode.exists():
        print('PRESERVED existing', episode, flush=True)
        continue
    command = [PYTHON, '-u', str(W / 'hybrid_pickup_v06.py'), '--output', str(episode),
               '--scene', str(args.scene.resolve() if args.scene else W / item['scene']), '--grasp', str(W / 'reports/pinch_geometry02.json'),
               '--neutral-start', str(W / 'reports/neutral_start.json'),
               '--close-seconds', '6.', '--joint-space-approach', '--vision-ablation', args.vision_ablation, '--compliant', '--thumb-effort', '.65', '--finger-effort', '.10', '--hand-damping', '3',
               '--solver', '0', '--velocity-iterations', '4', '--physics-hz', str(args.physics_hz),
               '--lift', '.12', '--lift-seconds', '5', '--hold-seconds', '6', '--control-hz', '20',
               '--dx', str(item['dx']), '--dy', str(item['dy']), '--yaw-deg', str(item['yaw_deg'])]
    if args.record:
        command.append('--record-demo')
    if args.render:
        command.append('--render')
    if args.policy:
        command += ['--policy', str(args.policy.resolve()), '--vision-ablation', args.vision_ablation]
    (out / 'collection_progress.json').write_text(json.dumps(dict(current=case, completed=results)))
    started = time.monotonic()
    with (out / (case + '.log')).open('w') as log:
        process = subprocess.run(command, cwd=W, env={**os.environ, 'OPENBLAS_NUM_THREADS':'1',
                                 'PYTHONDONTWRITEBYTECODE':'1'}, stdout=log, stderr=subprocess.STDOUT)
    result = json.loads((episode / 'result.json').read_text()) if (episode / 'result.json').exists() else {}
    success = bool(result.get('success')) and process.returncode == 0
    row = dict(id=case, split=item['split'], success=success, elapsed_s=time.monotonic()-started)
    if success:
        row.update(slip_m=result['last'].get('slip_m'), min_height_m=result['last']['minimum_tool_height_m'])
    else:
        failures += 1
        row['failure'] = (episode / 'failure.txt').read_text()[-1400:] if (episode / 'failure.txt').exists() else 'No sustained unsupported hold'
    results.append(row)
    print(json.dumps(row), flush=True)
    (out / 'collection_progress.json').write_text(json.dumps(dict(current=None, completed=results), indent=2))
    subprocess.run([PYTHON, str(W / 'publish_current_pickup.py')], cwd=W, check=True)
    if failures >= 2:
        print('Stopped collection after two failures: inspect physical coverage before continuing.', flush=True)
        break
(out / ('collection_' + time.strftime('%Y%m%d_%H%M%S') + '.json')).write_text(json.dumps(results, indent=2))
