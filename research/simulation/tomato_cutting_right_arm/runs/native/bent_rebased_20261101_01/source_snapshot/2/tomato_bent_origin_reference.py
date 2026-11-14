"""Translation-aware wrapper around the unchanged planar contact reference."""
from tomato_two_joint_sequence_reference import step as local_step,geometry
from tomato_offset_contact_reference import world_point

def origin_for(yaw,q):
    pose,_=geometry(yaw,q)
    return [-v for v in world_point(pose,[.004,.004,0.])]

def step(before,yaw,mp,width,k,dt,origin,pose=None):
    local=dict(before,p=[x-o for x,o in zip(before['p'],origin)])
    local_pose=None if pose is None else [x-o for x,o in zip(pose[:3],origin)]+pose[3:]
    result=local_step(local,yaw,mp,width,k,dt,pose=local_pose)
    result['after']['p']=[x+o for x,o in zip(result['after']['p'],origin)]
    result['point']=[x+o for x,o in zip(result['point'],origin)]
    return result
