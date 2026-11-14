"""Independent one-interval reference for a frozen-proxy then PhysX schedule."""
import math


def reference(zp, zb, mp, mb, k, height, dt, body_substeps=1):
    if not all(math.isfinite(v) for v in (zp,zb,mp,mb,k,height,dt)) or min(mp,mb,k,dt)<=0:
        raise ValueError('Finite positive masses, stiffness and dt required')
    if type(body_substeps) is not int or body_substeps<1:raise ValueError('Positive integer substeps required')
    depth=max(0.,height+zb-zp)
    frozen_depth=depth/(1.+k*dt*dt/mp)
    force=k*frozen_depth
    vp=dt*force/mp;vb=-dt*force/mb
    return dict(particle_z=zp+dt*vp,body_z=zb+dt*vb*(body_substeps+1)/(2*body_substeps),particle_vz=vp,body_vz=vb,force_n=force)


def assess(zp,zb,mp,mb,k,height,dt,after,force,body_substeps=1):
    expected=reference(zp,zb,mp,mb,k,height,dt,body_substeps)
    values=list(after.values())+[force]
    if not all(math.isfinite(v) for v in values):raise ValueError('Nonfinite output')
    pe=max(abs(after[n]-expected[n]) for n in ('particle_z','body_z'))
    ve=max(abs(after[n]-expected[n]) for n in ('particle_vz','body_vz'))
    fe=abs(force-expected['force_n'])
    dp=after['particle_z']-zp;db=after['body_z']-zb;rel=dp-db
    vp=after['particle_vz'];vb=after['body_vz']
    momentum=mp*vp+mb*vb
    impulse=max(abs(mp*vp-dt*force),abs(mb*vb+dt*force))
    depth0=max(0.,height+zb-zp);depth1=max(0.,height+after['body_z']-after['particle_z'])
    kinetic=.5*mp*vp*vp+.5*mb*vb*vb
    delta_u=.5*k*(depth1*depth1-depth0*depth0)
    work=force*rel
    velocity_loss=.5*mp*vp*vp+.5*mb*vb*vb/body_substeps # semiimplicit particle and TGS body substeps
    potential_quadratic=.5*k*rel*rel
    split_work=(force-k*depth1)*rel
    work_error=abs(kinetic-work+velocity_loss)
    energy_error=abs(kinetic+delta_u+velocity_loss+potential_quadratic-split_work)
    if pe>1e-7 or ve>2e-5 or fe>2e-5 or abs(momentum)>2e-7 or impulse>2e-7 or max(work_error,energy_error)>2e-8:
        raise ValueError(f'Partitioned reference mismatch: {pe=}, {ve=}, {fe=}, {momentum=}, {impulse=}, {energy_error=}')
    return dict(expected=expected,position_error_m=pe,velocity_error_m_s=ve,force_error_n=fe,
        momentum_error_kg_m_s=abs(momentum),impulse_error_kg_m_s=impulse,
        contact_work_j=work,kinetic_energy_j=kinetic,potential_change_j=delta_u,
        velocity_numerical_loss_j=velocity_loss,potential_quadratic_term_j=potential_quadratic,
        partition_splitting_work_j=split_work,work_identity_error_j=work_error,energy_identity_error_j=energy_error,
        energy_change_j=kinetic+delta_u,final_depth_m=depth1)
