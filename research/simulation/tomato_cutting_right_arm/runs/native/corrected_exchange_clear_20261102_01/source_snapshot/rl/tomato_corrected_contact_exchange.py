"""Once-only accepted-force handoff; no dynamics, state writes or implicit work claims.

Forces are accepted Newton nodal forces on the target at world positions.
The tool receives the opposite impulse, averaged over one measured robot block.
Geometry COM and Native application COM are explicit distinct world origins.
"""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class ContactExchangeRequest:
    block_id: str
    time_start_s: float
    time_end_s: float
    body_id: int
    geometry_com_world: tuple
    native_com_world: tuple
    reaction_impulse_world: tuple
    requested_native_com_wrench: tuple
    actual_float32_queue_wrench: tuple
    target_steps: int

class AcceptedContactExchange:
    def __init__(self,*,block_id,time_start_s,robot_dt_s,target_dt_s,body_id,geometry_com_world,native_com_world):
        self.block_id=str(block_id);self.start=float(time_start_s);self.robot_dt=float(robot_dt_s);self.target_dt=float(target_dt_s);self.body_id=int(body_id)
        self.cp=np.asarray(geometry_com_world,float).copy();self.cn=np.asarray(native_com_world,float).copy()
        if not self.block_id or self.body_id<0 or self.cp.shape!=(3,)or self.cn.shape!=(3,)or not np.isfinite(np.r_[self.cp,self.cn,self.start,self.robot_dt,self.target_dt]).all()or self.start<0 or self.robot_dt<=0 or self.target_dt<=0:raise ValueError('Finite explicit frame, clock and tool identity required')
        self.n=int(round(self.robot_dt/self.target_dt))
        if self.n<1 or abs(self.n*self.target_dt-self.robot_dt)>1e-15:raise ValueError('Robot interval must be an integer target subcycle count')
        self.count=0;self.impulse=np.zeros(6);self.closed=False;self.queue_attempted=False;self.request=None
    def accept(self,*,time_start_s,time_end_s,points_world,target_nodal_force,pressure_reaction_at_geometry_com,maximum_penetration_m):
        if self.closed or self.count>=self.n:raise ValueError('Closed or overfilled exchange block')
        a=float(time_start_s);b=float(time_end_s);expected=self.start+self.count*self.target_dt
        if not np.isfinite([a,b,maximum_penetration_m]).all()or abs(a-expected)>1e-15 or abs(b-a-self.target_dt)>1e-15:raise ValueError('Accepted target interval has a gap, overlap or wrong clock')
        x=np.asarray(points_world,float);f=np.asarray(target_nodal_force,float);w=np.asarray(pressure_reaction_at_geometry_com,float)
        if x.ndim!=2 or x.shape[1]!=3 or f.shape!=x.shape or w.shape!=(6,)or not all(np.isfinite(v).all()for v in [x,f,w]):raise ValueError('Finite matching accepted pressure arrays required')
        expected_w=np.r_[-f.sum(0),-np.cross(x-self.cp,f).sum(0)]
        if np.linalg.norm(w[:3]-expected_w[:3])>1e-9 or np.linalg.norm(w[3:]-expected_w[3:])>1e-10:raise ValueError('Pressure reaction sign/origin differs from accepted nodal force')
        native=w.copy();native[3:]+=np.cross(self.cp-self.cn,w[:3])
        if maximum_penetration_m<0 or maximum_penetration_m>.0001 or np.linalg.norm(native[:3])>.01 or np.linalg.norm(native[3:])>.0002:raise ValueError('Original contact penetration/force/moment stop exceeded')
        self.impulse+=self.target_dt*w;self.count+=1
    def finish(self):
        if self.closed or self.count!=self.n:raise ValueError('Incomplete or already finalized accepted block')
        w=self.impulse/self.robot_dt;native=w.copy();native[3:]+=np.cross(self.cp-self.cn,w[:3]);quantized=native.astype(np.float32).astype(float)
        if np.linalg.norm(quantized[:3])>.01 or np.linalg.norm(quantized[3:])>.0002:raise ValueError('Actual float32 queue would exceed original force/moment stop')
        self.request=ContactExchangeRequest(self.block_id,self.start,self.start+self.robot_dt,self.body_id,tuple(self.cp),tuple(self.cn),tuple(self.impulse),tuple(native),tuple(quantized),self.count);self.closed=True;return self.request
    def queue_once(self,callback):
        if not self.closed or self.request is None or self.queue_attempted:raise ValueError('Request must be complete and may be queued at most once')
        # Fail closed even if the callback partially mutates the external queue then raises.
        self.queue_attempted=True;callback(self.request);return self.request

class CorrectedRobotContactQueue:
    """Bind one tool request to the existing world's instantaneous COM queue.

    Call after AppLauncher. This queues only; the caller owns controller writes,
    exactly one PhysX step, queue-consumption checks, work ledger and chronology.
    There is deliberately no J-transpose effort path in this binding.
    """
    def __init__(self,robot,tool_body_id):self.robot=robot;self.tool_body_id=int(tool_body_id);self.block_ids=set()
    def __call__(self,request):
        if request.body_id!=self.tool_body_id or request.block_id in self.block_ids:raise ValueError('Wrong tool or repeated block identity')
        r=self.robot
        if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError('Existing external wrench would make the handoff ambiguous')
        self.block_ids.add(request.block_id)
        import torch
        w=np.array(request.actual_float32_queue_wrench)
        r.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor(w[:3][None,None],dtype=torch.float32),torques=torch.tensor(w[3:][None,None],dtype=torch.float32),positions=None,body_ids=[self.tool_body_id],is_global=True)
        if not r.instantaneous_wrench_composer.active:raise ValueError('Native instantaneous COM wrench queue did not activate')
