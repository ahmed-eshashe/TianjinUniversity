"""Bounded, sequential GPU runs. No installations or engine patches."""
import json, pathlib, subprocess, time, sys
root=pathlib.Path(__file__).resolve().parent
(root/'results').mkdir(exist_ok=True)
repeat=sys.argv[1:]==['repeat']
matrix = ([('cuts',s,0) for s in ['mls','pb'] for _ in range(2)] if repeat else [('stock','mls',0)]) if (repeat or sys.argv[1:] == ['stock']) else (
 [(m,s,1) for s in ['mls','pb'] for m in ['held','absent','far']]
 if sys.argv[1:] == ['probe'] else [('cuts',s,p) for s in ['mls','pb'] for p in [0,1]])
for index,(mode,solver,pulse) in enumerate(matrix):
 name=f'{mode}_{solver}_{pulse}'+('_offgrid' if mode in ['held','absent','far'] else '')
 if repeat: name+=f'_repeat{index%2+1}'
 cmd=[str(root/'feasibility'),mode,solver,str(root/'results'/name),str(pulse)]
 start=time.monotonic(); rows=[]; peak_rss=0; peak_gpu=0
 with (root/'results'/f'{name}.log').open('w') as log:
  process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=root)
  while process.poll() is None:
   try:
    status=pathlib.Path(f'/proc/{process.pid}/status').read_text()
    rss=int(next(l.split()[1] for l in status.splitlines() if l.startswith('VmRSS:')))
    peak_rss=max(peak_rss,rss)
   except (FileNotFoundError,StopIteration): pass
   result=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True,capture_output=True)
   for line in result.stdout.splitlines():
    parts=line.split(',')
    if parts[0].strip()==str(process.pid):
     try: peak_gpu=max(peak_gpu,int(parts[1]))
     except ValueError: pass
   if time.monotonic()-start>600:
    process.terminate()
    try: process.wait(timeout=10)
    except subprocess.TimeoutExpired: process.kill(); process.wait()
    break
   time.sleep(.5)
 elapsed=time.monotonic()-start
 record={'command':cmd,'exit_code':process.returncode,'process_wall_seconds':elapsed,'peak_sampled_rss_mib':peak_rss/1024,'peak_sampled_process_gpu_mib':peak_gpu,'sampling_seconds':.5}
 (root/'results'/f'{name}_run.json').write_text(json.dumps(record,indent=2))
 print(name,record,flush=True)
 if process.returncode!=0: sys.exit(process.returncode or 1)
