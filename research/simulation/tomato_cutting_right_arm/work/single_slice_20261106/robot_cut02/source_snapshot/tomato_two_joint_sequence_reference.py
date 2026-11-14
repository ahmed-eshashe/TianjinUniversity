"""Short-step planar two-link dynamics and partitioned side-contact reference."""
import math
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import dot,cross

def geometry(yaw,q):
    a=yaw+q[0];b=a+q[1]
    p=[.02*math.cos(a)+.01*math.cos(b),.02*math.sin(a)+.01*math.sin(b),0.]
    pose=p+[0.,0.,math.sin(b/2),math.cos(b/2)]
    jac=[[-.02*math.sin(a)-.01*math.sin(b),-.01*math.sin(b)],[.02*math.cos(a)+.01*math.cos(b),.01*math.cos(b)],[0.,0.],[0.,0.],[0.,0.],[1.,1.]]
    return pose,jac

def dynamics(q,qd,effort):
    c=math.cos(q[1]);h=.02*.02*.01*math.sin(q[1])
    matrix=[[.000212+.000008*c,.000102+.000004*c],[.000102+.000004*c,.000102]]
    bias=[-h*(2*qd[0]*qd[1]+qd[1]**2),h*qd[0]**2]
    a,b=matrix[0];_,d=matrix[1];det=a*d-b*b
    u=[effort[i]-bias[i] for i in range(2)]
    return matrix,bias,[(d*u[0]-b*u[1])/det,(a*u[1]-b*u[0])/det]

def step(before,yaw,mp,width,k,dt,pose=None):
    analytic,jac=geometry(yaw,before['q']);pose=analytic if pose is None else pose
    normal=[row[1] for row in quaternion_rotation(pose[3:])]
    depth=width-dot(normal,[p-x for p,x in zip(before['p'],pose[:3])])
    magnitude=k*max(0.,depth-dt*dot(normal,before['vp']))/(1+k*dt*dt/mp) if depth>0 else 0.
    force=[magnitude*n for n in normal];point=[p+depth*n for p,n in zip(before['p'],normal)]
    reaction=[-f for f in force];torque=list(cross([p-c for p,c in zip(point,pose[:3])],reaction));wrench=reaction+torque
    effort=[sum(jac[i][j]*wrench[i] for i in range(6)) for j in range(2)]
    matrix,bias,acc=dynamics(before['q'],before['qd'],effort)
    qd=[v+dt*a for v,a in zip(before['qd'],acc)]
    q=[q+dt*v+17/32*dt*dt*a for q,v,a in zip(before['q'],before['qd'],acc)]
    vp=[v+dt*f/mp for v,f in zip(before['vp'],force)];p=[x+dt*v for x,v in zip(before['p'],vp)]
    return dict(after=dict(q=q,qd=qd,p=p,vp=vp),force=force,point=point,wrench=wrench,effort_nm=effort,matrix=matrix,bias=bias,signed_depth_m=depth,normal=normal)
