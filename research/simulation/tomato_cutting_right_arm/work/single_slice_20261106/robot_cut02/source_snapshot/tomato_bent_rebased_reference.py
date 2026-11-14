"""Reference conversion for zero coordinates at the same physical bent rest pose."""
import math
from tomato_two_joint_sequence_reference import dynamics as physical_dynamics
from tomato_bent_origin_reference import step as physical_step,origin_for
REST=[math.pi/6,-math.pi/3]
def physical_angles(q):return [x+r for x,r in zip(q,REST)]
def dynamics(q,qd,effort):return physical_dynamics(physical_angles(q),qd,effort)
def step(before,yaw,mp,width,k,dt,origin,pose=None):
    converted=dict(before,q=physical_angles(before['q']))
    result=physical_step(converted,yaw,mp,width,k,dt,origin,pose=pose)
    result['after']['q']=[x-r for x,r in zip(result['after']['q'],REST)]
    return result
