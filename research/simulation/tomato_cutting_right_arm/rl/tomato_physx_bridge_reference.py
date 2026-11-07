"""Host-only state/wrench contract for the inspected installed bridge interfaces.

No engine imports or transfer calls. Both selected pose APIs use xyzw; the
velocity is world-frame COM linear velocity followed by world angular velocity.
"""
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import vector,dot,cross


def reference_packet(pose_xyzw,velocity_com_world,com_local_m,soft_force_world_n,contact_world_m):
    if len(pose_xyzw)!=7 or len(velocity_com_world)!=6:
        raise ValueError('Pose xyz+xyzw and velocity linear+angular required')
    position=vector(pose_xyzw[:3]);rotation=quaternion_rotation(pose_xyzw[3:])
    linear=vector(velocity_com_world[:3]);angular=vector(velocity_com_world[3:])
    com=vector(com_local_m);soft_force=vector(soft_force_world_n);point=vector(contact_world_m)
    com_world=tuple(dot(axis,com)+p for axis,p in zip(rotation,position))
    lever=tuple(p-c for p,c in zip(point,com_world))
    spin=cross(angular,lever);point_velocity=tuple(v+w for v,w in zip(linear,spin))
    reaction=tuple(-f for f in soft_force);moment=cross(lever,reaction)
    return {'newton_pose_xyzw':list(pose_xyzw),'newton_velocity_com_world':list(velocity_com_world),
        'com_world_m':list(com_world),'contact_velocity_world_m_s':list(point_velocity),
        'physx_wrench':{'force_n':list(reaction),'torque_about_com_nm':list(moment),
                        'positions':None,'is_global':True},
        'native_transfer_enabled':False,
        'scope':'Reference arithmetic only. Runtime mapping, timing, CPU/GPU transfer and integration are unvalidated.'}
