from pathlib import Path
import json,hashlib
from tomato_isaac_startup_guard import supervise
R=Path(__file__).resolve().parents[2];screen=R/'runs/native/load_twist_screen_20261102_01';p=screen/'hold_measurements.json';result=json.loads((screen/'supervisor_result.json').read_text());d=json.loads(p.read_text())
if not result['passed']or not result['worker'].get('loaded_scene_screen_passed')or result['worker'].get('load_case')!='lateral_twist':raise ValueError('Qualified short lateral/twisting screen required')
rate=max(ep['wall_s']/ep['steps']for ep in d['episodes']);budget=dict(maximum_measured_screen_wall_s_per_matched_step=rate,linear_5280_step_estimate_s=rate*5280,watchdog_wall_s=10800,allowance='Full pulse reaches over three times the screen load and includes one-second transient observation; up to six times the short-screen extrapolation is available, with live numerical/geometry/resource stops and checkpoint logging.',screen=str(p),screen_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Bounded synthetic loading only; no actual blade contact or training throughput estimate.')
(R/'work/integration_20261102/load_twist_budget_01.json').write_text(json.dumps(budget,indent=2)+'\n');answer=supervise(R/'runs/native/load_twist_20261102_01',mode='load_twist',wall_s=10800);print(json.dumps(answer,indent=2));raise SystemExit(0 if answer['passed']else 1)
