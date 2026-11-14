"""Guarded authored-mesh point queries only; no solver, SDF or physics steps."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import signal
import time
import traceback

from tomato_isaac_startup_worker import write
from tomato_sdf_native_probe import make_queries

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json'
BASELINE = ROOT/'runs/native/blade_target512_20261031_01/sdf_measurements.json'


def reference_registry(rows):
    return [{k: v for k, v in q.items() if not k.startswith('native_') and
             k not in ('signed_distance_error_m', 'sign_agrees', 'normal_angle_error_deg')} for q in rows]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--centered', action='store_true')
    parser.add_argument('--double', action='store_true')
    args = parser.parse_args()
    output = args.output
    def interrupt(signum, frame):
        raise InterruptedError('Diagnostic stopped')
    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)
    try:
        from tomato_native_worker import validate_inputs
        config = json.loads(CONFIG.read_text())
        blade = validate_inputs(ROOT, config)['blade']
        queries = make_queries(blade, targeted=True)
        baseline = json.loads(BASELINE.read_text())
        registry = reference_registry(queries)
        if len(queries) != 562 or registry != reference_registry(baseline['queries']):
            raise ValueError('Exact historical 562-point reference registry required')
        points_all = blade['vertices']+[q['point_m'] for q in queries]
        extent = [max(p[i] for p in points_all)-min(p[i] for p in points_all) for i in range(3)]
        radius = 2*math.hypot(*extent)
        if not math.isfinite(radius) or radius <= 0:
            raise ValueError('Finite full-domain query radius required')
        write(output, 'input_manifest.json', {
            'blade': config['blade'], 'historical_source_sha256': config['source_sha256'],
            'baseline_path': str(BASELINE), 'baseline_sha256': hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
            'reference_registry_sha256': hashlib.sha256(json.dumps(registry, sort_keys=True).encode()).hexdigest(),
            'query_radius_m': radius, 'parity_ray_samples': 1, 'mechanical_steps': 0})
        write(output, 'worker_status.json', {'stage': 'building_direct_mesh'})
        import warp as wp
        import numpy as np
        wp.init()
        wp.set_device('cuda:0')
        shift = [(max(p[i] for p in blade['vertices'])+min(p[i] for p in blade['vertices']))/2
                 for i in range(3)] if args.centered else [0., 0., 0.]
        vertex_values = [[p[i]-shift[i] for i in range(3)] for p in blade['vertices']]
        query_values = [[q['point_m'][i]-shift[i] for i in range(3)] for q in queries]
        write(output, 'coordinate_frame.json', {
            'common_translation_subtracted_m': shift, 'centered_before_float32_conversion': args.centered,
            'geometry_transform': 'identical translation of mesh and queries; no physical shape change'})

        @wp.kernel(enable_backward=False)
        def query_mesh(mesh_id: wp.uint64, points: wp.array(dtype=wp.vec3), max_dist: float,
                       distances: wp.array(dtype=float), normals: wp.array(dtype=wp.vec3),
                       found: wp.array(dtype=int), face_ids: wp.array(dtype=int)):
            i = wp.tid()
            result = wp.mesh_query_point_sign_parity(mesh_id, points[i], max_dist)
            found[i] = int(result.result)
            face_ids[i] = result.face
            if result.result:
                closest = wp.mesh_eval_position(mesh_id, result.face, result.u, result.v)
                delta = points[i]-closest
                distance = wp.length(delta)
                distances[i] = result.sign*distance
                if distance > 0.0:
                    normals[i] = result.sign*delta/distance

        started = time.monotonic()
        vertices = wp.array(vertex_values, dtype=wp.vec3, device='cuda:0')
        indices = wp.array([i for face in blade['triangles'] for i in face], dtype=int, device='cuda:0')
        mesh = wp.Mesh(points=vertices, indices=indices)
        points = wp.array(query_values, dtype=wp.vec3, device='cuda:0')
        distances = wp.zeros(len(queries), dtype=float, device='cuda:0')
        normals = wp.zeros(len(queries), dtype=wp.vec3, device='cuda:0')
        found = wp.zeros(len(queries), dtype=int, device='cuda:0')
        faces = wp.zeros(len(queries), dtype=int, device='cuda:0')
        if (output/'stop.request').exists():
            raise InterruptedError('Stopped before queries')
        write(output, 'worker_status.json', {'stage': 'direct_mesh_queries'})
        wp.launch(query_mesh, dim=len(queries), inputs=[mesh.id, points, radius],
                  outputs=[distances, normals, found, faces], device='cuda:0')
        wp.synchronize()
        cold_s = time.monotonic()-started
        # A second identical query batch separates warm dispatch from first compilation.
        started = time.monotonic()
        wp.launch(query_mesh, dim=len(queries), inputs=[mesh.id, points, radius],
                  outputs=[distances, normals, found, faces], device='cuda:0')
        wp.synchronize()
        warm_s = time.monotonic()-started
        d, n, ok, f = distances.numpy(), normals.numpy(), found.numpy(), faces.numpy()
        if not np.all(ok == 1) or not np.isfinite(d).all() or not np.isfinite(n).all():
            raise ValueError('Missing direct mesh query or nonfinite output')
        float32_distances = d.copy()
        double_durations = None
        if args.double:
            if args.centered:
                raise ValueError('Double diagnostic uses original authored coordinates')
            write(output, 'worker_status.json', {'stage': 'all_facet_float64_queries'})
            from tomato_mesh_double_query import query_all_facets
            unsigned, closest, f, double_durations = query_all_facets(
                blade['vertices'], blade['triangles'], [q['point_m'] for q in queries])
            signs = np.where(np.signbit(d), -1., 1.)
            d = signs*unsigned
            delta = np.asarray([q['point_m'] for q in queries], dtype=np.float64)-closest
            n = np.divide(signs[:, None]*delta, unsigned[:, None], out=np.zeros_like(delta),
                          where=unsigned[:, None] > 0)
        rows = []
        for q, value, normal, face in zip(queries, d, n, f):
            row = dict(q, native_distance_m=float(value), native_normal=normal.tolist(),
                       native_nearest_triangle=int(face))
            if args.double:
                row['native_original_float32_distance_m'] = float(float32_distances[len(rows)])
            if q['kind'] == 'signed_offset':
                row['signed_distance_error_m'] = abs(float(value)-q['reference_signed_distance_m'])
                row['sign_agrees'] = (float(value)<0) == (q['reference_signed_distance_m']<0)
                norm = float(np.linalg.norm(normal))
                if norm == 0:
                    raise ValueError('Missing off-surface direct-query normal')
                cosine = float(np.dot(normal/norm, q['reference_normal']))
                row['normal_angle_error_deg'] = math.degrees(math.acos(max(-1., min(1., cosine))))
            rows.append(row)
        surface = [q for q in rows if q['kind'] != 'signed_offset']
        offset = [q for q in rows if q['kind'] == 'signed_offset']
        thin = [q for q in offset if q.get('family') == 'thin_feature']
        result = {'query_count': len(rows), 'query_batches': 2, 'missing_queries': 0,
                  'centered_coordinates': args.centered,
                  'double_precision_all_facets': args.double,
                  'distance_arithmetic': 'float64 all 144 triangles' if args.double else 'installed float32 mesh query',
                  'sign_source': 'installed float32-mesh one-ray parity (unchanged)',
                  'double_query_wall_s_cold_warm': double_durations,
                  'coordinate_shift_m': shift,
                  'max_surface_error_m': max(abs(q['native_distance_m']) for q in surface),
                  'max_signed_distance_error_m': max(q['signed_distance_error_m'] for q in offset),
                  'sign_mismatches': sum(not q['sign_agrees'] for q in offset),
                  'thin_sign_mismatches': sum(not q['sign_agrees'] for q in thin),
                  'max_normal_angle_error_deg': max(q['normal_angle_error_deg'] for q in offset),
                  'max_thin_normal_angle_error_deg': max(q['normal_angle_error_deg'] for q in thin),
                  'cold_build_compile_query_wall_s': cold_s, 'warm_562_query_wall_s': warm_s,
                  'accuracy_thresholds_selected': False, 'point_query_accuracy_qualified': False,
                  'full_surface_contact_validated': False,
                  'limitations': ['Point queries do not establish edge/face contact completeness.',
                                 'Surface-point normals are not compared because sharp edges and zero distance are ambiguous.',
                                 'Mesh float32 rounding and parity/nearest-triangle robustness remain scoped to these samples.'],
                  'queries': rows}
        write(output, 'direct_mesh_measurements.json', result)
        write(output, 'worker_result.json', {
            'diagnostic_passed': True, 'shutdown_requested': True, 'direct_queries_completed': 562,
            'centered_coordinates': args.centered,
            'double_precision_all_facets': args.double,
            'mechanical_steps': 0, 'training': False, 'cutting_validated': False,
            'full_surface_contact_validated': False})
        return 0
    except BaseException:
        write(output, 'worker_failure.json', {'traceback': traceback.format_exc()})
        write(output, 'worker_result.json', {'diagnostic_passed': False, 'shutdown_requested': True})
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
