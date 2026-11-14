from pathlib import Path
import subprocess,os,time,json,threading
import psutil
w=Path(__file__).resolve().parent;r=w.parents[1];production=r/'work/single_slice_20261106/robot_cut18'
while not (production/'supervisor_result.json').exists():time.sleep(5)
cp=r/'work/single_slice_20261106/robot_cut17/checkpoints/step_006400.npz'
env=os.environ.copy();env.update(PYTHONPATH=str(r/'rl'),DISPLAY=':1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONUNBUFFERED='1')
start=time.time()
samples=[];done=threading.Event()
def sample():
 while not done.is_set():
  rows=[]
  for p in psutil.process_iter(['pid','cmdline','memory_info']):
   try:
    if any(str(w/'profile_worker.py')==x for x in (p.info['cmdline'] or [])):rows.append({'pid':p.pid,'rss_bytes':p.info['memory_info'].rss})
   except (psutil.NoSuchProcess,psutil.AccessDenied):pass
  gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout
  samples.append({'wall_s':time.time()-start,'processes':rows,'gpu_process_memory':gpu})
  done.wait(2)
threading.Thread(target=sample,daemon=True).start()
with (w/'profile.log').open('w') as f:
 try:
  p=subprocess.run([str(r/'.venv-native/bin/python'),str(w/'profile_worker.py'),'--output',str(w/'current_profile'),'--headless','--resume-checkpoint',str(cp)],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
  result={'returncode':p.returncode}
 except subprocess.TimeoutExpired:result={'timeout':True}
done.set();(w/'profile_memory.json').write_text(json.dumps(samples,indent=2))
result.update(wall_s=time.time()-start,production_pause=json.loads((production/'supervisor_result.json').read_text()))
(w/'profile_launch.json').write_text(json.dumps(result,indent=2))
