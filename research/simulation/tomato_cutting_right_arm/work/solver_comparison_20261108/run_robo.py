from pathlib import Path
import time,subprocess,os,json
w=Path(__file__).resolve().parent
while not (w/'disect_exit.json').exists():time.sleep(5)
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONUNBUFFERED='1')
results=[]
for path,scale in [('straight',1),('curved',1),('straight',.8)]:
 label=f'robo_{path}_{scale:g}'
 with (w/f'{label}.log').open('w') as f:
  try:
   p=subprocess.run([str(w/'env311/bin/python'),str(w/'robo_benchmark.py'),'--path',path,'--scale',str(scale)],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
   results.append({'case':label,'returncode':p.returncode})
  except subprocess.TimeoutExpired:results.append({'case':label,'timeout':True})
 (w/'robo_exits.json').write_text(json.dumps(results,indent=2))
 if results[-1].get('returncode')!=0:break
