"""Fail-closed launch/checkpoint contracts. This module cannot launch an engine."""
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from tomato_preupgrade_guard import startup_decision


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc(value):
    t=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None or t.utcoffset()!=dt.timedelta(0):
        raise ValueError('Explicit UTC timestamp required')
    return t


def owned_file(root,relative):
    root=Path(root).resolve()
    p=root/relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('Relative owned path required')
    # Reject symlinks at every level, even if the target remains inside root.
    for part in [p,*p.parents]:
        if part==root:break
        if part.is_symlink():raise ValueError('Symlink not allowed')
    if not p.is_file() or not p.resolve().is_relative_to(root):
        raise ValueError('Missing/outside owned file')
    return p


def validate_request(root,request,*,now_utc):
    """Check future approval binding without treating preparation as approval.

    A dictionary is evidence to be reviewed, not authentication. A later launcher
    must obtain explicit human authorization and invoke this before Popen.
    """
    now=utc(now_utc)
    if request.get('purpose') not in ('single_blade_coupon','two_piece_coupon'):
        raise ValueError('Isolated coupon scope required')
    if request.get('training') is not False or request.get('robot_coupling') is not False:
        raise ValueError('Training and robot coupling outside scope')
    seconds=request.get('wall_budget_s')
    if type(seconds) not in (int,float) or not math.isfinite(seconds) or not 0<seconds<=60:
        raise ValueError('Wall budget must be at most 60 seconds')
    end=utc(request['expires_utc']);start=utc(request['not_before_utc'])
    if not start<=now or now+dt.timedelta(seconds=seconds)>end:
        raise ValueError('Outside authorization window or insufficient remaining margin')
    sources=request.get('source_sha256')
    if not isinstance(sources,dict) or not sources:raise ValueError('Source binding required')
    for path,expected in sources.items():
        if digest(owned_file(root,path))!=expected:raise ValueError('Source hash mismatch')
    config=owned_file(root,request['config_path'])
    if digest(config)!=request['config_sha256']:raise ValueError('Configuration hash mismatch')
    cfg=json.loads(config.read_text())
    if cfg.get('purpose')!=request['purpose'] or cfg.get('native_execution_enabled') is not False:
        raise ValueError('Preparation config must remain disabled and match purpose')
    return {'request_verified':True,'execution_enabled':False,
            'native_runtime_validated':False,'pending':'Separate human authorization and reviewed launcher'}


def sample_resources(*,host_reader,gpu_reader):
    """Fresh acquisition adapter; readers must implement bounded actual reads."""
    ram=host_reader();used,total=gpu_reader()
    if any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in (ram,used,total)) or used>total:
        raise ValueError('Invalid actual resource sample')
    return {'available_ram_bytes':ram,'free_vram_bytes':total-used,
            'startup_allowed':startup_decision(ram,total-used)}


def checkpoint_request(*,run_id,step,source_sha256):
    if not isinstance(run_id,str) or not run_id or type(step)is not int or step<0:
        raise ValueError('Run identity and nonnegative committed step required')
    if not isinstance(source_sha256,dict) or not source_sha256:raise ValueError('Source binding required')
    return {'run_id':run_id,'last_committed_step':step,'source_sha256':dict(source_sha256),
            'command':'checkpoint_then_stop'}


def verify_checkpoint(root,request,ack):
    """Acknowledge only a matching committed state file; no native validity claim."""
    if ack.get('run_id')!=request['run_id'] or ack.get('source_sha256')!=request['source_sha256']:
        raise ValueError('Checkpoint identity/source mismatch')
    step=ack.get('committed_step')
    if type(step)is not int or step<request['last_committed_step']:
        raise ValueError('Stale or uncommitted checkpoint')
    p=owned_file(root,ack['state_path'])
    if digest(p)!=ack['state_sha256']:raise ValueError('Checkpoint digest mismatch')
    if ack.get('worker_stopped') is not True:raise ValueError('Worker stop acknowledgment required')
    return {'checkpoint_file_verified':True,'native_state_complete':False,
            'process_exit_independently_required':True}


def actual_resources():
    """Bounded read-only hardware query; never initializes a simulator or CUDA."""
    import subprocess
    def host():
        rows=Path('/proc/meminfo').read_text().splitlines()
        row=next(x for x in rows if x.startswith('MemAvailable:'))
        fields=row.split()
        if len(fields)!=3 or fields[2]!='kB':raise ValueError('Unexpected host memory units')
        return int(fields[1])*1024
    def gpu():
        raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total',
            '--format=csv,noheader,nounits'],text=True,timeout=2)
        rows=raw.strip().splitlines()
        if len(rows)!=1:raise ValueError('Explicit GPU selection required for multiple devices')
        fields=rows[0].split(',')
        if len(fields)!=2:raise ValueError('Unexpected GPU memory layout')
        return tuple(int(x.strip())*1024**2 for x in fields)
    return sample_resources(host_reader=host,gpu_reader=gpu)
