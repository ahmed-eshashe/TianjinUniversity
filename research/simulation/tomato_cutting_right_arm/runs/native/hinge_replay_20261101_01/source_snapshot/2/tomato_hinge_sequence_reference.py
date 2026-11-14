"""Planar side-contact and passive-hinge partitioned-step reference."""
import math
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import dot,cross


def pose_from_joint(yaw,q,radius=.01):
    a=yaw+q
    return [radius*math.cos(a),radius*math.sin(a),0.,0.,0.,math.sin(a/2),math.cos(a/2)]


def step(before,yaw,mp,inertia,width,k,dt,pose=None):
    if min(mp,inertia,width,k,dt)<=0 or not all(math.isfinite(v) for v in [before['q'],before['qd'],*before['p'],*before['vp'],yaw,mp,inertia,width,k,dt]):
        raise ValueError('Finite hinge state and positive physical parameters required')
    pose=pose_from_joint(yaw,before['q']) if pose is None else pose
    normal=[row[1] for row in quaternion_rotation(pose[3:])]
    depth=width-dot(normal,[p-x for p,x in zip(before['p'],pose[:3])])
    magnitude=k*max(0.,depth-dt*dot(normal,before['vp']))/(1+k*dt*dt/mp) if depth>0 else 0.
    force=[magnitude*n for n in normal];point=[p+depth*n for p,n in zip(before['p'],normal)]
    reaction=[-x for x in force];torque=list(cross([p-c for p,c in zip(point,pose[:3])],reaction))
    effort=cross(point,reaction)[2]
    qd=before['qd']+dt*effort/inertia;q=before['q']+dt*before['qd']+dt*dt*effort/inertia*17/32
    vp=[v+dt*f/mp for v,f in zip(before['vp'],force)];p=[x+dt*v for x,v in zip(before['p'],vp)]
    return dict(after=dict(q=q,qd=qd,p=p,vp=vp),force=force,point=point,wrench=reaction+torque,
        effort_nm=effort,signed_depth_m=depth,normal=normal)
