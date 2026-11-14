"""Native finite-feature distance/crossing diagnostic; zero mechanics calls."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback

from tomato_isaac_startup_worker import write
from tomato_triangle_distance import sub
from tomato_wrench_contract import cross, dot

ROOT = Path(__file__).resolve().parents[1]
PREP = ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z'


def fixtures(blade):
    from tomato_blade_challenge_fixture import build_fixtures, facet_mesh_distance
    from tomato_sdf_native_probe import signed_reference
    from tomato_facet_distance import triangle_triangle
    historical = json.loads((PREP/'real_blade_facet_challenges_2017.json').read_text())
    cases = []
    for c in historical['cases']:
        cases.append({'id': 'historical:'+c['id'], 'facet': c['soft_diagnostic_facet_m'],
                      'target': 'blade', 'expected_crossing': c['id'] == 'edge_through_authored_blade_face'})
    # Both endpoints span the complete blade thickness, unlike the historical
    # 0.1 mm fixture whose unsigned vertex clearances do not establish outside.
    wide = build_fixtures(blade, probe_halfspan_m=.01)
    for c in wide['cases']:
        cases.append({'id': 'wide:'+c['id'], 'facet': c['soft_diagnostic_facet_m'],
                      'target': 'blade', 'expected_crossing': c['id'] == 'edge_through_authored_blade_face'})
    vertices, faces = blade['vertices'], blade['triangles']
    center = [(a+b)/2 for a, b in zip(vertices[0], vertices[1])]
    edge = sub(vertices[1], vertices[0]); length = math.hypot(*edge); direction = [v/length for v in edge]
    tangent = cross(direction, [1., 0., 0.]); size = math.hypot(*tangent); tangent = [v/size for v in tangent]
    bitangent = cross(direction, tangent)
    # Disclosed large geometry-only probe: all three vertices must lie outside
    # the entire blade, while its interior intersects the chosen blade edge.
    radius = .4
    facet = [[center[k]+radius*(math.cos(a)*tangent[k]+math.sin(a)*bitangent[k]) for k in range(3)]
             for a in (0., 2*math.pi/3, 4*math.pi/3)]
    cases.append({'id': 'authored_blade_edge_through_soft_interior', 'facet': facet,
                  'target': 'blade', 'expected_crossing': True, 'probe_radius_m': radius})
    target = [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]]
    synthetic = [
        ('coplanar_contained', [[.1, .1, 0.], [.2, .1, 0.], [.1, .2, 0.]], True),
        ('coplanar_edge_cross', [[-.1, .3, 0.], [.8, -.1, 0.], [.8, .8, 0.]], True),
        ('coplanar_clear', [[2., 2., 0.], [3., 2., 0.], [2., 3., 0.]], False),
        ('parallel_1um_clear', [[.1, .1, 1e-6], [.2, .1, 1e-6], [.1, .2, 1e-6]], False),
        ('vertex_touch', [[0., 0., 0.], [-1., 0., 1.], [0., -1., 1.]], True),
        ('noncoplanar_cross', [[.2, .2, -1.], [.2, .2, 1.], [.3, .3, 1.]], True),
    ]
    for name, facet, expected in synthetic:
        cases.append({'id': name, 'facet': facet, 'target': 'synthetic', 'target_facet': target,
                      'expected_crossing': expected})
    for case in cases:
        if case['target'] == 'blade':
            case['reference'] = facet_mesh_distance(case['facet'], vertices, faces)
            case['vertex_references'] = [signed_reference(p, vertices, faces) for p in case['facet']]
        else:
            case['reference'] = triangle_triangle(case['facet'], case['target_facet'])
    if not all(v['reference_signed_distance_m'] > 0 for v in cases[2]['vertex_references']):
        raise ValueError('Wide positive fixture must have every soft vertex outside the blade')
    if not all(v['reference_signed_distance_m'] > 0 for v in cases[4]['vertex_references']):
        raise ValueError('Blade-edge fixture must have every soft vertex outside the blade')
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    def interrupt(signum, frame):
        raise InterruptedError('Geometry diagnostic stopped')
    signal.signal(signal.SIGTERM, interrupt); signal.signal(signal.SIGINT, interrupt)
    try:
        from tomato_native_worker import validate_inputs
        blade = validate_inputs(ROOT, json.loads((PREP/'single_blade_disabled_worker_config_2132.json').read_text()))['blade']
        cases = fixtures(blade)
        write(output, 'fixture_registry.json', {'cases': cases, 'mechanical_steps': 0,
              'historical_fixture_sha256': hashlib.sha256((PREP/'real_blade_facet_challenges_2017.json').read_bytes()).hexdigest(),
              'blade_export_sha256': hashlib.sha256((PREP/'blade_export.json').read_bytes()).hexdigest()})
        import warp as wp
        import numpy as np
        from tomato_mesh_double_query import make_closest_function
        wp.init(); wp.set_device('cuda:0')
        closest = make_closest_function()

        @wp.func
        def segment_distance(a: wp.vec3d, b: wp.vec3d, c: wp.vec3d, d: wp.vec3d):
            zero = wp.float64(0.0); one = wp.float64(1.0)
            u = b-a; v = d-c; aa = wp.dot(u, u); cc = wp.dot(v, v)
            best = wp.float64(1.0e30)
            for j in range(2):
                p = a
                if j == 1:
                    p = b
                t = wp.clamp(wp.dot(p-c, v)/cc, zero, one)
                best = wp.min(best, wp.length(p-(c+t*v)))
                q = c
                if j == 1:
                    q = d
                s = wp.clamp(wp.dot(q-a, u)/aa, zero, one)
                best = wp.min(best, wp.length((a+s*u)-q))
            normal = wp.cross(u, v); det = wp.dot(normal, normal)
            if det > zero:
                w = a-c; bb = wp.dot(u, v); dd = wp.dot(u, w); ee = wp.dot(v, w)
                s = (bb*ee-cc*dd)/det; t = (aa*ee-bb*dd)/det
                if s >= zero and s <= one and t >= zero and t <= one:
                    best = wp.min(best, wp.length((a+s*u)-(c+t*v)))
            return best

        @wp.func
        def segment_face(a: wp.vec3d, b: wp.vec3d, p: wp.vec3d, q: wp.vec3d, r: wp.vec3d):
            zero = wp.float64(0.0); one = wp.float64(1.0)
            best = wp.min(wp.length(a-closest(p, q, r, a)), wp.length(b-closest(p, q, r, b)))
            best = wp.min(best, segment_distance(a, b, p, q))
            best = wp.min(best, segment_distance(a, b, q, r))
            best = wp.min(best, segment_distance(a, b, r, p))
            # Moller-Trumbore segment intersection; the Python oracle uses
            # plane crossing followed by projected barycentric classification.
            direction = b-a; e1 = q-p; e2 = r-p; h = wp.cross(direction, e2); det = wp.dot(e1, h)
            if det != zero:
                inv = one/det; delta = a-p; u = inv*wp.dot(delta, h)
                z = wp.cross(delta, e1); v = inv*wp.dot(direction, z); t = inv*wp.dot(e2, z)
                if u >= zero and v >= zero and u+v <= one and t >= zero and t <= one:
                    best = zero
            return best

        @wp.kernel(enable_backward=False)
        def facet_pairs(first: wp.array(dtype=wp.vec3d), second: wp.array(dtype=wp.vec3d),
                        result: wp.array(dtype=wp.float64)):
            i = wp.tid(); a = first[3*i]; b = first[3*i+1]; c = first[3*i+2]
            p = second[3*i]; q = second[3*i+1]; r = second[3*i+2]
            best = segment_face(a, b, p, q, r)
            best = wp.min(best, segment_face(b, c, p, q, r))
            best = wp.min(best, segment_face(c, a, p, q, r))
            best = wp.min(best, segment_face(p, q, a, b, c))
            best = wp.min(best, segment_face(q, r, a, b, c))
            result[i] = wp.min(best, segment_face(r, p, a, b, c))

        first = []; second = []; owners = []
        for i, case in enumerate(cases):
            targets = [[blade['vertices'][j] for j in t] for t in blade['triangles']] if case['target'] == 'blade' else [case['target_facet']]
            for target in targets:
                first.extend(case['facet']); second.extend(target); owners.append(i)
        a = wp.array(first, dtype=wp.vec3d); b = wp.array(second, dtype=wp.vec3d)
        distances = wp.zeros(len(owners), dtype=wp.float64)
        if (output/'stop.request').exists():
            raise InterruptedError('Stopped before geometry queries')
        wp.launch(facet_pairs, dim=len(owners), inputs=[a, b], outputs=[distances], device='cuda:0'); wp.synchronize()
        values = distances.numpy()
        if not np.isfinite(values).all() or np.any(values < 0):
            raise ValueError('Invalid finite-feature result')
        measured = []
        for i, case in enumerate(cases):
            native = min(float(v) for v, owner in zip(values, owners) if owner == i)
            # A scoped numerical comparison tolerance is disclosed separately
            # from physical contact, penetration, work or force acceptance.
            reference = case['reference']['distance_m']; tolerance = 1e-9
            agrees = abs(native-reference) <= tolerance
            classification_ok = native <= tolerance if case['expected_crossing'] else native > tolerance
            measured.append({'id': case['id'], 'native_distance_m': native, 'reference_distance_m': reference,
                             'distance_error_m': abs(native-reference), 'comparison_agrees': agrees,
                             'expected_crossing': case['expected_crossing'], 'classification_agrees': classification_ok,
                             'vertex_reference_signed_distances_m': [v['reference_signed_distance_m'] for v in case.get('vertex_references', [])]})
        passed = all(c['comparison_agrees'] and c['classification_agrees'] for c in measured)
        write(output, 'crossing_measurements.json', {
            'cases': measured, 'pair_count': len(owners), 'numerical_comparison_tolerance_m': 1e-9,
            'tolerance_scope': 'Floating-point fixture comparison only; not a physical contact threshold',
            'geometry_diagnostic_passed': passed, 'full_surface_contact_validated': False,
            'limitations': ['No exact/adaptive predicates or continuous collision detection.',
                            'No solver contact records, normals, impulses or forces were created.',
                            'Passing finite fixtures does not establish global contact completeness.']})
        write(output, 'worker_result.json', {'diagnostic_passed': passed, 'shutdown_requested': True,
              'crossing_cases_completed': len(cases), 'mechanical_steps': 0, 'training': False,
              'full_surface_contact_validated': False})
        return 0 if passed else 1
    except BaseException:
        write(output, 'worker_failure.json', {'traceback': traceback.format_exc()})
        write(output, 'worker_result.json', {'diagnostic_passed': False, 'shutdown_requested': True})
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
