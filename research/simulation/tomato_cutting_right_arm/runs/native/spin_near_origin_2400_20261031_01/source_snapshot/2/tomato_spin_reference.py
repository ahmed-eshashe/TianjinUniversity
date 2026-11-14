"""Continuous torque-free Euler equations with RK4; independent of PhysX."""
import math
from tomato_turning_sequence_reference import quat_multiply
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import cross,dot


def rotate(q,v):return [dot(row,v) for row in quaternion_rotation(q)]


def body_vector(q,v):
    r=quaternion_rotation(q)
    return [sum(r[j][i]*v[j] for j in range(3)) for i in range(3)]


def invariants(q,omega_world,principal):
    w=body_vector(q,omega_world);local_l=[i*v for i,v in zip(principal,w)]
    return dict(angular_momentum=rotate(q,local_l),energy=.5*dot(w,local_l))


def advance(q,wbody,principal,dt,substeps=16):
    if len(principal)!=3 or len(wbody)!=3 or len(q)!=4 or min(principal)<=0 or not math.isfinite(dt) or dt<=0 or type(substeps)is not int or substeps<1:
        raise ValueError('Valid finite free-spin inputs required')
    if not all(math.isfinite(x) for x in [*q,*wbody,*principal]):raise ValueError('Nonfinite spin state')
    def deriv(y):
        w=y[4:];iw=[principal[j]*w[j] for j in range(3)];gy=cross(w,iw)
        dq=quat_multiply(y[:4],w+[0.])
        return [.5*v for v in dq]+[-gy[j]/principal[j] for j in range(3)]
    y=list(q)+list(wbody);h=dt/substeps
    for _ in range(substeps):
        a=deriv(y);b=deriv([v+.5*h*d for v,d in zip(y,a)])
        c=deriv([v+.5*h*d for v,d in zip(y,b)]);d=deriv([v+h*dv for v,dv in zip(y,c)])
        y=[v+h*(a[j]+2*b[j]+2*c[j]+d[j])/6 for j,v in enumerate(y)]
        norm=math.hypot(*y[:4]);y[:4]=[v/norm for v in y[:4]]
    return dict(q=y[:4],wbody=y[4:],omega_world=rotate(y[:4],y[4:]))
