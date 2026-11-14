"""Disabled native-format preview and complete-stream snapshot reader.

No Warp import, engine buffer write, native capture, force evaluation or solver
launch is provided. Hashes bind snapshot contents, not runtime authenticity.
"""
import hashlib
import json
import math
import struct
from tomato_mesh_contact_contract import review_batch, review_record, _transform
from tomato_wrench_contract import vector, dot

ARRAY_FIELDS = ('soft_contact_particle', 'soft_contact_indices', 'soft_contact_barycentric',
                'soft_contact_shape', 'soft_contact_body_pos', 'soft_contact_body_vel', 'soft_contact_normal')
FLOAT_FIELDS = ('soft_contact_barycentric', 'soft_contact_body_pos', 'soft_contact_body_vel', 'soft_contact_normal')


def _f32(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('Finite scalar required')
    try:
        result = struct.unpack('<f', struct.pack('<f', value))[0]
    except (OverflowError, struct.error) as exc:
        raise ValueError('Float32 overflow') from exc
    if not math.isfinite(result):
        raise ValueError('Nonfinite float32 conversion')
    return result


def _i32(value):
    if type(value) is not int or not -(2**31) <= value < 2**31:
        raise ValueError('Int32 value required')
    return value


def _digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _identity(identity):
    for name in ('run_id', 'episode_id'):
        if not isinstance(identity.get(name), str) or not identity[name]:
            raise ValueError('Run and episode identity required')
    if type(identity.get('step')) is not int or identity['step'] < 0:
        raise ValueError('Nonnegative step required')
    if any(type(identity.get(k)) not in (int, float) or not math.isfinite(identity[k]) for k in ('start_s', 'dt_s')):
        raise ValueError('Finite interval required')
    if identity['start_s'] < 0 or identity['dt_s'] <= 0:
        raise ValueError('Valid interval required')
    pins = identity.get('source_sha256')
    if not isinstance(pins, dict) or not pins:
        raise ValueError('Source pins required')
    if any(not isinstance(k, str) or not isinstance(h, str) or len(h) != 64 or
           any(c not in '0123456789abcdef' for c in h) for k, h in pins.items()):
        raise ValueError('SHA-256 source pins required')


def preview_buffers(records, context, identity, *, global_capacity, body_capacity, observed_dynamic_adjacency):
    """Convert reviewed raw records to float32/int32 active-prefix lists only.

    Does not reduce records, renormalize values, inflate the surface, or populate
    native replay slots. Conversion errors are reported without qualification.
    """
    _identity(identity)
    if identity['step'] != context['step'] or identity['dt_s'] != context['dt_s']:
        raise ValueError('Context and snapshot interval differ')
    review = review_batch(records, context, global_capacity=global_capacity, body_capacity=body_capacity,
                          observed_dynamic_adjacency=observed_dynamic_adjacency)
    arrays = {key: [] for key in ARRAY_FIELDS}; errors = {key: 0. for key in FLOAT_FIELDS}
    for record in records:
        row = review_record(record, context)
        arrays['soft_contact_particle'].append(_i32(row['corners'][0] if record['feature'] == 'particle' else -1))
        arrays['soft_contact_indices'].append([_i32(i) for i in row['corners']])
        arrays['soft_contact_shape'].append(_i32(row['shape_id']))
        source = {'soft_contact_barycentric': row['weights'], 'soft_contact_body_pos': row['rigid_surface_body_m'],
                  'soft_contact_body_vel': row['rigid_surface_velocity_body_m_s'], 'soft_contact_normal': row['normal_world']}
        for field, values in source.items():
            converted = [_f32(v) for v in values]
            errors[field] = max(errors[field], *(abs(a-b) for a, b in zip(converted, values)))
            arrays[field].append(converted)
    shape_body = [-1]*(context['shape_id']+1); shape_body[context['shape_id']] = context['body_id']
    payload = {'identity': identity, 'origin': 'synthetic_reference_preview', 'soft_contact_count': [len(records)],
               'soft_contact_max': global_capacity, 'active_prefix_only': True, 'arrays': arrays,
               'shape_body': shape_body, 'particle_q_world_m': [[_f32(v) for v in p] for p in context['particles_world_m']],
               'record_ids': [r['id'] for r in records],
               'dynamic_adjacency_observed': observed_dynamic_adjacency,
               'conversion_max_absolute_error_by_field': errors,
               'conversion_qualified': False, 'native_buffer_write_enabled': False,
               'solver_launch_enabled': False, 'native_runtime_validated': False,
               'missing_native_bindings': ['owned live-state capture/IPC', 'replay tids allocation',
                                           'float32 error acceptance policy', 'complete native history/reset registry'],
               'reference_duplicate_report': review['exact_duplicate_events']}
    return {'payload': payload, 'sha256': _digest(payload)}


def collect_snapshot_contacts(envelope, expected_identity, context, *, target_body, collector_capacity):
    """Validate the global active prefix before filtering by rigid body.

    Dynamic solver adjacency is intentionally unused. Reading the snapshot does
    not prove candidate completeness, physical normal/penetration or reactions.
    """
    _identity(expected_identity)
    p = envelope['payload']
    if _digest(p) != envelope['sha256']:
        raise ValueError('Snapshot content hash mismatch')
    if p['identity'] != expected_identity or expected_identity['step'] != context['step'] or expected_identity['dt_s'] != context['dt_s']:
        raise ValueError('Stale run/episode/step/source/interval snapshot')
    if type(target_body) is not int or target_body != context['body_id']:
        raise ValueError('Explicit target-body context required')
    count_view = p['soft_contact_count']; capacity = p['soft_contact_max']
    if not isinstance(count_view, list) or len(count_view) != 1:
        raise ValueError('Single native count view required')
    count = _i32(count_view[0]); _i32(capacity)
    if count < 0 or capacity <= 0 or count >= capacity:
        raise ValueError('Invalid or saturated raw contact count')
    if type(collector_capacity) is not int or collector_capacity <= 0:
        raise ValueError('Positive collector capacity required')
    arrays = p['arrays']
    if any(not isinstance(arrays.get(k), list) or len(arrays[k]) < count for k in ARRAY_FIELDS):
        raise ValueError('Truncated contact field')
    particles = p['particle_q_world_m']
    for point in particles:
        vector(point)
        if any(_f32(v) != v for v in point):
            raise ValueError('Snapshot particle values must represent float32')
    result = []
    for index in range(count):
        corners = arrays['soft_contact_indices'][index]
        if not isinstance(corners, list) or len(corners) != 3:
            raise ValueError('Three native corner indices required')
        for corner in corners: _i32(corner)
        size = 1 if corners[1:] == [-1, -1] else 2 if corners[2] == -1 else 3
        if any(not 0 <= i < len(particles) for i in corners[:size]) or any(i != -1 for i in corners[size:]) or len(set(corners[:size])) != size:
            raise ValueError('Invalid corner registry or padding')
        shape = _i32(arrays['soft_contact_shape'][index])
        if not 0 <= shape < len(p['shape_body']):
            raise ValueError('Invalid global contact shape mapping')
        body = _i32(p['shape_body'][shape])
        if body < -1:
            raise ValueError('Invalid body mapping')
        particle = _i32(arrays['soft_contact_particle'][index])
        if particle != (corners[0] if size == 1 else -1):
            raise ValueError('Particle-only view disagrees with unified record')
        values = {}
        for field in FLOAT_FIELDS:
            values[field] = vector(arrays[field][index])
            if any(_f32(v) != v for v in values[field]):
                raise ValueError('Native vector values must represent float32')
        weights = values['soft_contact_barycentric']; normal = values['soft_contact_normal']
        if any(w < 0 for w in weights) or any(w != 0 for w in weights[size:]) or math.fsum(weights) <= 0 or math.hypot(*normal) == 0:
            raise ValueError('Invalid raw weights or normal')
        # Validate even foreign-body records; filtering must not hide bad input.
        if body != target_body:
            continue
        if shape != context['shape_id']:
            raise ValueError('Isolated target shape context mismatch')
        world = _transform(values['soft_contact_body_pos'], context['body_to_world'])
        soft = tuple(math.fsum(weights[j]*particles[corners[j]][k] for j in range(size)) for k in range(3))
        projected_gap = dot(normal, tuple(a-b for a, b in zip(soft, world)))
        result.append({'global_index': index, 'shape_id': shape, 'body_id': body, 'corners': corners,
                       'barycentric': list(weights), 'soft_point_world_m': soft,
                       'raw_rigid_surface_world_m': world, 'normal_world': normal,
                       'body_surface_velocity_body_m_s': values['soft_contact_body_vel'],
                       'barycentric_sum_error': math.fsum(weights)-1., 'normal_length_error': math.hypot(*normal)-1.,
                       'projected_gap_from_rounded_snapshot_m': projected_gap})
    if len(result) >= collector_capacity:
        raise ValueError('Collector saturated; no silent truncation')
    return {'global_prefix_records_checked': count, 'target_records': result,
            'target_count': len(result), 'complete_prefix_read': True,
            'dynamic_adjacency_used': False, 'conversion_qualified': False,
            'pose_source': 'provided reference context; owned native pose capture not implemented',
            'native_runtime_validated': False, 'reaction_force_evaluated': False,
            'solver_launch_enabled': False}
