"""Bent 2R initial-rest contact response, independent of engine measurements."""
from tomato_two_joint_sequence_reference import geometry,dynamics

def expected_response(yaw,q,wrench,dt):
    pose,jac=geometry(yaw,q)
    effort=[sum(jac[k][j]*wrench[k] for k in range(6)) for j in range(2)]
    matrix,bias,acc=dynamics(q,[0.,0.],effort)
    return dict(matrix=matrix,jacobian=jac,pose=pose,wrench=wrench,effort=effort,velocity=[dt*a for a in acc],position=[x+17/32*dt*dt*a for x,a in zip(q,acc)])

def coast_velocity(q,qd,dt):
    _,_,acc=dynamics(q,qd,[0.,0.])
    return [v+dt*a for v,a in zip(qd,acc)]
