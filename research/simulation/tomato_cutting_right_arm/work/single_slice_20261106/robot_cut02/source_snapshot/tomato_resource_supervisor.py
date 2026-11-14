"""Resource policy to checkpoint/cleanup integration using fixed stdlib fixtures.

No arbitrary command or native execution route is accepted. Actual hardware
readers and native-worker protocol still require reviewed runtime integration.
"""
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from tomato_checkpoint_supervisor import _FIXTURE
from tomato_native_launch_contract import checkpoint_request,verify_checkpoint
from tomato_preupgrade_guard import startup_decision,runtime_decision,valid_memory,stop_group,group_members


def supervise_fixture(output,*,monitor,mode='ack',wall_s=.5,checkpoint_grace_s=.2):
    if mode not in ('ack','ignore','bad_hash','exit_without_ack'):raise ValueError('Fixed fixture only')
    if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<v<=1 for v in (wall_s,checkpoint_grace_s)):
        raise ValueError('Bounded fixture wall/checkpoint budgets required')
    # Startup unreadability/refusal must occur before any child launch.
    try:ram,vram=monitor()
    except (OSError,ValueError,RuntimeError):return {'launched':False,'reason':'startup_unreadable'}
    if not startup_decision(ram,vram):return {'launched':False,'reason':'startup_refused'}
    root=Path(output).resolve();root.mkdir(parents=True,exist_ok=False)
    req=checkpoint_request(run_id=root.name,step=7,source_sha256={'fixture':'fixed_stdlib_only'})
    process=None;reason='exception';warnings=0;errors=0;ack=False;requested=False;samples=[]
    start=time.monotonic();deadline=start+wall_s;checkpoint_deadline=None
    try:
        process=subprocess.Popen([sys.executable,'-c',_FIXTURE,str(root),mode],start_new_session=True,
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        (root/'owned_pid.json').write_text(json.dumps({'pid':process.pid}))
        while True:
            now=time.monotonic()
            if now>=deadline:reason='wall_timeout';break
            if checkpoint_deadline is not None and now>=checkpoint_deadline:reason='checkpoint_timeout';break
            try:
                ram,vram=monitor()
                if not valid_memory(ram,vram):raise ValueError('Invalid monitor sample')
                errors=0;action=runtime_decision(ram,vram)
                samples.append({'available_ram_bytes':ram,'free_vram_bytes':vram,'action':action})
            except (OSError,ValueError,RuntimeError):
                errors+=1;action='stop' if errors>=3 else 'continue'
            if action=='stop':reason='monitor_error' if errors>=3 else 'hard_memory_stop';break
            if action=='checkpoint_and_stop' and not requested:
                requested=True;warnings+=1;checkpoint_deadline=min(deadline,now+checkpoint_grace_s)
                temp=root/'request.tmp';temp.write_text(json.dumps(req));temp.replace(root/'stop_request.json')
            if requested and (root/'ack.json').exists():
                try:verify_checkpoint(root,req,json.loads((root/'ack.json').read_text()))
                except (OSError,ValueError,TypeError,KeyError):reason='invalid_ack';break
                ack=True
            if process.poll() is not None:
                reason='checkpoint_and_exit' if requested and ack and process.returncode==0 else 'exit_without_valid_ack';break
            time.sleep(.005)
    finally:
        if process is not None:stop_group(process)
    result={'launched':True,'reason':reason,'checkpoint_requested':requested,'checkpoint_verified':ack,
        'warning_requests':warnings,'monitor_errors':errors,'samples':samples,
        'running_group_members_after_cleanup':[pid for pid,state in group_members(process.pid) if state!='Z'],
        'native_runtime_validated':False,'resource_samples_origin':'injected_fixture_monitor'}
    (root/'supervisor_result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
