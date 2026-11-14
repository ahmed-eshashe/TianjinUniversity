"""SI frames, rigid endpoint interpolation and once-only wrench chronology."""
import numpy as np
from scipy.spatial.transform import Rotation

def pose_matrix(pose):
    pose=np.asarray(pose,float)
    if pose.shape!=(7,) or not np.isfinite(pose).all():raise ValueError('Invalid measured pose')
    T=np.eye(4);T[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();T[:3,3]=pose[:3];return T

def average_wrench(linear_impulse,angular_impulse,dt,Q,anchor,com):
    if not np.isfinite(dt) or dt<=0:raise ValueError('Invalid physical interval')
    Q=np.asarray(Q,float);f=Q@np.asarray(linear_impulse,float)/dt
    m=Q@np.asarray(angular_impulse,float)/dt+np.cross(np.asarray(anchor)-np.asarray(com),f)
    w=np.r_[f,m]
    if not np.isfinite(w).all():raise ValueError('Nonfinite exchanged wrench')
    return w

class ExchangeClock:
    def __init__(self):self.step=0;self.time=0.;self.queued=-1
    def accept(self,step,start,dt):
        if step!=self.step or abs(start-self.time)>1e-10 or dt<=0:raise ValueError('Repeated, delayed or missing material interval')
        self.step+=1;self.time+=dt
    def queue_once(self,step):
        if step!=self.step-1 or step<=self.queued:raise ValueError('Duplicate or stale native force queue')
        self.queued=step
    def reset(self):self.__init__()
