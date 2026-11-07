"""Independent 1-D backward-Euler reference for a free particle/free slab pair."""
import math


def reference_step(initial,mass_particle,mass_body,stiffness,half_height,dt):
    if not all(math.isfinite(x) and x>0 for x in (mass_particle,mass_body,stiffness,half_height,dt)):
        raise ValueError('Finite positive reference parameters required')
    zp,zb,vp,vb=[initial[k] for k in ('particle_z','body_z','particle_vz','body_vz')]
    predicted_depth=half_height+zb-zp-dt*(vp-vb)
    depth=max(0.,predicted_depth)/(1+stiffness*dt*dt*(1/mass_particle+1/mass_body))
    force=stiffness*depth
    vp1=vp+dt*force/mass_particle;vb1=vb-dt*force/mass_body
    return {'particle_z':zp+dt*vp1,'body_z':zb+dt*vb1,'particle_vz':vp1,'body_vz':vb1,
            'contact_force_n':force,'penetration_m':depth}


def assess_step(initial,final,mass_particle,mass_body,stiffness,half_height,dt):
    expected=reference_step(initial,mass_particle,mass_body,stiffness,half_height,dt)
    pos_error=max(abs(final[k]-expected[k]) for k in ('particle_z','body_z'))
    velocity_error=max(abs(final[k]-expected[k]) for k in ('particle_vz','body_vz'))
    mp,mb,k=mass_particle,mass_body,stiffness
    dp=final['particle_z']-initial['particle_z'];db=final['body_z']-initial['body_z']
    dvp=final['particle_vz']-initial['particle_vz'];dvb=final['body_vz']-initial['body_vz']
    depth0=max(0.,half_height+initial['body_z']-initial['particle_z'])
    depth1=max(0.,half_height+final['body_z']-final['particle_z'])
    f1=k*depth1
    momentum0=mp*initial['particle_vz']+mb*initial['body_vz']
    momentum1=mp*final['particle_vz']+mb*final['body_vz']
    kinetic0=.5*mp*initial['particle_vz']**2+.5*mb*initial['body_vz']**2
    kinetic1=.5*mp*final['particle_vz']**2+.5*mb*final['body_vz']**2
    potential0=.5*k*depth0**2;potential1=.5*k*depth1**2
    impulse_residual=max(abs(mp*dvp-dt*f1),abs(mb*dvb+dt*f1))
    work=f1*(dp-db)
    velocity_dissipation=.5*mp*dvp**2+.5*mb*dvb**2
    # Both fixtures remain wholly in contact or wholly clear; no activation switch.
    position_dissipation=.5*k*(depth1-depth0)**2
    work_residual=abs(kinetic1-kinetic0-work+velocity_dissipation)
    energy_residual=abs((kinetic1+potential1)-(kinetic0+potential0)+velocity_dissipation+position_dissipation)
    result={'expected':expected,'max_position_error_m':pos_error,'max_velocity_error_m_s':velocity_error,
        'momentum_initial_kg_m_s':momentum0,'momentum_final_kg_m_s':momentum1,
        'momentum_residual_kg_m_s':abs(momentum1-momentum0),'impulse_residual_n_s':impulse_residual,
        'kinetic_initial_j':kinetic0,'kinetic_final_j':kinetic1,'potential_initial_j':potential0,'potential_final_j':potential1,
        'contact_work_backward_euler_j':work,'velocity_numerical_dissipation_j':velocity_dissipation,
        'position_numerical_dissipation_j':position_dissipation,'work_identity_residual_j':work_residual,
        'energy_identity_residual_j':energy_residual,'energy_change_j':kinetic1+potential1-kinetic0-potential0}
    values=[v for v in result.values() if isinstance(v,(float,int))]
    if not all(math.isfinite(v) for v in values):raise ValueError('Nonfinite dynamic result')
    if (pos_error>1e-7 or velocity_error>2e-5 or result['momentum_residual_kg_m_s']>2e-7
        or impulse_residual>2e-7 or work_residual>2e-8 or energy_residual>2e-8):
        raise ValueError('Dynamic proxy reference mismatch: '+str(result))
    return result
