"""Host error-gate classification for a measurement audit, never hides a failed gate."""
import math

LIMITS=dict(angular_velocity_rad_s=2e-4,rotation_rad=2e-5,relative_angular_momentum=2e-4,
    relative_energy=2e-4,linear_velocity_m_s=2e-6,com_position_m=1e-7)
FIELDS=dict(angular_velocity_rad_s='angular_velocity_error_rad_s',rotation_rad='rotation_error_rad',
    relative_angular_momentum='relative_angular_momentum_drift',relative_energy='relative_energy_drift',
    linear_velocity_m_s='linear_velocity_error_m_s',com_position_m='com_position_error_m')


def violations(sample,gyro_enabled):
    if not all(math.isfinite(sample[f]) and sample[f]>=0 for f in FIELDS.values()):raise ValueError('Invalid measurement')
    checked=list(FIELDS) if gyro_enabled else ['linear_velocity_m_s','com_position_m']
    return [key for key in checked if sample[FIELDS[key]]>LIMITS[key]]
