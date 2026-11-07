"""Bounded sequential native comparisons after clean production checkpoint pause."""
from pathlib import Path
import subprocess,os,time,json
w=Path(__file__).parent;r=w.parents[1]
while not (w/'robot_cut17/supervisor_result.json').exists():time.sleep(5)
report=json.loads((w/'bodyward_timestep_comparison/report.json').read_text())
assert all(c['passed'] for c in report['cases'] if c['candidate']!='original')
cp=w/'robot_cut17/checkpoints/step_006400.npz'
for stride,count in [(1,32),(4,8)]:
 out=w/f'coupling_timestep_stride{stride}'
 env=os.environ.copy();env.update(DISPLAY=':1',TOMATO_COMPARISON_STRIDE=str(stride))
 with (w/f'coupling_timestep_stride{stride}.log').open('w') as log:
  result=subprocess.run([str(r/'.venv-native/bin/python'),str(r/'rl/tomato_coupling_timestep_comparison_guard.py'),'--output',str(out),'--wall-seconds','1800','--cut-steps',str(6401+count),'--headless','--resume-checkpoint',str(cp)],env=env,stdout=log,stderr=subprocess.STDOUT)
 print(stride,result.returncode,flush=True)
 if (out/'worker_failure.json').exists() or not (out/'cutting_result.json').exists():raise RuntimeError('Bounded comparison did not finish')
