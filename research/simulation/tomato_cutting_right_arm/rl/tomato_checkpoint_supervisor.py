"""Stdlib fixture supervisor for checkpoint-stop handshake. No native launcher."""
import json
import subprocess
import sys
import time
from pathlib import Path
from tomato_native_launch_contract import checkpoint_request,verify_checkpoint
from tomato_preupgrade_guard import stop_group,group_members

# Fixed built-in fixture only. There is no arbitrary command parameter.
_FIXTURE='''
import sys,time,json,hashlib
from pathlib import Path
root=Path(sys.argv[1]);mode=sys.argv[2]
while not (root/'stop_request.json').exists():time.sleep(.005)
if mode=='ignore':time.sleep(30)
if mode=='exit_without_ack':sys.exit(0)
r=json.loads((root/'stop_request.json').read_text())
p=root/'state.json';p.write_text(json.dumps({'fixture_only':True,'committed_step':r['last_committed_step']}))
a={'run_id':r['run_id'],'source_sha256':r['source_sha256'],'committed_step':r['last_committed_step'],
   'state_path':'state.json','state_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'worker_stopped':True}
if mode=='bad_hash':a['state_sha256']='invalid'
t=root/'ack.tmp';t.write_text(json.dumps(a));t.replace(root/'ack.json')
'''


def run_checkpoint_fixture(output,*,mode='ack',ack_timeout_s=.3):
    """Run only a fixed bounded fixture. Outer test worker owns shared locks/caps.

    Worker-stopped flag alone is insufficient: require verified ack AND actual
    leader exit. Always terminate the private process group, including children.
    """
    if mode not in ('ack','ignore','exit_without_ack','bad_hash'):
        raise ValueError('Unknown fixed fixture')
    if type(ack_timeout_s) not in (int,float) or not 0<ack_timeout_s<=1:
        raise ValueError('Fixture timeout outside bounds')
    root=Path(output).resolve();root.mkdir(parents=True,exist_ok=False)
    req=checkpoint_request(run_id=root.name,step=7,source_sha256={'fixture':'fixed_stdlib_only'})
    process=None;reason='exception';verified=False;exited=False
    try:
        process=subprocess.Popen([sys.executable,'-c',_FIXTURE,str(root),mode],
            start_new_session=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        (root/'stop_request.json').write_text(json.dumps(req))
        until=time.monotonic()+ack_timeout_s
        while time.monotonic()<until:
            if (root/'ack.json').exists():
                try:verify_checkpoint(root,req,json.loads((root/'ack.json').read_text()))
                except (ValueError,OSError,KeyError,TypeError):reason='invalid_ack';break
                verified=True
            if process.poll() is not None:
                exited=True;reason='checkpoint_and_exit' if verified and process.returncode==0 else 'exit_without_valid_ack';break
            time.sleep(.005)
        else:reason='checkpoint_timeout'
    finally:
        if process is not None:stop_group(process)
    running=[pid for pid,state in group_members(process.pid) if state!='Z']
    return {'reason':reason,'checkpoint_verified':verified,'leader_exited_before_cleanup':exited,
        'process_group_running_after_cleanup':running,'native_runtime_validated':False}
