"""Bounded isolated configure/compile; never launches the robot worker."""
from pathlib import Path
import argparse,json,os,signal,subprocess,time,shutil
p=argparse.ArgumentParser();p.add_argument('phase',choices=['configure','compile']);p.add_argument('--output',required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;cwd=root/'PhysX/omni/ovexts';out=root/a.output;out.mkdir(exist_ok=False)
cmd=['./build.sh','-r','-g','-n','--devphysx']if a.phase=='configure'else[shutil.which('cmake')or'cmake','--build','_compiler/gcc-linux-x86_64/build-release','--target','OvruntimePhysX','-j2']
env=dict(os.environ,BUILD_JOB_COUNT='2');start=time.monotonic();deadline=1800.;reason=None;proc=None;samples=[]
def group_members(gid):
 r=subprocess.run(['ps','-eo','pid=,pgid='],capture_output=True,text=True,check=True)
 return [int(x.split()[0])for x in r.stdout.splitlines()if int(x.split()[1])==gid]
def stop(*_):raise InterruptedError('External stop')
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:
 with (out/'console.log').open('w')as f:
  proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  while proc.poll()is None:
   fields={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()if line.startswith('MemAvailable:')}
   available=fields['MemAvailable'];free=shutil.disk_usage(root).free;elapsed=time.monotonic()-start
   samples.append({'elapsed_s':elapsed,'mem_available_bytes':available,'disk_free_bytes':free})
   if elapsed>deadline:reason='wall_deadline';break
   if available<4*1024**3:reason='memory_floor';break
   if free<10*1024**3:reason='disk_floor';break
   time.sleep(2)
except BaseException as error:reason=repr(error)
finally:
 if proc is not None and group_members(proc.pid):
  os.killpg(proc.pid,signal.SIGTERM)
  until=time.monotonic()+10
  while group_members(proc.pid)and time.monotonic()<until:time.sleep(.2)
  if group_members(proc.pid):os.killpg(proc.pid,signal.SIGKILL)
  proc.wait()
 remaining=group_members(proc.pid)if proc else []
 result={'phase':a.phase,'command':cmd,'returncode':proc.returncode if proc else None,'stop_reason':reason,'wall_s':time.monotonic()-start,'remaining_owned_pids':remaining,'passed':proc is not None and proc.returncode==0 and reason is None and not remaining,'robot_simulation_runs':0}
 (out/'resources.json').write_text(json.dumps(samples,indent=2)+'\n');(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
