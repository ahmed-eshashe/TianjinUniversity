"""Transactional event-localized geometry driver. Restricted component fixture.
Bulk GPU and fractional CPU velocity-Verlet use the same full-mass mechanics.
"""
import copy,json,hashlib,time
from pathlib import Path
import numpy as np
from band_system import BandSystem
from multicut import volume_certificates
from blade_sweep import validate_pose,shadow
from deformed_sweep import DeformedSweep,field_snapshot
from integrated_cut import RejectedEvent
from gpu_backend import GPUReference


def clone_cpu(s):
    out=shadow(s)
    for key,old in s.pieces.items():
        p=copy.copy(old)
        for field in ['q','vg','support_impulse','support_moment']:setattr(p,field,getattr(old,field).copy())
        p.history=copy.deepcopy(old.history);p.update_state();out.pieces[key]=p
    return out

class EventSweep(DeformedSweep):
    def __init__(self,cpu,initial_pose,dt=3.90625e-7/16,probe=25e-6,event_tol=2.5e-10):
        super().__init__(cpu,initial_pose)
        if cpu.band is None:raise RejectedEvent('band must be initialized from current pose')
        b=cpu.band;self.histories={'root':{'axis':b['axis'],'plane':b['plane'],'rectangles':[]}}
        self.dt=dt;self.probe=probe;self.event_tol=event_tol;self.activations=[];self.cost={'trials':0,'GPU_steps':0,'CPU_fractional_steps':0,'peak_array_bytes':0,'propagation_s':0.,'geometry_s':0.}

    def clone(self):
        out=copy.copy(self);out.cpu=clone_cpu(self.cpu);out.previous=field_snapshot(self.previous_proxy())
        out.histories=copy.deepcopy(self.histories);out.commands=copy.deepcopy(self.commands);out.activations=copy.deepcopy(self.activations);out.cost=copy.deepcopy(self.cost)
        return out
    def previous_proxy(self):
        s=copy.copy(self.cpu);s.pieces=self.previous;return s

    def guard_pose(self,new_pose):
        new_pose=validate_pose(new_pose);initial=np.array(self.cpu.band['initial_pose'])
        if np.max(abs(new_pose[:3,:3]-initial[:3,:3]))>1e-10:raise RejectedEvent('single aligned approach: orientation change unsupported')
        if abs((new_pose[:3,3]-initial[:3,3])@initial[:3,2])>1e-12:raise RejectedEvent('single aligned approach: off-plane translation unsupported')
        return new_pose

    def propagate(self,duration):
        if duration<=0:raise ValueError('positive propagation interval required')
        start=time.perf_counter();end=self.cpu.time+duration;dt=self.dt
        # Complete any previously interrupted absolute mechanical time cell.
        phase=self.cpu.time/dt;nearest=round(phase)
        if abs(phase-nearest)>1e-7:
            first=min(end-self.cpu.time,(np.floor(phase)+1)*dt-self.cpu.time)
            if first>1e-16:self.cpu.step(first);self.cost['CPU_fractional_steps']+=1
        remaining=end-self.cpu.time;n=int(np.floor(remaining/dt+1e-8))
        if n:
            g=GPUReference(self.cpu,dt=dt);g.step(n);g.export();self.cost['GPU_steps']+=n;self.cost['peak_array_bytes']=max(self.cost['peak_array_bytes'],g.memory())
        remaining=end-self.cpu.time
        if remaining>1e-16:self.cpu.step(remaining);self.cost['CPU_fractional_steps']+=1
        if abs(self.cpu.time-end)>1e-14:raise RejectedEvent('event clock mismatch')
        # Same float64 value, canonical Python scalar for deterministic checkpoint fingerprints.
        self.cpu.time=float(self.cpu.time)
        for p in self.cpu.pieces.values():
            p.time=float(p.time)
            if not all(c['passed'] for c in volume_certificates(p)):raise RejectedEvent('continuous volume certificate failed')
        self.cost['propagation_s']+=time.perf_counter()-start

    def trial(self,target,duration):
        t=self.clone();t.propagate(duration);start=time.perf_counter();p=t.propose(target,preview_only=True)
        t.cost['geometry_s']+=time.perf_counter()-start
        self.cost['trials']+=1
        # Cost measures all previews, even discarded bisection states.
        for k in ['GPU_steps','CPU_fractional_steps','propagation_s','geometry_s']:self.cost[k]+=t.cost[k]-self.cost[k]
        self.cost['peak_array_bytes']=max(self.cost['peak_array_bytes'],t.cost['peak_array_bytes'])
        return t,p

    def action(self,new_pose,duration,wall_limit=600):
        new_pose=self.guard_pose(new_pose)
        if not np.isfinite(duration) or duration<=0:raise RejectedEvent('invalid action duration')
        token=self.fingerprint();work=self.clone();begin=time.perf_counter();t0=work.cpu.time;end=t0+duration;p0=work.pose.copy()
        def target(t):
            p=p0.copy();p[:3,3]=p0[:3,3]+(new_pose[:3,3]-p0[:3,3])*((t-t0)/duration);return p
        while work.cpu.time<end-1e-15:
            if time.perf_counter()-begin>wall_limit:raise TimeoutError('bounded action exceeded; original state retained')
            start=work.cpu.time;h=min(work.probe,end-start);trial,preview=work.trial(target(start+h),h)
            if preview['topology_changed']:
                low,high=0.,h
                while high-low>work.event_tol:
                    if time.perf_counter()-begin>wall_limit:raise TimeoutError('event bracket exceeded wall limit')
                    middle=(low+high)/2;candidate,p=work.trial(target(start+middle),middle)
                    if p['topology_changed']:high=middle;trial=candidate
                    else:low=middle
                # The upper trial is always independently proven to cover support.
                p=trial.propose(target(start+high))
                if not p['topology_changed']:raise RejectedEvent('preview/commit disagree')
                before=trial.cpu.metrics();trial.commit(p);after=trial.cpu.metrics()
                trial.activations.append({'time_s':trial.cpu.time,'bracket_s':[start+low,start+high],'bracket_width_s':high-low,'changes':p['command']['changes'],'energy_jump_J':after['energy']-before['energy'],'mass_jump_kg':after['mass']-before['mass']})
            else:
                p=trial.propose(target(start+h));trial.commit(p)
                if p['topology_changed']:raise RejectedEvent('no-event preview/commit disagree')
            trial.cost=copy.deepcopy(work.cost);work=trial
        if token!=self.fingerprint():raise RejectedEvent('concurrent action mutation')
        self.__dict__.update(work.__dict__)
        return self

    def save(self,stem):
        stem=Path(stem);self.cpu.save(stem.with_suffix('.npz'))
        meta={'schema':14,'state_sha256':hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),'blade_sha256':self.blade.sha256,'pose':self.pose.tolist(),'histories':self.histories,'commands':self.commands,'epoch':self.epoch,'dt':self.dt,'probe':self.probe,'event_tol':self.event_tol,'activations':self.activations,'cost':self.cost,'fingerprint':self.fingerprint(),'cpu_repr':str((self.cpu.time,self.cpu.steps,self.cpu.cut_count,self.cpu.events,self.cpu.config)),'piece_repr':{k:str((p.steps,p.epoch,p.keys,p.plane)) for k,p in self.cpu.pieces.items()}}
        stem.with_suffix('.json').write_text(json.dumps(meta,indent=2,allow_nan=False))
    @classmethod
    def restore(cls,stem):
        stem=Path(stem);m=json.loads(stem.with_suffix('.json').read_text())
        if m['schema']!=14 or hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest()!=m['state_sha256']:raise ValueError('checkpoint hash/schema mismatch')
        out=cls(BandSystem.restore(stem.with_suffix('.npz')),m['pose'],m['dt'],m['probe'],m['event_tol'])
        if out.blade.sha256!=m['blade_sha256']:raise ValueError('blade hash mismatch')
        for k in ['histories','commands','epoch','activations','cost']:setattr(out,k,m[k])
        return out
