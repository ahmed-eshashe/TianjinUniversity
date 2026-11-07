"""Recover resource supervision of one independently identified orphan worker.

Never fabricates an ordinary supervisor pass: records interrupted protection.
"""
from pathlib import Path
import argparse,json,os,time,fcntl,signal
from contextlib import ExitStack
from tomato_isaac_startup_guard import hardware_sample,worker_passed
from tomato_preupgrade_guard import runtime_decision,group_members
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--run',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[2];out=a.run.resolve();launch=json.loads((out/'launch_manifest.json').read_text());pid=a.pid
cmd=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0');actual=[s.decode()for s in cmd if s]
assert actual==launch['command'] and os.getpgid(pid)==pid
stat=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split();ticks=int(stat[19]);started=ticks/os.sysconf('SC_CLK_TCK');uptime=float(Path('/proc/uptime').read_text().split()[0]);remaining=max(0.,launch['worker_wall_budget_s']-(uptime-started));deadline=time.monotonic()+remaining;errors=0;samples=0;minimum_ram=minimum_vram=None;reason='worker_exited';begin=time.time()
(out/'coordinator_interruption.json').write_text(json.dumps(dict(outer_tool_session=32843,reported_exit_code=143,native_pid=pid,owned_command=actual,original_resource_monitor_interrupted=True,remaining_original_wall_budget_s=remaining,adoption_started_unix_s=begin,physics_source_or_state_modified=False,scope='Resource protection has an explicitly disclosed interruption; an ordinary uninterrupted supervisor pass cannot be claimed.'),indent=2)+'\n')
with ExitStack()as stack:
 for name in ['offline_overnight.lock','right_arm_control.lock']:
  lock=stack.enter_context((root/'logs'/name).open('a'));fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 stream=stack.enter_context((out/'adopted_resource_samples.jsonl').open('w'))
 while any(state!='Z'for _,state in group_members(pid)):
  if time.monotonic()>=deadline:reason='original_wall_timeout';break
  try:
   ram,vram=hardware_sample();action=runtime_decision(ram,vram);errors=0;samples+=1;minimum_ram=ram if minimum_ram is None else min(minimum_ram,ram);minimum_vram=vram if minimum_vram is None else min(minimum_vram,vram);stream.write(json.dumps(dict(unix_s=time.time(),available_ram_bytes=ram,free_vram_bytes=vram,action=action))+'\n');stream.flush()
  except Exception as exc:
   errors+=1;action='stop'if errors>=3 else'continue';stream.write(json.dumps(dict(error=repr(exc),consecutive_errors=errors))+'\n');stream.flush()
  if action!='continue':reason='resource_or_monitor_stop';break
  time.sleep(.2)
 if reason!='worker_exited':
  (out/'stop.request').write_text('Recovered monitor reached original stop condition.\n')
  try:os.killpg(pid,signal.SIGTERM)
  except ProcessLookupError:pass
  time.sleep(2)
  try:os.killpg(pid,signal.SIGKILL)
  except ProcessLookupError:pass
 remaining_group=[p for p,state in group_members(pid)if state!='Z'];wp=out/'worker_result.json';worker=json.loads(wp.read_text())if wp.exists()else{};native_component_complete=reason=='worker_exited'and not remaining_group and worker_passed(worker,launch['mode'])
 report=dict(physics_component_complete_after_monitor_recovery=native_component_complete,uninterrupted_resource_supervision_passed=False,original_supervisor_exit_code=143,reason=reason,remaining_live_group_members=remaining_group,worker=worker,adopted_resource_samples=samples,min_available_ram_bytes=minimum_ram,min_free_vram_bytes=minimum_vram,scope='Recovered owned-worker monitoring only; no original supervisor exit status inferred. Raw complete physics may be independently analysed with the monitoring interruption disclosed.')
 (out/'recovered_monitor_result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
