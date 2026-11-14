"""Independent planar 2R initial-rest reference; stdlib only."""
import math

def reference(angle=0.,dt=1/2400):
    m=.02;r=.01;l=.02;iz=.0001
    matrix=[[2*iz+m*r*r+m*(l*l+r*r+2*l*r),iz+m*(r*r+l*r)],[iz+m*(r*r+l*r),iz+m*r*r]]
    jac=[[-.03*math.sin(angle),-.01*math.sin(angle)],[.03*math.cos(angle),.01*math.cos(angle)],[0.,0.],[0.,0.],[0.,0.],[1.,1.]]
    wrench=[-3*math.sin(angle),3*math.cos(angle),0.,0.,0.,.0012]
    effort=[sum(jac[k][j]*wrench[k] for k in range(6)) for j in range(2)]
    a,b=matrix[0];_,d=matrix[1];det=a*d-b*b
    assert det>0 and a>0
    acc=[(d*effort[0]-b*effort[1])/det,(a*effort[1]-b*effort[0])/det]
    return dict(matrix=matrix,jacobian=jac,wrench=wrench,effort=effort,velocity=[dt*x for x in acc],position=[17/32*dt*dt*x for x in acc])

def check(ref,matrix,jac,q,qd):
    errors=dict(matrix=max(abs(matrix[i][j]-ref['matrix'][i][j]) for i in range(2) for j in range(2)),
        jacobian=max(abs(jac[i][j]-ref['jacobian'][i][j]) for i in range(6) for j in range(2)),
        position=max(abs(q[i]-ref['position'][i]) for i in range(2)),velocity=max(abs(qd[i]-ref['velocity'][i]) for i in range(2)))
    gates=dict(matrix=1e-8,jacobian=1e-6,position=1e-6,velocity=2e-5)
    if any(errors[k]>gates[k] for k in errors):raise ValueError(f'Two-joint reference mismatch: {errors}')
    return errors
