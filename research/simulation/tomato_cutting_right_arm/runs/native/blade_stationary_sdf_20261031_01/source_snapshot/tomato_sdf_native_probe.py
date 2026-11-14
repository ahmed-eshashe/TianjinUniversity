"""Native texture-SDF measurements against separate authored-mesh references."""
import math
from tomato_triangle_distance import point_mesh, sub
from tomato_wrench_contract import cross, dot
from tomato_sdf_diagnostics import surface_probes
from tomato_coupon_trajectory import audit_closed_surface


def signed_reference(point, vertices, triangles):
    """Unsigned closest facet plus independent solid-angle inside classification."""
    closest = point_mesh(point, vertices, triangles)
    distance = closest['distance_m']
    if distance <= 1e-12:
        raise ValueError('Signed reference requires an off-surface query')
    angles = []
    for face in triangles:
        a, b, c = [sub(vertices[i], point) for i in face]
        la, lb, lc = [math.hypot(*v) for v in (a, b, c)]
        numerator = dot(a, cross(b, c))
        denominator = la*lb*lc + dot(a, b)*lc + dot(b, c)*la + dot(c, a)*lb
        angles.append(2*math.atan2(numerator, denominator))
    winding = math.fsum(angles)/(4*math.pi)
    if min(abs(winding), abs(abs(winding)-1)) > 1e-6:
        raise ValueError('Ambiguous winding-number sign reference')
    sign = -1 if abs(winding) > .5 else 1
    normal = [sign*(p-q)/distance for p, q in zip(point, closest['closest_point_m'])]
    return {'reference_signed_distance_m': sign*distance, 'reference_normal': normal,
            'reference_nearest_triangle': closest['triangle_id'], 'winding_number': winding}


def make_queries(blade):
    vertices, triangles = blade['vertices'], blade['triangles']
    audit_closed_surface(vertices, triangles)
    queries = surface_probes(vertices, triangles)
    ranked = []
    for i, face in enumerate(triangles):
        a, b, c = [vertices[j] for j in face]
        n = cross(sub(b, a), sub(c, a))
        size = math.hypot(*n)
        ranked.append((size, i, [v/size for v in n],
                       [math.fsum(p[k] for p in (a, b, c))/3 for k in range(3)]))
    for _, i, normal, center in sorted(ranked, reverse=True)[:12]:
        for offset in (-.001, -.00025, .00025, .001):
            point = [p+offset*n for p, n in zip(center, normal)]
            queries.append({'id': f'face_offset:{i}:{offset}', 'kind': 'signed_offset',
                            'point_m': point, 'face_offset_m': offset,
                            **signed_reference(point, vertices, triangles)})
    return queries


def measure_native_sdf(bundle, blade):
    import warp as wp
    import numpy as np
    from newton._src.geometry.sdf_texture import TextureSDFData, texture_sample_sdf_grad

    @wp.kernel(enable_backward=False)
    def sample(table: wp.array(dtype=TextureSDFData), index: int,
               points: wp.array(dtype=wp.vec3), distances: wp.array(dtype=float),
               gradients: wp.array(dtype=wp.vec3)):
        i = wp.tid()
        d, g = texture_sample_sdf_grad(table[index], points[i])
        distances[i] = d
        gradients[i] = g

    model = bundle['model']
    if model.shape_count != 1 or not np.array_equal(model.shape_scale.numpy()[0], [1, 1, 1]):
        raise ValueError('Probe requires one unscaled authored blade shape')
    sdf_index = int(model._shape_sdf_index.numpy()[0])
    if sdf_index < 0:
        raise ValueError('Blade lacks a native texture SDF; no fallback accepted')
    queries = make_queries(blade)
    points = wp.array([q['point_m'] for q in queries], dtype=wp.vec3, device=model.device)
    distances = wp.zeros(len(queries), dtype=float, device=model.device)
    gradients = wp.zeros(len(queries), dtype=wp.vec3, device=model.device)
    wp.launch(sample, dim=len(queries), inputs=[model._texture_sdf_data, sdf_index, points],
              outputs=[distances, gradients], device=model.device)
    wp.synchronize()
    values, normals = distances.numpy(), gradients.numpy()
    if not np.isfinite(values).all() or not np.isfinite(normals).all():
        raise ValueError('Nonfinite SDF query or gradient')
    rows = []
    for query, value, gradient in zip(queries, values, normals):
        row = dict(query, native_distance_m=float(value), native_gradient=gradient.tolist(),
                   native_gradient_norm=float(np.linalg.norm(gradient)))
        if query['kind'] == 'signed_offset':
            row['signed_distance_error_m'] = abs(float(value)-query['reference_signed_distance_m'])
            row['sign_agrees'] = (float(value) < 0) == (query['reference_signed_distance_m'] < 0)
            if row['native_gradient_norm'] > 1e-12:
                cosine = float(np.dot(gradient/row['native_gradient_norm'], query['reference_normal']))
                row['normal_angle_error_deg'] = math.degrees(math.acos(max(-1., min(1., cosine))))
            else:
                row['normal_angle_error_deg'] = None
        rows.append(row)
    surface = [r for r in rows if r['kind'] != 'signed_offset']
    offset = [r for r in rows if r['kind'] == 'signed_offset']
    angles = [r['normal_angle_error_deg'] for r in offset if r['normal_angle_error_deg'] is not None]
    return {'surface_query_count': len(surface), 'signed_offset_query_count': len(offset),
            'maximum_surface_abs_distance_m': max(abs(r['native_distance_m']) for r in surface),
            'maximum_signed_distance_error_m': max(r['signed_distance_error_m'] for r in offset),
            'sign_mismatch_count': sum(not r['sign_agrees'] for r in offset),
            'undefined_gradient_count': len(offset)-len(angles),
            'maximum_normal_angle_error_deg': max(angles) if angles else None,
            'acceptance_thresholds_selected': False, 'native_sdf_accuracy_qualified': False,
            'limitations': ['Normals compared only at sampled offsets, not sharp surface edges.',
                            'Floating-point winding sign assumes the authored closed surface; self-intersections not certified.',
                            'Samples do not prove contact completeness or thin-edge preservation.'],
            'queries': rows}
