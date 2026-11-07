"""Owned-process launch for the research slicing extension; existing memory policy."""
import argparse,fcntl,json,os,signal,subprocess,time,hashlib
from contextlib import ExitStack
from pathlib import Path
from tomato_backward_elbow_guard_v01 import hardware_sample
from tomato_preupgrade_guard import startup_decision,runtime_decision,stop_group
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--wall-seconds',type=float,default=43200);p.add_argument('--cut-steps',type=int,default=20000);p.add_argument('--headless',action='store_true');p.add_argument('--interactive',action='store_true');p.add_argument('--resume-checkpoint',type=Path);a=p.parse_args()
 if not(0<a.wall_seconds<=86400 and 0<a.cut_steps<=100000) or (a.headless and a.interactive):raise ValueError('Invalid bounded launch settings')
 comparison=json.loads((ROOT/'work/single_slice_20261106/exploratory_comparison_v1.json').read_text())
 if comparison.get('passed') is not True:raise ValueError('Exploratory accuracy comparisons have not passed')
 motion=ROOT/'work/single_slice_20261106/bodyward_motion_check01'
 # Motion-only worker intentionally returns 1 when no full slice is claimed.
 if json.loads((motion/'motion_check.json').read_text()).get('passed') is not True or not (motion/'actual_pose.json').exists() or not (motion/'measurements.json').exists():raise ValueError('Incomplete native motion result')
 if not (motion/'motion_check.json').exists() or (motion/'worker_failure.json').exists() or json.loads((motion/'supervisor_result.json').read_text()).get('returncode')!=1:raise ValueError('Horizontal withdrawal motion check missing or unexpected worker termination')
 a.output.mkdir(parents=True,exist_ok=False);proc=None;reason='not_launched';start=time.monotonic()
 def stopped(*_):raise InterruptedError('Owned supervisor stop')
 signal.signal(signal.SIGINT,stopped);signal.signal(signal.SIGTERM,stopped)
 with ExitStack()as stack:
  for name in ('offline_overnight.lock','right_arm_control.lock'):
   lock=stack.enter_context((ROOT/'logs'/name).open('a'));fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   ram,vram=hardware_sample()
   if not startup_decision(ram,vram):raise RuntimeError('Existing startup memory protection refused launch')
   command=[str(ROOT/'.venv-native/bin/python'),str(ROOT/'rl/tomato_research_cut_robot_worker_v15.py'),'--output',str(a.output),'--cut-steps',str(a.cut_steps)]+(['--headless']if a.headless else [])+(['--interactive']if a.interactive else [])
   if a.resume_checkpoint is not None:command+=['--resume-checkpoint',str(a.resume_checkpoint)]
   env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONUNBUFFERED='1');sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in (ROOT/'rl').glob('tomato_*.py')};(a.output/'launch_manifest.json').write_text(json.dumps(dict(command=command,wall_seconds=a.wall_seconds,source_sha256=sources),indent=2))
   log=stack.enter_context((a.output/'worker.log').open('w'));proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True,env=env);errors=0
   while proc.poll()is None:
    if time.monotonic()-start>a.wall_seconds:reason='wall_timeout';break
    if(a.output/'stop.request').exists():reason='owned_stop_request';break
    try:
     ram,vram=hardware_sample();action=runtime_decision(ram,vram);errors=0
    except Exception:errors+=1;action='stop'if errors>=3 else 'continue'
    if action!='continue':reason='memory_or_monitor_stop';break
    time.sleep(1)
   else:reason='exited'
  finally:
   if proc is not None:stop_group(proc,grace_s=5)
   result=dict(reason=reason,returncode=None if proc is None else proc.returncode,wall_s=time.monotonic()-start,full_slice_success=False)
   if(a.output/'cutting_result.json').exists():result['full_slice_success']=json.loads((a.output/'cutting_result.json').read_text())['full_slice_success']
   (a.output/'supervisor_result.json').write_text(json.dumps(result,indent=2));print(result)
 return 0 if result['full_slice_success'] else 1
if __name__=='__main__':raise SystemExit(main())
