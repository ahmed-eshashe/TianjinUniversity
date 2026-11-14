"""Actual OS signal delivery to a fixed stdlib supervisor; no native launch route."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
from tomato_preupgrade_guard import stop_group,group_members

_CHILD=r'''
import subprocess,sys,signal,time
from pathlib import Path
signal.signal(signal.SIGTERM,signal.SIG_IGN)
p=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'])
Path(sys.argv[1]).write_text(str(p.pid))
time.sleep(30)
'''


def _serve(output):
    root=Path(output);process=None;received=None
    class Interrupted(Exception):pass
    def handler(number,frame):
        nonlocal received
        received=number
        raise Interrupted()
    for number in (signal.SIGINT,signal.SIGTERM):signal.signal(number,handler)
    try:
        process=subprocess.Popen([sys.executable,'-c',_CHILD,str(root/'grandchild')],start_new_session=True,
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        end=time.monotonic()+1
        while not (root/'grandchild').exists():
            if time.monotonic()>=end:raise RuntimeError('Child readiness timeout')
            time.sleep(.005)
        p=root/'ready.tmp';p.write_text(json.dumps({'child_group':process.pid}));p.replace(root/'ready.json')
        time.sleep(30)
    except Interrupted:pass
    finally:
        if process is not None:stop_group(process)
        (root/'result.json').write_text(json.dumps({'received_signal':received,
            'remaining_child_group':[p for p,s in group_members(process.pid) if s!='Z'] if process else [],
            'native_runtime_validated':False}))


def run_signal_fixture(output,number):
    if type(number)is not int or number not in (int(signal.SIGINT),int(signal.SIGTERM)):
        raise ValueError('SIGINT or SIGTERM fixed fixture only')
    root=Path(output).resolve();root.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parent))
    process=None;child_group=None
    try:
        process=subprocess.Popen([sys.executable,'-c','from tomato_signal_fixture import _serve;import sys;_serve(sys.argv[1])',str(root)],
            start_new_session=True,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        end=time.monotonic()+2
        while not (root/'ready.json').exists():
            if process.poll() is not None or time.monotonic()>=end:raise RuntimeError('Supervisor readiness failure')
            time.sleep(.005)
        child_group=json.loads((root/'ready.json').read_text())['child_group']
        os.kill(process.pid,number)
        process.wait(timeout=2)
        result=json.loads((root/'result.json').read_text())
        result.update(supervisor_returncode=process.returncode,delivered_signal=number,
            remaining_supervisor_group=[p for p,s in group_members(process.pid) if s!='Z'])
        return result
    finally:
        if process is not None:stop_group(process)
        # Independent emergency cleanup of only the fixture-owned child group.
        if child_group is not None:
            try:os.killpg(child_group,signal.SIGKILL)
            except ProcessLookupError:pass
