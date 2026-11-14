from pathlib import Path
import psutil,subprocess,time,json
w=Path(__file__).resolve().parent;end=time.monotonic()+3600;rows=[]
while time.monotonic()<end:
 procs=[]
 for p in psutil.process_iter(['pid','cmdline','memory_info']):
  try:
   cmd=p.info['cmdline'] or []
   if any(Path(arg).name in ['profile_worker2.py','disect_repeat.py'] for arg in cmd[1:]):procs.append(dict(pid=p.pid,cmd=cmd,rss=p.info['memory_info'].rss))
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 if procs:
  gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout
  rows.append(dict(time=time.time(),processes=procs,gpu=gpu));(w/'memory_samples2.json').write_text(json.dumps(rows,indent=2))
 if (w/'disect_repeat_exit.json').exists():break
 time.sleep(2)
