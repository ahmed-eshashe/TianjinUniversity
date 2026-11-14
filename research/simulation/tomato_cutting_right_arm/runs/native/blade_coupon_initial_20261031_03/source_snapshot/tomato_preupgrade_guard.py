"""Preparation guard reference. CLI is preview-only; native execution disabled.

Uses unchanged production watchdog policy, with fail-closed input validation.
Only built-in tiny dummy commands can execute through this module for tests.
"""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from guard_benchmark import startup_allowed, resource_action


def valid_memory(ram, vram):
    return all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in (ram,vram))


def startup_decision(ram, vram):
    return valid_memory(ram,vram) and startup_allowed(ram,vram)


def runtime_decision(ram, vram, errors=0):
    if not valid_memory(ram,vram) or type(errors) is not int or errors < 0:
        return 'stop'
    return resource_action(ram,vram,errors)


def native_preview(root, config):
    worker=Path(root)/'rl/tomato_native_coupon.py'
    return {'command':['/home/omen/miniconda3/envs/isaaclab_6/bin/python',
                       str(worker),'--config',str(Path(config))],
            'execution_enabled':False,'worker_source_exists':worker.is_file(),
            'requires':['RAM upgrade resource verification','explicit native execution authorization',
                        'reviewed dedicated native launch integration'],
            'worker_wall_budget_s':60,'imports_or_subprocesses_started':False}


def stop_group(process, grace_s=.1):
    """Own process group only, TERM then KILL even if leader already exited."""
    pgid=process.pid  # start_new_session=True established this ownership
    try:
        os.killpg(pgid,signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=grace_s)
    except subprocess.TimeoutExpired:
        pass
    # The leader may exit while descendants still run. Always send final KILL.
    try:
        os.killpg(pgid,signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=1)


def group_members(pgid):
    members=[]
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            fields=path.read_text().rsplit(')',1)[1].split()
            if int(fields[2]) == pgid:
                members.append((int(path.parent.name),fields[0]))
        except (OSError,ValueError,IndexError):
            continue
    return members


def run_dummy(mode, *, monitor, wall_s=.15):
    """Exercise supervisor lifecycle using fixed stdlib-only fixture commands.

    This is a test route, not the future native launcher. CPU/address-space caps,
    locks, deadline and quota checks belong to the outer capped test worker.
    """
    scripts={
        'exit':'pass',
        'sleep':'import time;time.sleep(30)',
        'ignore_term':'import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)',
        'spawn_sleep':'import subprocess,sys,time;subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"]);time.sleep(30)',
    }
    if mode not in scripts or not math.isfinite(wall_s) or not 0 < wall_s <= 1:
        raise ValueError('Only bounded built-in dummy fixtures are allowed')
    ram,vram=monitor()
    if not startup_decision(ram,vram):
        return {'reason':'startup_refused','launched':False}
    process=None;reason='exception';samples=[];errors=0;started=time.monotonic()
    try:
        process=subprocess.Popen([sys.executable,'-c',scripts[mode]],
                                 start_new_session=True,stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        while process.poll() is None:
            if time.monotonic()-started >= wall_s:
                reason='wall_timeout';break
            try:
                ram,vram=monitor()
                if not valid_memory(ram,vram):
                    raise ValueError('Invalid memory sample')
                errors=0;action=runtime_decision(ram,vram,errors)
                samples.append({'ram':ram,'vram':vram,'action':action})
            except (OSError,ValueError,RuntimeError):
                errors+=1;action='stop' if errors>=3 else 'continue'
            if action != 'continue':
                reason='monitor_error' if errors>=3 else action;break
            time.sleep(.005)
        else:
            reason='exited'
        return {'reason':reason,'launched':True,'pid':process.pid,
                'returncode_before_cleanup':process.poll(),'samples':samples,
                'group_before_cleanup':group_members(process.pid)}
    finally:
        if process is not None:
            stop_group(process)


def main():
    parser=argparse.ArgumentParser(description='Native coupon preview only; no execution')
    parser.add_argument('--config',required=True)
    args=parser.parse_args()
    print(json.dumps(native_preview(Path(__file__).resolve().parents[1],args.config),indent=2))


if __name__=='__main__':
    main()
