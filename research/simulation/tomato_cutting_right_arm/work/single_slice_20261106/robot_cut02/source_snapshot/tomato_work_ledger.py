"""Offline work-accounting reference; no simulator/constitutive law changes.

All channels are SI. Positive external work enters the material system.
Gravity is included in stored potential energy, not counted again as work.
This is a specified quadrature and ledger check, not a native physics pass.
"""
from dataclasses import dataclass
import math
from tomato_load_samples import validate_sequence
from tomato_wrench_contract import power, vector


@dataclass(frozen=True)
class StepMotion:
    step: int
    start_s: float
    dt_s: float
    body: str
    origin_world_m: tuple
    velocity_world_m_s: tuple
    angular_velocity_world_rad_s: tuple


def finite(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Finite SI energy required')
    return value


def integrate_work(samples, motions, *, convention):
    """Step-average load dot declared constant step twist times dt.

    Force/motion are ON and OF the same named body at the same world origin.
    For an actuator balancing contact reaction, negate the contact load first.
    This rule is not exact for unknown within-step load/velocity covariance;
    native timestep/refinement checks remain necessary.
    """
    if convention != 'step_average_load_constant_twist':
        raise ValueError('Unsupported or undeclared quadrature convention')
    validate_sequence(samples)
    if len(samples) != len(motions):
        raise ValueError('Load and motion samples must be complete')
    increments = []
    for load, motion in zip(samples, motions):
        for name in ('step', 'start_s', 'dt_s', 'body', 'origin_world_m'):
            if getattr(load, name) != getattr(motion, name):
                raise ValueError('Mismatched motion sample: ' + name)
        inc = power(load.force_n, load.moment_nm,
                    vector(motion.velocity_world_m_s),
                    vector(motion.angular_velocity_world_rad_s)) * load.dt_s
        increments.append(finite(inc))
    return {'work_j': finite(math.fsum(increments)), 'increments_j': increments,
            'quadrature': convention, 'runtime_physics_validated': False}


def energy_balance(*, initial_energy_j, final_energy_j, external_work_j,
                   dissipation_j, relative_tolerance, absolute_tolerance_j):
    """Return a dimensionally consistent signed residual with separate channels.

    Existing offline 1% / 1e-12 J ceilings cannot be loosened via this helper.
    No automatic native solver tolerance selection is implied by these ceilings.
    Caller supplies all channels explicitly, including zeros, and must choose
    the reference system before using this helper.
    """
    stored = {'elastic', 'kinetic', 'gravitational'}
    external = {'tool', 'fixture', 'other_external'}
    dissipated = {'fracture', 'friction', 'damping'}
    for mapping, keys in [(initial_energy_j, stored), (final_energy_j, stored),
                          (external_work_j, external), (dissipation_j, dissipated)]:
        if set(mapping) != keys:
            raise ValueError('Missing, duplicated or unsupported ledger channels')
        for value in mapping.values():
            finite(value)
    if any(finite(x) < 0 for x in dissipation_j.values()):
        raise ValueError('Dissipation cannot be negative')
    for mapping in (initial_energy_j, final_energy_j):
        if finite(mapping['elastic']) < 0 or finite(mapping['kinetic']) < 0:
            raise ValueError('Elastic and kinetic energies cannot be negative')
    rel, absolute = finite(relative_tolerance), finite(absolute_tolerance_j)
    if not 0 <= rel <= .01 or not 0 <= absolute <= 1e-12:
        raise ValueError('Tolerance cannot exceed existing offline ceilings')
    delta = finite(math.fsum(float(final_energy_j[k])-float(initial_energy_j[k]) for k in stored))
    work = finite(math.fsum(map(float, external_work_j.values())))
    loss = finite(math.fsum(map(float, dissipation_j.values())))
    residual = finite(work - delta - loss)
    scale = max(abs(work), abs(delta) + loss)
    allowed = finite(absolute + rel * scale)
    return {'balanced': abs(residual) <= allowed, 'external_work_j': work,
            'stored_energy_change_j': delta, 'dissipation_j': loss,
            'residual_j': residual, 'scale_j': scale, 'allowed_error_j': allowed,
            'relative_residual': abs(residual)/scale if scale else None,
            'zero_activity': scale == 0, 'runtime_physics_validated': False}
