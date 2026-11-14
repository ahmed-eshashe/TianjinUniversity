"""Collision-generated analytic fixture records; no solver or force evaluation."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback

from tomato_isaac_startup_worker import write
from tomato_owned_contact_capture import capture_owned_prefix
from tomato_contact_snapshot import collect_snapshot_contacts
from tomato_wrench_contract import dot

ROOT = Path(__file__).resolve().parents[1]
HALF = (.01, .01, .002)
COORDINATE_CHECK_M = 1e-7  # Analytic float32 fixture only, not a physical contact tolerance.


def box_reference(point, half=HALF):
    """Independent Euclidean distance and outward normal candidates for a box."""
    q = [abs(p)-h for p, h in zip(point, half)]
    outside = [max(x, 0.) for x in q]; length = math.hypot(*outside)
    distance = length+min(max(q), 0.)
    if length > 0:
        normals = [[(1 if p >= 0 else -1)*v/length for p, v in zip(point, outside)]]
    else:
        nearest = max(q); normals = []
        for axis in range(3):
            if abs(q[axis]-nearest) <= COORDINATE_CHECK_M:
                normal = [0., 0., 0.]; normal[axis] = 1. if point[axis] >= 0 else -1.; normals.append(normal)
    return distance, normals


def fixture_cases():
    return [
        {'id': 'particle_inside', 'kind': 'particle', 'points': [[0., 0., .001]], 'positive': True},
        {'id': 'particle_clear', 'kind': 'particle', 'points': [[0., 0., .003]], 'positive': False},
        {'id': 'edge_inside_vertices_outside', 'kind': 'edge', 'points': [[-.03, 0., .001], [.03, 0., .001]], 'positive': True},
        {'id': 'face_inside_vertices_outside', 'kind': 'face',
         'points': [[-.04, -.02, .001], [.04, -.02, .001], [0., .04, .001]], 'positive': True},
        {'id': 'face_clear', 'kind': 'face',
         'points': [[-.04, -.02, .003], [.04, -.02, .003], [0., .04, .003]], 'positive': False},
        {'id': 'transformed_face_inside', 'kind': 'face',
         'points': [[-.04, -.02, .001], [.04, -.02, .001], [0., .04, .001]], 'positive': True, 'transformed': True},
    ]


def build_case(case, *, for_solver=False):
    import warp as wp
    import newton
    transformed = case.get('transformed', False)
    rotation = ((0., 0., 1.), (1., 0., 0.), (0., 1., 0.)) if transformed else ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
    translation = (.1, -.2, .3) if transformed else (0., 0., 0.)
    shape_offset = (.004, .005, .006) if transformed else (0., 0., 0.)
    quaternion = (.5, .5, .5, .5) if transformed else (0., 0., 0., 1.)
    builder = newton.ModelBuilder(gravity=(0., 0., 0.))
    for p in case['points']:
        body_point = [a+b for a, b in zip(p, shape_offset)]
        world = [dot(row, body_point)+t for row, t in zip(rotation, translation)]
        builder.add_particle(wp.vec3(*world), wp.vec3(0.), .001, radius=0.)
    if case['kind'] == 'edge': builder.add_edge(-1, -1, 0, 1, rest=0., edge_ke=0., edge_kd=0.)
    if case['kind'] == 'face': builder.add_triangle(0, 1, 2, tri_ke=0., tri_ka=0., tri_kd=0.)
    body = builder.add_body(xform=wp.transform(wp.vec3(*translation), wp.quat(*quaternion)),
                            is_kinematic=True, label='analytic_diagnostic_box')
    shape = builder.add_shape_box(body, hx=HALF[0], hy=HALF[1], hz=HALF[2],
              xform=wp.transform(wp.vec3(*shape_offset), wp.quat_identity()),
              cfg=newton.ModelBuilder.ShapeConfig(density=0., mu=0., margin=0., gap=0.))
    if for_solver:
        builder.color()
    model = builder.finalize(device='cuda:0'); state = model.state()
    pipeline = newton.CollisionPipeline(model, broad_phase='nxn', soft_contact_gap=0.,
                 soft_contact_max=32, rigid_contact_max=8, enable_rigid_soft_full_surface_contact=True)
    contacts = pipeline.contacts()
    return model, state, pipeline, contacts, body, shape, rotation, translation


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    def stop(signum, frame): raise InterruptedError('Analytic contact diagnostic stopped')
    signal.signal(signal.SIGINT, stop); signal.signal(signal.SIGTERM, stop)
    try:
        import warp as wp
        import newton
        wp.init(); wp.set_device('cuda:0')
        source_files = ['tomato_analytic_contact_worker.py', 'tomato_owned_contact_capture.py',
                        'tomato_contact_snapshot.py', 'tomato_isaac_startup_guard.py']
        pins = {'rl/'+name: hashlib.sha256((ROOT/'rl'/name).read_bytes()).hexdigest() for name in source_files}
        results = []
        for case in fixture_cases():
            if (output/'stop.request').exists(): raise InterruptedError('Stop requested between fixtures')
            write(output, 'worker_status.json', {'stage': 'analytic_collision_generation', 'case': case['id']})
            model, state, pipeline, contacts, body, shape, rotation, translation = build_case(case)
            before_particles = state.particle_q.numpy().tolist(); before_body = state.body_q.numpy().tolist()
            pipeline.collide(state, contacts); wp.synchronize()
            if state.particle_q.numpy().tolist() != before_particles or state.body_q.numpy().tolist() != before_body:
                raise ValueError('Collision-only query unexpectedly changed positions')
            identity = {'run_id': output.name, 'episode_id': case['id'], 'step': 0,
                        'start_s': 0., 'dt_s': 1/1200, 'source_sha256': pins}
            context = {'step': 0, 'dt_s': 1/1200, 'body_id': body, 'shape_id': shape,
                       'body_to_world': {'rotation': rotation, 'translation_m': translation}}
            generation = int(contacts.contact_generation.numpy()[0])
            envelope, captured_context = capture_owned_prefix(contacts, state.particle_q, model.shape_body, state.body_q,
                identity, context, expected_generation=generation, native_capture_authorized=True,
                capture_origin='owned_analytic_collision_diagnostic')
            observed = collect_snapshot_contacts(envelope, identity, captured_context, target_body=body, collector_capacity=32)
            actual_rotation = captured_context['body_to_world']['rotation']; actual_translation = captured_context['body_to_world']['translation_m']
            actual_shape_offset = model.shape_transform.numpy()[shape][:3].tolist()
            actual_half = model.shape_scale.numpy()[shape].tolist()
            def local(point):
                delta = [p-t for p, t in zip(point, actual_translation)]
                return [sum(actual_rotation[j][i]*delta[j] for j in range(3))-actual_shape_offset[i] for i in range(3)]
            rows = []
            for row in observed['target_records']:
                soft = local(row['soft_point_world_m']); rigid = local(row['raw_rigid_surface_world_m'])
                phi, possible_normals = box_reference(soft, actual_half)
                surface_error = abs(box_reference(rigid, actual_half)[0])
                gap_error = abs(phi-row['projected_gap_from_rounded_snapshot_m'])
                world_candidates = [[dot(axis, n) for axis in actual_rotation] for n in possible_normals]
                normal_error = min(math.hypot(*(a-b for a, b in zip(row['normal_world'], n))) for n in world_candidates)
                corners = row['corners']; kind = 'particle' if corners[1:] == [-1, -1] else 'edge' if corners[2] == -1 else 'face'
                if (surface_error > COORDINATE_CHECK_M or gap_error > COORDINATE_CHECK_M or normal_error > 1e-6 or
                    abs(row['barycentric_sum_error']) > 1e-6 or abs(row['normal_length_error']) > 1e-6 or kind != case['kind'] or phi >= 0):
                    raise ValueError('Analytic contact reference mismatch for '+case['id'])
                rows.append(dict(row, feature=kind, reference_signed_distance_m=phi,
                                raw_surface_error_m=surface_error, projected_gap_error_m=gap_error,
                                outward_normal_vector_error=normal_error))
            if len(rows) != (1 if case['positive'] else 0):
                raise ValueError('Expected analytic feature/clear contact count mismatch: '+case['id'])
            vertex_phi = [box_reference(p)[0] for p in case['points']]
            if 'vertices_outside' in case['id'] and not all(p > 0 for p in vertex_phi):
                raise ValueError('Full-feature fixture vertices must be outside')
            write(output, case['id']+'_capture.json', envelope)
            results.append({'id': case['id'], 'expected_kind': case['kind'], 'contact_count': len(rows),
                            'vertex_reference_signed_distances_m': vertex_phi, 'records': rows,
                            'particle_and_body_positions_unchanged': True})
        write(output, 'analytic_contact_measurements.json', {'cases': results,
            'coordinate_comparison_m': COORDINATE_CHECK_M, 'normal_and_weight_comparison': 1e-6,
            'comparison_scope': 'Numerical checks for this float32 analytic fixture only; no physical contact tolerance.',
            'collision_queries': len(results), 'mechanical_steps': 0, 'force_evaluations': 0,
            'real_blade_contact_validated': False, 'full_surface_contact_globally_validated': False})
        write(output, 'worker_result.json', {'diagnostic_passed': True, 'shutdown_requested': True,
            'analytic_collision_cases_completed': len(results), 'mechanical_steps': 0, 'force_evaluations': 0,
            'training': False, 'real_blade_contact_validated': False})
        return 0
    except BaseException:
        write(output, 'worker_failure.json', {'traceback': traceback.format_exc()})
        write(output, 'worker_result.json', {'diagnostic_passed': False, 'shutdown_requested': True})
        traceback.print_exc(); return 1


if __name__ == '__main__': raise SystemExit(main())
