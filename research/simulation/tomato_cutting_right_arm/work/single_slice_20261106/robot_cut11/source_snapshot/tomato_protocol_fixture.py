"""Fixed stdlib process fixture exercising MonitorProtocol; no native route."""
import json
import subprocess
import sys
import time
from pathlib import Path
from tomato_supervision_protocol import MonitorProtocol
from tomato_checkpoint_supervisor import _FIXTURE
from tomato_native_launch_contract import checkpoint_request,verify_checkpoint
from tomato_preupgrade_guard import startup_decision,stop_group,group_members


def run_fixture(output,*,monitor,mode='ack',wall_s=.5,grace_s=.2):
    if mode not in ('ack','ignore','bad_hash','exit_without_ack'):raise ValueError('Fixed fixture only')
    if not 0<wall_s<=1 or not 0<grace_s<=wall_s:raise ValueError('Fixture budgets required')
    start=time.monotonic();protocol=MonitorProtocol(start=start,wall_s=wall_s,checkpoint_grace_s=grace_s)
    try:sample=monitor()
    except (OSError,ValueError,RuntimeError):return {'launched':False,'reason':'startup_unreadable'}
    if not startup_decision(*sample):return {'launched':False,'reason':'startup_refused'}
    root=Path(output).resolve();root.mkdir(parents=True,exist_ok=False)
    request=checkpoint_request(run_id=root.name,step=7,source_sha256={'fixture':'fixed_stdlib_only'})
    process=None;ack=False;requested=False;reason='exception';actions=[]
    try:
        process=subprocess.Popen([sys.executable,'-c',_FIXTURE,str(root),mode],start_new_session=True,
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        while True:
            try:sample=monitor()
            except (OSError,ValueError,RuntimeError):sample=None
            action=protocol.tick(time.monotonic(),sample=sample);actions.append(action)
            if action.startswith('stop'):reason=action;break
            if action=='request_checkpoint_once':
                requested=True;p=root/'request.tmp';p.write_text(json.dumps(request));p.replace(root/'stop_request.json')
            if requested and (root/'ack.json').exists():
                try:verify_checkpoint(root,request,json.loads((root/'ack.json').read_text()))
                except (OSError,ValueError,TypeError,KeyError):reason='invalid_ack';break
                ack=True
            if process.poll() is not None:
                reason='checkpoint_and_exit' if requested and ack and process.returncode==0 else 'exit_without_valid_ack';break
            time.sleep(.005)
    finally:
        if process is not None:stop_group(process)
    return {'launched':True,'reason':reason,'actions':actions,'checkpoint_verified':ack,
        'running_after_cleanup':[p for p,s in group_members(process.pid) if s!='Z'],
        'native_runtime_validated':False,'monitor_origin':'injected_fixture_only'}
