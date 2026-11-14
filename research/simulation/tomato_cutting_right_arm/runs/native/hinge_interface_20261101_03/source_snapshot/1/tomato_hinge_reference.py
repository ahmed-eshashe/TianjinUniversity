"""Passive planar hinge response to a world force at COM and COM torque."""
import math
from tomato_wrench_contract import cross,dot


def expected_pulse(mass,com_inertia,lever,force,torque,axis,dt):
    if min(mass,com_inertia,dt)<=0 or not all(math.isfinite(v) for v in [mass,com_inertia,dt,*lever,*force,*torque,*axis]):raise ValueError('Finite positive hinge fixture inputs required')
    if abs(math.hypot(*axis)-1.)>1e-8:raise ValueError('Unit hinge axis required')
    radius_sq=dot(lever,lever)-dot(lever,axis)**2
    inertia=com_inertia+mass*radius_sq
    moment=cross(lever,force);effort=dot(axis,[moment[j]+torque[j] for j in range(3)])
    return dict(effective_inertia_kg_m2=inertia,generalized_effort_nm=effort,
        joint_velocity_rad_s=dt*effort/inertia,joint_position_rad=dt*dt*effort/inertia*17/32)


def check(expected,mass_matrix,q,qd):
    errors=dict(mass_matrix_error_kg_m2=abs(mass_matrix-expected['effective_inertia_kg_m2']),
        joint_position_error_rad=abs(q-expected['joint_position_rad']),joint_velocity_error_rad_s=abs(qd-expected['joint_velocity_rad_s']))
    if not all(math.isfinite(v) for v in errors.values()) or errors['mass_matrix_error_kg_m2']>1e-8 or errors['joint_position_error_rad']>1e-6 or errors['joint_velocity_error_rad_s']>2e-5:
        raise ValueError(f'Hinge response mismatch: {errors}')
    return errors
