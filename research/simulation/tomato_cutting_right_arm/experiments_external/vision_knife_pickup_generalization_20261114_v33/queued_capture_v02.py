from pathlib import Path
import os,sys,time,subprocess,json
import psutil
W=Path(__file__).resolve().parent
wait=[]
for p in psutil.process_iter(['pid','cmdline']):
 c=p.info['cmdline'] or []
 if any(Path(x).name=='run_curriculum_v33.py' for x in c) and 'v13_teacher_matrix' in c:wait.append(p)
print('Waiting for teacher batch:',[p.pid for p in wait],flush=True)
for p in wait:
 try:p.wait()
 except psutil.NoSuchProcess:pass
while not (W/'extra_training_curriculum_v02.json').exists():time.sleep(2)
(W/'reports/extra_capture_started.json').write_text(json.dumps(dict(time=time.time(),scope='Additional training images only; independent test set unused')))
r=subprocess.run([sys.executable,'-u',str(W/'run_head_collection_v02.py')],cwd=W)
sys.exit(r.returncode)
