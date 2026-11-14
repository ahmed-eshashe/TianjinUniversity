"""Independent impulse/coast checks for isolated isotropic CPU PhysX proxies."""
import math


def check_pulse(before,after,force,torque,mass,inertia,dt):
    if not all(math.isfinite(v) and v>0 for v in (mass,inertia,dt)):
        raise ValueError('Positive finite mass, isotropic inertia and dt required')
    expected=[before[i]+dt*force[i]/mass for i in range(3)]
    expected += [before[i+3]+dt*torque[i]/inertia for i in range(3)]
    linear=math.dist(after[:3],expected[:3]);angular=math.dist(after[3:],expected[3:])
    if not math.isfinite(linear+angular) or linear>2e-5 or angular>2e-6:
        raise ValueError('PhysX one-shot wrench impulse mismatch')
    return {'expected_velocity_com_world':expected,'linear_velocity_error_m_s':linear,'angular_velocity_error_rad_s':angular}


def check_coast(before,after):
    linear=math.dist(before[:3],after[:3]);angular=math.dist(before[3:],after[3:])
    if not math.isfinite(linear+angular) or linear>2e-6 or angular>2e-6:
        raise ValueError('Unexpected force persistence or coast drift')
    return {'linear_velocity_change_m_s':linear,'angular_velocity_change_rad_s':angular}
