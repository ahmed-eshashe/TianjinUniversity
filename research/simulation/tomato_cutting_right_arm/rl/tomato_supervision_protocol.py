"""Disabled worker/guard binding and pure event protocol; never launches a process."""
import math
from pathlib import Path
from tomato_native_launch_contract import validate_request, owned_file
from tomato_native_worker import preview
from tomato_preupgrade_guard import runtime_decision, valid_memory
import json


def prepare(root,request,output,*,now_utc):
    validate_request(root,request,now_utc=now_utc)
    path=owned_file(root,request['config_path'])
    config=json.loads(path.read_text())
    # Both authorities must bind exactly the worker's source set, not subsets.
    if request['source_sha256']!=config['source_sha256']:
        raise ValueError('Request and worker source sets differ')
    root=Path(root).resolve();out=Path(output).absolute()
    if not out.is_relative_to(root) or '..' in out.parts:
        raise ValueError('Output must be owned')
    for p in [out,*out.parents]:
        if p==root:break
        if p.is_symlink():raise ValueError('Symlink output forbidden')
    config['_config_path']=str(path.resolve())
    command=preview(root,config,out)
    return dict(command,wall_budget_s=request['wall_budget_s'],
        execution_enabled=False,supervisor_integration_validated=False,
        checkpoint_resumable=False,protocol='checkpoint_then_stop',
        pending=['native checkpoint serialization and command polling',
                 'actual bounded monitor/process-group wiring and runtime evidence'])


class MonitorProtocol:
    """Pure event decisions. Clock/readers/IPC/exit verification remain external."""
    def __init__(self,*,start,wall_s,checkpoint_grace_s):
        if any(type(x) not in (int,float) or not math.isfinite(x) for x in (start,wall_s,checkpoint_grace_s)) or not 0<wall_s<=60 or not 0<checkpoint_grace_s<=wall_s:
            raise ValueError('Finite bounded monotonic budgets required')
        self.last=start;self.deadline=start+wall_s;self.grace=checkpoint_grace_s
        self.checkpoint_deadline=None;self.errors=0;self.terminal=False

    def tick(self,now,*,sample=None):
        if type(now) not in (int,float) or not math.isfinite(now) or now<self.last:
            self.terminal=True
            return 'stop_invalid_clock'
        self.last=now
        if self.terminal:return 'stop'
        if now>=self.deadline or (self.checkpoint_deadline is not None and now>=self.checkpoint_deadline):
            self.terminal=True;return 'stop_timeout'
        if not isinstance(sample,(tuple,list)) or len(sample)!=2 or not valid_memory(*sample):
            self.errors+=1
            if self.errors>=3:self.terminal=True;return 'stop_monitor_errors'
            return 'continue'
        self.errors=0;action=runtime_decision(*sample)
        if action=='stop':self.terminal=True;return 'stop_memory'
        if action=='checkpoint_and_stop':
            if self.checkpoint_deadline is None:
                self.checkpoint_deadline=min(self.deadline,now+self.grace)
                return 'request_checkpoint_once'
            return 'await_checkpoint_exit'
        return 'await_checkpoint_exit' if self.checkpoint_deadline is not None else 'continue'
