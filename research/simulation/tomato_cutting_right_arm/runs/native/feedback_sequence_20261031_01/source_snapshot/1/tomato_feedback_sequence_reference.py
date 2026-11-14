"""Head-on frozen-proxy soft solve, then 16 force-driven PhysX TGS substeps."""
import math


def reference(before,mp,mb,k,height,dt,substeps=16):
    vals=[*before.values(),mp,mb,k,height,dt]
    if not all(math.isfinite(v) for v in vals) or min(mp,mb,k,dt)<=0:
        raise ValueError('Finite inputs and positive masses/stiffness/dt required')
    if type(substeps) is not int or substeps<1:raise ValueError('Positive substep count required')
    zp,zb,vp,vb=[before[n] for n in ('particle_z','body_z','particle_vz','body_vz')]
    depth=height+zb-zp
    force=k*max(0.,depth-dt*vp)/(1.+k*dt*dt/mp) if depth>0 else 0.
    ap=force/mp;ab=-force/mb
    return dict(particle_z=zp+dt*(vp+dt*ap),body_z=zb+dt*vb+dt*dt*ab*(substeps+1)/(2*substeps),
        particle_vz=vp+dt*ap,body_vz=vb+dt*ab,force_n=force)


def assess(before,after,mp,mb,k,height,dt,force,substeps=16):
    expected=reference(before,mp,mb,k,height,dt,substeps)
    if not all(math.isfinite(v) for v in [*after.values(),force]):raise ValueError('Nonfinite measured state')
    pe=max(abs(after[n]-expected[n]) for n in ('particle_z','body_z'))
    ve=max(abs(after[n]-expected[n]) for n in ('particle_vz','body_vz'))
    fe=abs(force-expected['force_n'])
    dvp=after['particle_vz']-before['particle_vz'];dvb=after['body_vz']-before['body_vz']
    momentum=mp*dvp+mb*dvb
    impulse=max(abs(mp*dvp-dt*force),abs(mb*dvb+dt*force))
    rel=(after['particle_z']-before['particle_z'])-(after['body_z']-before['body_z'])
    d0=height+before['body_z']-before['particle_z'];d1=height+after['body_z']-after['particle_z']
    dk=.5*mp*(after['particle_vz']**2-before['particle_vz']**2)+.5*mb*(after['body_vz']**2-before['body_vz']**2)
    du=.5*k*(max(d1,0.)**2-max(d0,0.)**2)
    work=force*rel;loss=.5*mp*dvp*dvp+.5*mb*dvb*dvb/substeps
    # Exact unilateral-potential correction also covers the exit interval.
    end_force=k*max(d1,0.);potential_correction=-(du+end_force*rel)
    split=(force-end_force)*rel
    we=abs(dk-work+loss);ee=abs(dk+du+loss+potential_correction-split)
    if pe>1e-7 or ve>2e-5 or fe>2e-5 or abs(momentum)>2e-7 or impulse>2e-7 or max(we,ee)>2e-8:
        raise ValueError(f'Sequence reference mismatch: {pe=}, {ve=}, {fe=}, {momentum=}, {impulse=}, {we=}, {ee=}')
    return dict(expected=expected,position_error_m=pe,velocity_error_m_s=ve,force_error_n=fe,
        momentum_increment_error_kg_m_s=abs(momentum),impulse_error_kg_m_s=impulse,
        work_identity_error_j=we,energy_identity_error_j=ee,contact_work_j=work,kinetic_change_j=dk,
        potential_change_j=du,numerical_loss_j=loss,potential_correction_j=potential_correction,
        partition_splitting_work_j=split,energy_change_j=dk+du,final_signed_depth_m=d1)
