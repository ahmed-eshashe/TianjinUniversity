from pathlib import Path
import os,time,subprocess,json
W=Path(__file__).resolve().parents[1];pid=json.loads((W/'persistent_cut_controls.partial.json').read_text())['pid'];rows=[];start=time.monotonic()
while time.monotonic()-start<600:
 try:
  status=Path(f'/proc/{pid}/status').read_text()
  if '\nState:\tZ' in status:break
 except FileNotFoundError:break
 out=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout
 rss=[l for l in status.splitlines() if l.startswith(('VmRSS:','VmHWM:'))];rows.append({'elapsed_s':time.monotonic()-start,'process_memory':rss,'gpu_processes':out.strip()});time.sleep(1)
(W/'runs/gate2_resources.json').write_text(json.dumps({'pid':pid,'sampling_interval_s':1,'note':'Sampling began after first full-cut control, misses earlier peaks; per-process lifetime host peak also in gate result','samples':rows},indent=2));print('samples',len(rows))
