from pathlib import Path
import sys,subprocess,time,json,fcntl
from contextlib import ExitStack
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_backward_elbow_guard_v01 import hardware_sample
from tomato_preupgrade_guard import startup_decision,runtime_decision,stop_group
out=w/'failure_probe01';out.mkdir(exist_ok=True);samples=[];start=time.monotonic();proc=None;reason='not_launched'
with ExitStack() as stack:
 for name in ['offline_overnight.lock','right_arm_control.lock']:
  lock=stack.enter_context((r/'logs'/name).open('a'));fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  assert startup_decision(*hardware_sample())
  log=stack.enter_context((out/'worker.log').open('w'));proc=subprocess.Popen([str(r/'.venv-native/bin/python'),str(w/'check_failure_probe.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  while proc.poll() is None:
   ram,vram=hardware_sample();samples.append(dict(time_s=time.monotonic()-start,ram_available_bytes=ram,vram_free_bytes=vram))
   if runtime_decision(ram,vram)!='continue':reason='memory_stop';break
   if time.monotonic()-start>1200:reason='wall_timeout';break
   time.sleep(1)
  else:reason='exited'
 finally:
  if proc is not None and proc.poll() is None:stop_group(proc,grace_s=5)
  (out/'supervisor.json').write_text(json.dumps(dict(reason=reason,returncode=None if proc is None else proc.returncode,samples=samples),indent=2))
print(reason)
