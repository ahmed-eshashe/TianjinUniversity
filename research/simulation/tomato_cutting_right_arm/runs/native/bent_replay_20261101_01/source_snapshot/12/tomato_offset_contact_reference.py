"""Independent plane-contact force and world-COM wrench for two frozen proxies."""
import math
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import cross,dot


def world_point(pose,local):
    rotation=quaternion_rotation(pose[3:])
    return [p+dot(row,local) for p,row in zip(pose[:3],rotation)]


def expected_contact(pose,com_local,particle,mp,k,height,dt):
    if not all(math.isfinite(v) for v in [*particle,mp,k,height,dt]) or min(mp,k,dt)<=0:
        raise ValueError('Finite fixture inputs required')
    rotation=quaternion_rotation(pose[3:]);normal=[row[2] for row in rotation]
    delta=[a-b for a,b in zip(particle,pose[:3])];depth=height-dot(normal,delta)
    if depth<=0:raise ValueError('Initially penetrating plane contact required')
    magnitude=k*depth/(1.+k*dt*dt/mp)
    force=[magnitude*n for n in normal]
    point=[p+depth*n for p,n in zip(particle,normal)]
    com=world_point(pose,com_local);lever=[p-c for p,c in zip(point,com)]
    reaction=[-v for v in force];torque=list(cross(lever,reaction))
    return dict(soft_force=force,rigid_point=point,com_world=com,reaction_force=reaction,torque=torque,
        particle_after=[p+dt*dt*f/mp for p,f in zip(particle,force)])


def validate_wrench(expected,force,point,wrench):
    if not all(math.isfinite(v) for v in [*force,*point,*wrench]):raise ValueError('Nonfinite wrench')
    fe=math.dist(force,expected['soft_force']);pe=math.dist(point,expected['rigid_point'])
    re=math.dist(wrench[:3],expected['reaction_force']);te=math.dist(wrench[3:],expected['torque'])
    if max(fe,re)>2e-5 or pe>1e-7 or te>2e-7:raise ValueError('Contact force/point/world COM torque mismatch')
    return dict(soft_force_error_n=fe,point_error_m=pe,reaction_error_n=re,torque_error_nm=te)


def rotation_vector(initial,final):
    # final * conjugate(initial), world-frame increment; both normalized xyzw.
    a=[x/math.hypot(*initial) for x in initial];b=[x/math.hypot(*final) for x in final]
    av=[-v for v in a[:3]];bv=b[:3]
    v=[b[3]*av[i]+a[3]*bv[i]+cross(bv,av)[i] for i in range(3)]
    w=b[3]*a[3]-dot(bv,av)
    if w<0:v=[-x for x in v];w=-w
    length=math.hypot(*v)
    return [0.]*3 if length==0 else [x*2*math.atan2(length,w)/length for x in v]
