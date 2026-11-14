from pathlib import Path
import subprocess,os,time,json
w=Path(__file__).resolve().parent;r=w.parents[1]
while not (w/'robo_straight_0.8_result.json').exists():time.sleep(2)
time.sleep(3)
env=os.environ.copy();env.update(PYTHONPATH=str(r/'rl'),DISPLAY=':1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONUNBUFFERED='1')
start=time.monotonic()
with (w/'profile2.log').open('w') as f:
 try:
  p=subprocess.run([str(r/'.venv-native/bin/python'),str(w/'profile_worker2.py'),'--output',str(w/'current_profile2'),'--headless','--resume-checkpoint',str(r/'work/single_slice_20261106/robot_cut17/checkpoints/step_006400.npz')],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
  result={'returncode':p.returncode}
 except subprocess.TimeoutExpired:result={'timeout':True}
result['wall_s']=time.monotonic()-start;(w/'profile2_launch.json').write_text(json.dumps(result))
