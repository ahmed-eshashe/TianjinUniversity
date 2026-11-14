"""Unexecuted native segment source plus tested immutable output journal.

The journal records diagnostics only. It is not a restartable native checkpoint,
physics audit, independent reaction measurement or cutting qualification.
"""
import hashlib
import json
import math
import os
from pathlib import Path
from tomato_kinematic_interval import interval_target
from tomato_native_step import step_native_once
from tomato_reaction_metadata import capture_metadata,endpoint_work_estimate


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


class SegmentJournal:
    def __init__(self,path,*,run_id,episode_id,source_sha256):
        if not all(isinstance(v,str) and v for v in (run_id,episode_id)) or not source_sha256:
            raise ValueError('Run/episode/source identity required')
        self.root=Path(path);self.root.mkdir(parents=True,exist_ok=False)
        self.identity={'run_id':run_id,'episode_id':episode_id,'source_sha256':dict(source_sha256)}
        self.next_step=0;self.previous=None
        self._write('identity.json',self.identity)
    def _write(self,name,value):
        # Exclusive creation preserves used output evidence; reject nonfinite JSON.
        data=encoded(value)
        with (self.root/name).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        return hashlib.sha256(data).hexdigest()
    def commit(self,record):
        if type(record.get('step'))is not int or record['step']!=self.next_step:
            raise ValueError('Journal steps must be consecutive from zero')
        row={**self.identity,'previous_record_sha256':self.previous,'diagnostic':record,
             'native_physics_pass':False}
        h=self._write(f'step{self.next_step:06d}.json',row)
        self.previous=h;self.next_step+=1
        return h
    def checkpoint(self,state):
        return self._write(f'checkpoint{self.next_step:06d}.json',{
            **self.identity,'committed_steps':self.next_step,'last_record_sha256':self.previous,
            'diagnostic_state':state,'native_state_registry_complete':False,'restart_supported':False})


def validate_segment(config):
    if config.get('native_execution_enabled') is not False:raise ValueError('Preparation config must stay disabled')
    n=config.get('max_steps')
    if type(n)is not int or not 1<=n<=12:raise ValueError('At most twelve mechanical calls per segment')
    dt=config.get('dt_s')
    if type(dt) not in (int,float) or not math.isfinite(dt) or dt<=0:raise ValueError('Positive finite step size required')
    return n,dt


def run_native_segment(bundle,trajectory,config,journal,observer_kernel,*,native_execution_authorized=False):
    """Source-only isolated coupon loop; no command-line execution route.

    A later reviewed supervisor must hold both locks, validate hashes/quota and
    resource/deadline budgets before calling. This function is not that guard.
    """
    if native_execution_authorized is not True:raise PermissionError('Native execution disabled during preparation')
    count,dt=validate_segment(config)
    if journal.next_step!=0:raise ValueError('Reusing/resuming diagnostic state is unsupported')
    for step in range(count):
        interval=interval_target(trajectory,step=step,dt_s=dt)
        pose=interval['pose']
        row=step_native_once(bundle,pose,step=step,start_s=step*dt,dt_s=dt,
            observer_kernel=observer_kernel,first_step=step==0,native_execution_authorized=True)
        row['prescribed_pose']=pose
        row['prescribed_interval']=interval
        metadata=capture_metadata(bundle,row,target_origin_world_m=(0.,0.,0.),
            native_execution_authorized=True)
        record_diagnostic_step(journal,row,metadata)
    state=bundle['state0']
    journal.checkpoint({'particle_q_m':state.particle_q.numpy().tolist(),
        'particle_qd_m_s':state.particle_qd.numpy().tolist(),
        'body_q':state.body_q.numpy().tolist(),'body_qd':state.body_qd.numpy().tolist(),
        'missing':['all solver history','contact buffers','native reset registry']})
    return {'committed_steps':count,'status':'bounded_diagnostic_segment_only',
            'native_physics_pass':False,'restart_supported':False}


def record_diagnostic_step(journal,row,metadata):
    """Only endpoint diagnostics; no step-average ledger or work acceptance."""
    for key in ('step','start_s','dt_s'):
        if row[key]!=metadata[key]:raise ValueError('Reaction/motion step mismatch')
    if metadata.get('work_ledger_admissible') is not False or metadata.get('temporal_semantics')!='end_of_step_force_not_step_average':
        raise ValueError('Endpoint diagnostic semantics required')
    enriched={**row,'endpoint_reaction_metadata':metadata,
        'endpoint_work_estimate':endpoint_work_estimate(metadata)}
    return journal.commit(enriched)
