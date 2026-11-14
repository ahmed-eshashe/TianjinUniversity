"""Independent local +Y plane contact for the passive-hinge coupling check."""
import math
from tomato_reaction_metadata import quaternion_rotation
from tomato_offset_contact_reference import world_point
from tomato_wrench_contract import dot,cross


def expected_contact(pose,particle,mass,half_width,stiffness,dt):
    if min(mass,half_width,stiffness,dt)<=0:raise ValueError('Positive contact parameters required')
    rotation=quaternion_rotation(pose[3:]);normal=[row[1] for row in rotation]
    depth=half_width-dot(normal,[p-x for p,x in zip(particle,pose[:3])])
    if not math.isfinite(depth) or depth<=0:raise ValueError('Initially penetrating side contact required')
    f=stiffness*depth/(1+stiffness*dt*dt/mass)
    force=[f*v for v in normal];point=[p+depth*n for p,n in zip(particle,normal)]
    reaction=[-x for x in force];moment=list(cross([p-c for p,c in zip(point,pose[:3])],reaction))
    return dict(force=force,point=point,wrench=reaction+moment,
        particle_after=[p+dt*dt*v/mass for p,v in zip(particle,force)],velocity=[dt*v/mass for v in force])
