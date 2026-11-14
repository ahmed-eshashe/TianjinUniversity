"""One explicitly unqualified opposite-face probe, after frozen pickup evaluation."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time

W = Path(__file__).resolve().parent
assert json.loads((W / 'reports/hybrid_v07_campaign.json').read_text())['limited_curriculum_physical_gate_passed']
source = W / 'datasets/hybrid_v07_validation/recovery_validation_000/configuration.json'
settings = json.loads(source.read_text())['args']
out = W / 'datasets/rest_pose_probe_v01/opposite_face_000'
assert not out.exists(), 'Preserve previous evidence; do not overwrite an episode'
out.parent.mkdir(parents=True, exist_ok=True)
settings['output'] = str(out)
settings['rest_roll_deg'] = 180.0
command = [sys.executable, '-u', str(W / 'hybrid_rest_probe_v01.py')]
for key, value in settings.items():
    flag = '--' + key.replace('_', '-')
    if isinstance(value, bool):
        if value:
            command.append(flag)
    elif value is not None:
        command += [flag, str(value)]
(out.parent / 'command.json').write_text(json.dumps(command, indent=2))
start = time.monotonic()
with (out.parent / 'opposite_face_000.log').open('w') as log:
    completed = subprocess.run(command, cwd=W, stdout=log, stderr=subprocess.STDOUT,
                               env={**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
result = json.loads((out / 'result.json').read_text()) if (out / 'result.json').exists() else {}
failure = (out / 'failure.txt').read_text() if (out / 'failure.txt').exists() else ''
summary = dict(success=bool(result.get('success')) and completed.returncode == 0,
               elapsed_s=time.monotonic() - start, returncode=completed.returncode,
               failure=failure.splitlines()[-1] if failure else None,
               scope='One opposite-face probe; no retraining, changed grip or general rest-pose qualification.')
(W / 'reports/hybrid_v07_rest_probe.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary), flush=True)
