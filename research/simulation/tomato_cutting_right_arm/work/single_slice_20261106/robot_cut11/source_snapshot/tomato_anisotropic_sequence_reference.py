"""Independent moving-plane contact and unequal-inertia TGS rigid step reference."""
import math
from tomato_offset_contact_reference import world_point
from tomato_anisotropic_reference import apply_inertia
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import cross,dot


def quat_multiply(a,b):
    c=cross(a[:3],b[:3])
    return [a[3]*b[j]+b[3]*a[j]+c[j] for j in range(3)]+[a[3]*b[3]-dot(a[:3],b[:3])]


def step(before,com,mp,mb,inertia,k,height,dt):
    if min(mp,mb,*inertia,k,dt)<=0 or not all(math.isfinite(v) for v in [*before['pose'],*before['velocity'],*before['p'],*before['vp'],*com,mp,mb,*inertia,k,height,dt]):
        raise ValueError('Finite state and positive physical scalars required')
    pose=before['pose'];p=before['p'];vp=before['vp'];v=before['velocity'];q=pose[3:]
    normal=[row[2] for row in quaternion_rotation(q)]
    local_delta=[p[j]-pose[j] for j in range(3)];depth=height-dot(normal,local_delta)
    magnitude=k*max(0.,depth-dt*dot(normal,vp))/(1.+k*dt*dt/mp) if depth>0 else 0.
    f=[magnitude*x for x in normal];point=[p[j]+depth*normal[j] for j in range(3)]
    c0=world_point(pose,com);reaction=[-x for x in f];tau=list(cross([point[j]-c0[j] for j in range(3)],reaction))
    pv=[vp[j]+dt*f[j]/mp for j in range(3)];pn=[p[j]+dt*pv[j] for j in range(3)]
    spin=apply_inertia(pose,inertia,v[3:])
    gyro=cross(v[3:],spin)
    alpha=apply_inertia(pose,inertia,[tau[j]-gyro[j] for j in range(3)],inverse=True)
    bv=[v[j]+dt*reaction[j]/mb for j in range(3)];omega=[v[j+3]+dt*alpha[j] for j in range(3)]
    cn=[c0[j]+dt*v[j]+dt*dt*reaction[j]/mb*17/32 for j in range(3)]
    for substep in range(1,17):
        w=[v[j+3]+substep/16*dt*alpha[j] for j in range(3)]
        angle=math.hypot(*w)*dt/16
        scale=dt/32 if angle==0 else math.sin(angle/2)/math.hypot(*w)
        dq=[x*scale for x in w]+[math.cos(angle/2)]
        q=quat_multiply(dq,q);norm=math.hypot(*q);q=[x/norm for x in q]
    rc=world_point([0.,0.,0.]+q,com)
    final=dict(pose=[cn[j]-rc[j] for j in range(3)]+q,velocity=bv+omega,p=pn,vp=pv)
    return dict(after=final,normal=normal,signed_depth_m=depth,force=f,point=point,wrench=reaction+tau,com_world=c0,angular_reference='Frozen initial world inertia and explicit gyro over one short interval; TGS force schedule. Not a general exact PhysX integrator.')
