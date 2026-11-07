import sys,json,subprocess
from pathlib import Path
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'rl'))
from tomato_isaac_startup_guard import supervise
for mode in ['tangent_fine_short','tangent_finest_short']:
 result=supervise(R/'runs/native'/f'{mode}_20261102_01',mode=mode)
 print(json.dumps(result),flush=True)
 if not result['passed']:raise SystemExit(1)
result=subprocess.run([str(R/'.venv-native/bin/python'),str(R/'work/integration_20261102/compare_tangent_time_levels.py'),'--output',str(R/'runs/offline/tangent_time_screen_20261102_01')],check=False)
raise SystemExit(result.returncode)
