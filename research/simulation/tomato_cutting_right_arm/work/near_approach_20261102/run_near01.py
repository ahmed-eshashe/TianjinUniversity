from pathlib import Path
import json
from tomato_isaac_startup_guard import supervise
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
assert json.loads((R/'runs/offline/near_approach_plan_20261102_02/measurements.json').read_text())['host_preflight_passed']
print(supervise(R/'runs/native/near_approach_20261102_01',mode='near_approach',wall_s=600),flush=True)
