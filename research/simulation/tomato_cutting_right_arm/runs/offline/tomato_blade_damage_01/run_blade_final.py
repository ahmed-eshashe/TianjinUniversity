import subprocess,os,json
from pathlib import Path
r=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');f=r/'runs/offline/tomato_blade_damage_01'
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
test=subprocess.run([str(r/'.venv-native/bin/python'),'/tmp/test_blade_damage.py'],cwd=r,env=env,text=True,capture_output=True,timeout=60)
(f/'tests.log').write_text(test.stdout+test.stderr)
if test.returncode:raise SystemExit('Regression failed')
sequences={'insertion_final':('contact',[i*.25 for i in range(17)]),'miss_final':('miss',[0,4])}
for name,(mode,depths) in sequences.items():
 previous=None
 for i,depth in enumerate(depths):
  out=f/name/f'{i:02}';out.parent.mkdir(exist_ok=True)
  args=[str(r/'.venv-native/bin/python'),'rl/offline_tomato_blade_damage.py','--depth-mm',str(depth),'--mode',mode,'--output',str(out)]
  if previous:args+=['--previous',str(previous)]
  guess=f/'before_redundancy_fix_insertion_final'/f'{i:02}'/'positions.npy'
  if name=='insertion_final' and guess.exists():args+=['--guess',str(guess)]
  result=subprocess.run(args,cwd=r,env=env,capture_output=True,text=True,timeout=60)
  (out.parent/f'{i:02}.log').write_text(result.stdout+result.stderr);print(name,i,result.returncode,result.stdout,result.stderr,flush=True)
  if result.returncode:break
  summary=json.loads((out/'summary.json').read_text())
  if not summary['passed']:break
  previous=out
 print('SEQUENCE END',name,flush=True)
print('COMPLETE',flush=True)
