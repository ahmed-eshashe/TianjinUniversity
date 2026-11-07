from pathlib import Path
import json,hashlib
from tomato_isaac_startup_guard import supervise
R=Path(__file__).resolve().parents[2];screen=R/'runs/native/prepared_scene_device_screen_20261102_02';p=screen/'hold_measurements.json';result=json.loads((screen/'supervisor_result.json').read_text());d=json.loads(p.read_text())
if not result['passed']or not result['worker'].get('prepared_scene_device_screen_passed'):raise ValueError('Qualified synchronized screen required')
rate=max(ep['wall_s']/ep['steps']for ep in d['episodes']);budget=dict(warm_screen_maximum_wall_s_per_matched_step=rate,expected_48000_step_wall_s=rate*48000,watchdog_wall_s=3600,allowance='About three times the measured short-run extrapolation plus setup; full run remains independently monitored and checkpointed.',source_screen=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Cost estimate for an unloaded prepared hold only. Not loaded contact, cut or training throughput.')
(R/'work/integration_20261102/prepared_scene_hold_budget_01.json').write_text(json.dumps(budget,indent=2)+'\n')
answer=supervise(R/'runs/native/prepared_scene_device_hold_20261102_01',mode='prepared_scene_device_hold',wall_s=3600);print(json.dumps(answer,indent=2));raise SystemExit(0 if answer['passed']else 1)
