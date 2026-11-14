"""Offline arithmetic audit for axis-aligned stationary box contact records.

Uses the recorded native rigid point: rigid-transform arithmetic is not replayed.
No simulation imports, state changes, or physical acceptance decisions.
"""
from fractions import Fraction
import math
import struct


def round32(value):
    """Round exact rational arithmetic to nearest binary32, ties to even.

    Restricted to finite normal-range fixture arithmetic and exact zero.
    Neighbor comparison avoids an intermediate binary64 double-rounding error.
    """
    value = Fraction(value)
    if value == 0:
        return 0.0
    sign = -1 if value < 0 else 1
    magnitude = abs(value)
    approximate = struct.unpack('>f', struct.pack('>f', float(magnitude)))[0]
    bits = struct.unpack('>I', struct.pack('>f', approximate))[0]
    candidates = []
    for b in (bits-1, bits, bits+1):
        if not 0 <= b < 0x7f800000:
            continue
        candidate = struct.unpack('>f', struct.pack('>I', b))[0]
        candidates.append((abs(Fraction(candidate)-magnitude), b & 1, candidate))
    if not candidates:
        raise ValueError('Unsupported binary32 range')
    return sign*min(candidates)[2]


def fma32(a, b, c):
    return round32(Fraction(a)*Fraction(b)+Fraction(c))


def interpolate32(points, corners, weights, *, fused):
    result = [round32(Fraction(weights[0])*Fraction(v)) for v in points[corners[0]]]
    for corner, weight in zip(corners[1:], weights[1:]):
        if corner < 0:
            continue
        for axis in range(3):
            product = Fraction(weight)*Fraction(points[corner][axis])
            result[axis] = (round32(product+Fraction(result[axis])) if fused else
                            round32(Fraction(round32(product))+Fraction(result[axis])))
    return result


def replay_stationary_axis_contact(payload, comparison, *, fused):
    arrays = payload['arrays']
    if payload['soft_contact_count'] != [1]:
        raise ValueError('Single-contact fixture required')
    normal = arrays['soft_contact_normal'][0]
    if sum(v != 0 for v in normal) != 1 or sum(v*v for v in normal) != 1:
        raise ValueError('Axis-unit normal required')
    if any(arrays['soft_contact_body_vel'][0]) or comparison['expected_mu'] != 0:
        raise ValueError('Stationary frictionless fixture required')
    row = comparison['record']
    for field, key in [('soft_contact_indices', 'corners'), ('soft_contact_barycentric', 'barycentric'),
                       ('soft_contact_normal', 'normal_world')]:
        if list(arrays[field][0]) != list(row[key]):
            raise ValueError('Saved contact inputs differ')
    exact_soft = [math.fsum(w*p[axis] for w, corner in zip(arrays['soft_contact_barycentric'][0],
                  arrays['soft_contact_indices'][0]) if corner >= 0
                  for p in [payload['particle_q_world_m'][corner]]) for axis in range(3)]
    if exact_soft != list(row['soft_point_world_m']):
        raise ValueError('Saved particle state differs')
    point = interpolate32(payload['particle_q_world_m'], arrays['soft_contact_indices'][0],
                          arrays['soft_contact_barycentric'][0], fused=fused)
    rigid = comparison['native_arrays']['rigid_point'][0]
    # One nonzero normal component means no dot-product reduction ambiguity.
    axis = next(i for i, v in enumerate(normal) if v)
    gap = round32(Fraction(normal[axis])*Fraction(round32(Fraction(point[axis])-Fraction(rigid[axis]))))
    penetration = max(0., -gap)
    magnitude = round32(Fraction(penetration)*Fraction(comparison['expected_ke']))
    force = [round32(Fraction(v)*Fraction(magnitude)) for v in normal]
    return {'soft_point_binary32_m': point, 'penetration_binary32_m': penetration,
            'replayed_force_n': force, 'matches_recorded_force_exactly': force == comparison['native_arrays']['force'][0],
            'error_from_independent_geometry_reference_n': math.dist(force, comparison['expected_force_n'])}


def separated_reference_checks(payload, comparison, *, surface_error_m, normal_error):
    """Fixture-only gates: existing geometry tolerances plus exact force replay.

    The historical geometry-to-force gate remains separately reported.
    """
    replay = replay_stationary_axis_contact(payload, comparison, fused=True)
    penetration_error = abs(replay['penetration_binary32_m']-comparison['independent_penetration_m'])
    values = (surface_error_m, normal_error, penetration_error)
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('Finite nonnegative geometry errors required')
    return {'replay': replay, 'penetration_error_m': penetration_error,
            'surface_error_m': surface_error_m, 'normal_error': normal_error,
            'geometry_passed': surface_error_m <= 1e-7 and penetration_error <= 1e-7 and normal_error <= 1e-6,
            'arithmetic_passed': replay['matches_recorded_force_exactly'],
            'historical_geometry_force_gate_passed': comparison['force_error_n'] <= 1e-5}
