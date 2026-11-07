import sys,json
from pathlib import Path
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'rl'))
from tomato_isaac_startup_guard import supervise
for mode in ['block_preconditioner','block_integrator','block_short','block_duration','failed_frame']:
 result=supervise(R/'runs/native'/f'{mode}_20261102_01',mode=mode)
 print(json.dumps(result),flush=True)
 if not result['passed']:break
