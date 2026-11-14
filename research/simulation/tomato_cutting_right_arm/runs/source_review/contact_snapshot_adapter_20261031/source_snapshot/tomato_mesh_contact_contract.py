"""Float64 reference contact-record checks. No native writer or force launch."""
import math
from tomato_wrench_contract import cross, dot, rotation, vector

NUMERIC_ATOL = 1e-12  # Reference arithmetic only; not a physical/native tolerance.


def _close(actual, expected, label):
    if abs(actual-expected) > NUMERIC_ATOL:
        raise ValueError(label+' mismatch')


def _weights(values, size):
    if not isinstance(values, (list, tuple)) or len(values) != 3:
        raise ValueError('Three barycentric weights required')
    w = vector(values)
    if any(x < 0 for x in w) or any(x != 0 for x in w[size:]):
        raise ValueError('Nonnegative active weights and zero padding required')
    _close(math.fsum(w), 1., 'Barycentric sum')
    return w


def _transform(point, transform):
    r = rotation(transform['rotation']); t = vector(transform['translation_m'])
    return tuple(dot(row, point)+offset for row, offset in zip(r, t))


def _blend(points, weights):
    return tuple(math.fsum(w*p[k] for w, p in zip(weights, points)) for k in range(3))


def review_record(record, context):
    """Check one disclosed particle/edge/face reference record against geometry.

    Raw rigid point is body-local; normal is world outward; shape margin and
    maximum participating particle radius enter the projected gap exactly once.
    A face normal is a reference convention, not a validated contact manifold.
    """
    if record.get('source_kind') != 'signed_surface_reference':
        raise ValueError('Intersection-only/ambiguous witnesses cannot become contact records')
    if record.get('normal_source') != 'outward_rigid_face_reference':
        raise ValueError('Explicit unambiguous reference normal required')
    if not isinstance(record.get('id'), str) or not record['id']:
        raise ValueError('Record identity required')
    if type(record.get('step')) is not int or record['step'] != context['step'] or record['step'] < 0:
        raise ValueError('Same-step contact required')
    if type(context['dt_s']) not in (float, int) or not math.isfinite(context['dt_s']) or context['dt_s'] <= 0:
        raise ValueError('Finite positive interval required')
    for field in ('shape_id', 'body_id'):
        if type(record.get(field)) is not int or record[field] != context[field] or record[field] < 0:
            raise ValueError('Explicit isolated shape/body mapping required')
    size = {'particle': 1, 'edge': 2, 'face': 3}.get(record.get('feature'))
    if size is None:
        raise ValueError('Unknown contact feature')
    corners = record.get('corners')
    if not isinstance(corners, (list, tuple)) or len(corners) != 3:
        raise ValueError('Three padded soft-corner indices required')
    if any(type(i) is not int or not 0 <= i < len(context['particles_world_m']) for i in corners[:size]):
        raise ValueError('Invalid active particle index')
    if any(i != -1 for i in corners[size:]) or len(set(corners[:size])) != size:
        raise ValueError('Distinct active corners and -1 padding required')
    weights = _weights(record['barycentric'], size)
    soft = _blend([vector(context['particles_world_m'][i]) for i in corners[:size]], weights[:size])
    face_id = record.get('rigid_triangle_id')
    if type(face_id) is not int or not 0 <= face_id < len(context['rigid_triangles']):
        raise ValueError('Authored rigid facet identity required')
    triangle = context['rigid_triangles'][face_id]
    if len(triangle) != 3 or len(set(triangle)) != 3 or any(type(i) is not int or not 0 <= i < len(context['rigid_vertices_shape_m']) for i in triangle):
        raise ValueError('Invalid rigid facet registry')
    vertices = [vector(context['rigid_vertices_shape_m'][i]) for i in triangle]
    rigid_shape = _blend(vertices, _weights(record['rigid_barycentric'], 3))
    rigid_body = _transform(rigid_shape, context['shape_to_body'])
    stored = vector(record['rigid_surface_body_m'])
    for a, b in zip(stored, rigid_body):
        _close(a, b, 'Raw rigid surface point/body frame')
    rigid_world = _transform(rigid_body, context['body_to_world'])
    a, b, c = [_transform(_transform(p, context['shape_to_body']), context['body_to_world']) for p in vertices]
    outward = cross(tuple(y-x for x, y in zip(a, b)), tuple(y-x for x, y in zip(a, c)))
    length = math.hypot(*outward)
    if length <= 0:
        raise ValueError('Degenerate rigid facet')
    n = vector(record['normal_world'])
    _close(math.hypot(*n), 1., 'Normal length')
    for actual, expected in zip(n, (x/length for x in outward)):
        _close(actual, expected, 'World outward normal')
    phi = dot(n, tuple(x-y for x, y in zip(soft, rigid_world)))
    tangent = tuple(x-y-phi*normal for x, y, normal in zip(soft, rigid_world, n))
    _close(math.hypot(*tangent), 0., 'Reference face-normal surface projection')
    declared = record['projected_signed_gap_m']
    if type(declared) not in (float, int) or not math.isfinite(declared):
        raise ValueError('Finite declared projected gap required')
    _close(phi, declared, 'Projected gap')
    if len(context['particle_radius_m']) != len(context['particles_world_m']):
        raise ValueError('Complete particle-radius registry required')
    radii = [context['particle_radius_m'][i] for i in corners[:size]]
    margin = context['shape_margin_m']
    if any(type(x) not in (float, int) or not math.isfinite(x) or x < 0 for x in [*radii, margin]):
        raise ValueError('Finite nonnegative radii and shape margin required')
    radius = max(radii)
    penetration = -(phi-radius-margin)
    velocity = vector(record['rigid_surface_velocity_body_m_s'])
    return {'id': record['id'], 'step': record['step'], 'shape_id': record['shape_id'],
            'body_id': record['body_id'], 'corners': tuple(corners), 'weights': weights,
            'soft_point_world_m': soft, 'rigid_surface_body_m': rigid_body,
            'rigid_surface_world_m': rigid_world, 'normal_world': n,
            'rigid_surface_velocity_body_m_s': velocity,
            'projected_signed_gap_m': phi, 'maximum_particle_radius_m': radius,
            'shape_margin_m': margin, 'reference_penetration_m': penetration,
            'reference_force_law_active': penetration > 0,
            'normal_and_penetration_physically_validated': False,
            'solver_launch_enabled': False}


