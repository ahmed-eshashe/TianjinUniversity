from pathlib import Path
import subprocess,os,json
r=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');f=r/'runs/offline/tomato_blade_damage_01/patch_energy';f.mkdir(exist_ok=True)
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
for steps in [2400,4800]:
 for start in range(0,47,8):
  out=f/f'{steps}_{start:02}.json'
  result=subprocess.run([str(r/'.venv-native/bin/python'),'rl/offline_tomato_blade_energy.py','--start',str(start),'--count',str(min(8,47-start)),'--steps',str(steps),'--output',str(out)],cwd=r,env=env,text=True,capture_output=True,timeout=60)
  out.with_suffix('.log').write_text(result.stdout+result.stderr);print(steps,start,result.returncode,result.stdout,result.stderr,flush=True)
  if result.returncode:raise SystemExit(1)
print('COMPLETE',flush=True)