def review_batch(records, context, *, global_capacity, body_capacity, observed_dynamic_adjacency):
    """Reject invalid/saturated streams, merge exact equivalent events only.

    Nearby points or different soft supports are retained: no spatial clustering
    or force-manifold reduction is defined. Kinematic observation uses the full
    global stream because the solver's dynamic-body adjacency omits that body.
    """
    for value in (global_capacity, body_capacity):
        if type(value) is not int or value <= 0:
            raise ValueError('Positive finite capacity required')
    if len(records) >= global_capacity:
        raise ValueError('Raw stream saturated; reduction must not hide overflow')
    motion = context['body_motion_type']
    if motion not in ('dynamic', 'kinematic', 'static'):
        raise ValueError('Explicit motion type required')
    inverse_mass = context['body_inv_mass_effective']
    if type(inverse_mass) not in (int, float) or not math.isfinite(inverse_mass) or inverse_mass < 0:
        raise ValueError('Actual finite effective inverse mass required')
    if motion != 'dynamic' and inverse_mass != 0:
        raise ValueError('Isolated prescribed/static body must have zero effective inverse mass')
    expected = list(range(len(records))) if inverse_mass > 0 else []
    if (not isinstance(observed_dynamic_adjacency, list) or
            any(type(i) is not int for i in observed_dynamic_adjacency) or
            sorted(observed_dynamic_adjacency) != expected):
        raise ValueError('Solver dynamic-body adjacency differs from expected source behavior')
    if len(expected) >= body_capacity:
        raise ValueError('Dynamic-body adjacency saturated')
    reviewed = [review_record(record, context) for record in records]
    if len({row['id'] for row in reviewed}) != len(reviewed):
        raise ValueError('Duplicate record identity')
    kept = []; key_to_index = {}; reductions = []
    for row in reviewed:
        support = tuple(sorted((i, w) for i, w in zip(row['corners'], row['weights']) if i >= 0 and w != 0))
        key = (row['step'], row['shape_id'], row['body_id'], support,
               row['rigid_surface_body_m'], row['rigid_surface_velocity_body_m_s'], row['normal_world'],
               row['maximum_particle_radius_m'], row['shape_margin_m'])
        if key in key_to_index:
            reductions.append({'record': row['id'], 'same_as': kept[key_to_index[key]]['id']})
        else:
            key_to_index[key] = len(kept); kept.append(row)
    return {'raw_count': len(records), 'unique_reference_count': len(kept), 'records': kept,
            'exact_duplicate_events': reductions, 'observed_dynamic_adjacency': observed_dynamic_adjacency,
            'full_stream_observer_indices': list(range(len(records))),
            'kinematic_reactions_require_full_stream': motion == 'kinematic',
            'nearby_contact_reduction_defined': False, 'solver_launch_enabled': False,
            'native_contact_validated': False, 'physical_force_validated': False}
