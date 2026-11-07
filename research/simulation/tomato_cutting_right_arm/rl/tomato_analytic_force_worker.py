"""Stationary analytic force/Hessian and reconstructed-reaction diagnostic."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback

from tomato_analytic_contact_worker import fixture_cases, build_case, box_reference
from tomato_contact_snapshot import collect_snapshot_contacts
from tomato_owned_contact_capture import capture_owned_prefix
from tomato_isaac_startup_worker import write
from tomato_wrench_contract import cross, dot
from tomato_contact_precision_audit import separated_reference_checks

ROOT = Path(__file__).resolve().parents[1]


def stationary_reference(penetration_m, normal, stiffness_n_m, surface_world_m, com_world_m):
    if stiffness_n_m < 0 or not math.isfinite(stiffness_n_m):
        raise ValueError('Finite nonnegative stiffness required')
    magnitude = max(0., penetration_m)*stiffness_n_m
    force = [magnitude*x for x in normal]
    reaction = [-v for v in force]
    moment = cross([p-c for p, c in zip(surface_world_m, com_world_m)], reaction)
    hessian = [[stiffness_n_m*a*b if penetration_m > 0 else 0. for b in normal] for a in normal]
    return force, reaction, list(moment), hessian


def evaluate_native(model, state, contacts, solver):
    import warp as wp
    from newton._src.solvers.vbd.rigid_vbd_kernels import init_body_particle_contacts, _eval_soft_ef_contact
    count = int(contacts.soft_contact_count.numpy()[0])
    if not 0 < count < contacts.soft_contact_max:
        raise ValueError('Nonempty unsaturated contact stream required')
    ke = wp.zeros(count, dtype=float); kd = wp.zeros(count, dtype=float)
    mu = wp.zeros(count, dtype=float); material_ke = wp.zeros(count, dtype=float)
    wp.launch(init_body_particle_contacts, dim=count,
              inputs=[contacts.soft_contact_count, contacts.soft_contact_shape,
                      model.soft_contact_ke, model.soft_contact_kd, model.soft_contact_mu,
                      model.shape_material_ke, model.shape_material_kd, model.shape_material_mu,
                      solver.rigid_contact_k_start_value], outputs=[ke, kd, mu, material_ke], device=model.device)
    previous_particle = wp.clone(state.particle_q); previous_body = wp.clone(state.body_q)

    @wp.kernel(enable_backward=False)
    def evaluate(pos: wp.array[wp.vec3], previous_pos: wp.array[wp.vec3], radius: wp.array[float],
                 body_q: wp.array[wp.transform], body_prev: wp.array[wp.transform],
                 body_qd: wp.array[wp.spatial_vector], body_com: wp.array[wp.vec3],
                 shape_body: wp.array[int], corners: wp.array[wp.vec3i], bary: wp.array[wp.vec3],
                 shapes: wp.array[int], points: wp.array[wp.vec3], velocities: wp.array[wp.vec3],
                 normals: wp.array[wp.vec3], margins: wp.array[float], k: wp.array[float],
                 damping: wp.array[float], friction: wp.array[float], eps: float, dt: float,
                 force: wp.array[wp.vec3], hessian: wp.array[wp.mat33], rigid_point: wp.array[wp.vec3],
                 body_wrench: wp.array[wp.spatial_vector]):
        i = wp.tid()
        f, h, point = _eval_soft_ef_contact(i, corners[i], bary[i], pos, previous_pos, radius,
            k[i], damping[i], friction[i], eps, shape_body, body_q, body_prev, body_qd, body_com,
            shapes, points, velocities, normals, margins, dt)
        body = shape_body[shapes[i]]
        com = wp.transform_point(body_q[body], body_com[body])
        reaction = -f
        force[i] = f; hessian[i] = h; rigid_point[i] = point
        body_wrench[i] = wp.spatial_vector(reaction, wp.cross(point-com, reaction))

    force = wp.zeros(count, dtype=wp.vec3); hessian = wp.zeros(count, dtype=wp.mat33)
    point = wp.zeros(count, dtype=wp.vec3); wrench = wp.zeros(count, dtype=wp.spatial_vector)
    wp.launch(evaluate, dim=count, inputs=[state.particle_q, previous_particle, model.particle_radius,
        state.body_q, previous_body, state.body_qd, model.body_com, model.shape_body,
        contacts.soft_contact_indices, contacts.soft_contact_barycentric, contacts.soft_contact_shape,
        contacts.soft_contact_body_pos, contacts.soft_contact_body_vel, contacts.soft_contact_normal,
        model.shape_margin, ke, kd, mu, solver.friction_epsilon, 1/1200],
        outputs=[force, hessian, point, wrench], device=model.device)
    wp.synchronize()
    return {'ke': ke.numpy().tolist(), 'kd': kd.numpy().tolist(), 'mu': mu.numpy().tolist(),
            'material_ke': material_ke.numpy().tolist(), 'force': force.numpy().tolist(),
            'hessian': hessian.numpy().tolist(), 'rigid_point': point.numpy().tolist(), 'wrench': wrench.numpy().tolist()}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    def stop(signum, frame): raise InterruptedError('Force diagnostic stopped')
    signal.signal(signal.SIGINT, stop); signal.signal(signal.SIGTERM, stop)
    try:
        import warp as wp
        import newton.solvers
        wp.init(); wp.set_device('cuda:0')
        pins = {'rl/'+name: hashlib.sha256((ROOT/'rl'/name).read_bytes()).hexdigest() for name in
                ['tomato_analytic_force_worker.py', 'tomato_analytic_contact_worker.py', 'tomato_owned_contact_capture.py',
                 'tomato_contact_snapshot.py', 'tomato_isaac_startup_guard.py', 'tomato_contact_precision_audit.py']}
        results = []; evaluations = 0
        for case in fixture_cases():
            if (output/'stop.request').exists(): raise InterruptedError('Stopped between force fixtures')
            write(output, 'worker_status.json', {'stage': 'stationary_analytic_force', 'case': case['id']})
            model, state, pipeline, contacts, body, shape, rotation, translation = build_case(case, for_solver=True)
            solver = newton.solvers.SolverVBD(model, iterations=5, rigid_compliant_alm=True,
                                             integrate_with_external_rigid_solver=False)
            before = {'particles': state.particle_q.numpy().tolist(), 'body': state.body_q.numpy().tolist()}
            pipeline.collide(state, contacts); wp.synchronize()
            identity = dict(run_id=output.name, episode_id=case['id'], step=0, start_s=0., dt_s=1/1200, source_sha256=pins)
            context = dict(step=0, dt_s=1/1200, body_id=body, shape_id=shape,
                           body_to_world={'rotation': rotation, 'translation_m': translation})
            snapshot, captured_context = capture_owned_prefix(contacts, state.particle_q, model.shape_body, state.body_q,
                identity, context, expected_generation=int(contacts.contact_generation.numpy()[0]),
                native_capture_authorized=True, capture_origin='owned_analytic_collision_diagnostic')
            observed = collect_snapshot_contacts(snapshot, identity, captured_context, target_body=body, collector_capacity=32)
            write(output, case['id']+'_capture.json', snapshot)
            count = observed['target_count']
            if count != (1 if case['positive'] else 0): raise ValueError('Analytic contact count changed')
            parameters = {'soft_ke': float(model.soft_contact_ke), 'soft_kd': float(model.soft_contact_kd),
                'soft_mu': float(model.soft_contact_mu), 'shape_ke': float(model.shape_material_ke.numpy()[shape]),
                'shape_kd': float(model.shape_material_kd.numpy()[shape]), 'shape_mu': float(model.shape_material_mu.numpy()[shape]),
                'cold_start_k': float(solver.rigid_contact_k_start_value), 'friction_epsilon': float(solver.friction_epsilon)}
            avg_ke = .5*(parameters['soft_ke']+parameters['shape_ke'])
            expected_k = min(avg_ke, parameters['cold_start_k']) if parameters['cold_start_k'] >= 0 else avg_ke
            expected_kd = .5*(parameters['soft_kd']+parameters['shape_kd'])
            expected_mu = math.sqrt(parameters['soft_mu']*parameters['shape_mu'])
            if expected_mu != 0: raise ValueError('This stationary frictionless reference requires mixed mu=0')
            rows = []; raw = None
            if count:
                raw = evaluate_native(model, state, contacts, solver); evaluations += count
                r = captured_context['body_to_world']['rotation']; t = captured_context['body_to_world']['translation_m']
                local_com = model.body_com.numpy()[body].tolist(); com = [dot(axis, local_com)+v for axis, v in zip(r, t)]
                shape_offset = model.shape_transform.numpy()[shape][:3].tolist(); half = model.shape_scale.numpy()[shape].tolist()
                for i, row in enumerate(observed['target_records']):
                    soft = row['soft_point_world_m']; delta = [p-v for p, v in zip(soft, t)]
                    local_soft = [sum(r[j][k]*delta[j] for j in range(3))-shape_offset[k] for k in range(3)]
                    phi, normals = box_reference(local_soft, half)
                    if len(normals) != 1: raise ValueError('Force reference requires unique analytic normal')
                    world_normal = [dot(axis, normals[0]) for axis in r]
                    expected_f, expected_r, expected_m, expected_h = stationary_reference(-phi, world_normal,
                        expected_k, row['raw_rigid_surface_world_m'], com)
                    force_error = math.hypot(*(a-b for a, b in zip(raw['force'][i], expected_f)))
                    reaction_error = math.hypot(*(a-b for a, b in zip(raw['wrench'][i][:3], expected_r)))
                    moment_error = math.hypot(*(a-b for a, b in zip(raw['wrench'][i][3:], expected_m)))
                    hessian_error = max(abs(raw['hessian'][i][a][b]-expected_h[a][b]) for a in range(3) for b in range(3))
                    comparison = {
                        'parameters': parameters, 'native_arrays': raw, 'expected_force_n': expected_f,
                        'expected_moment_nm': expected_m, 'expected_hessian': expected_h,
                        'force_error_n': force_error, 'reaction_error_n': reaction_error,
                        'moment_error_nm': moment_error, 'hessian_error_n_m': hessian_error,
                        'expected_ke': expected_k, 'expected_kd': expected_kd, 'expected_mu': expected_mu,
                        'independent_penetration_m': -phi, 'record': row}
                    rigid_delta = [p-v for p, v in zip(raw['rigid_point'][i], t)]
                    local_rigid = [sum(r[j][k]*rigid_delta[j] for j in range(3))-shape_offset[k] for k in range(3)]
                    surface_error = abs(box_reference(local_rigid, half)[0])
                    normal_error = math.dist(row['normal_world'], world_normal)
                    checks = separated_reference_checks(snapshot['payload'], comparison,
                        surface_error_m=surface_error, normal_error=normal_error)
                    arithmetic_f = checks['replay']['replayed_force_n']
                    arithmetic_r = [-v for v in arithmetic_f]
                    arithmetic_m = cross([p-c for p, c in zip(raw['rigid_point'][i], com)], arithmetic_r)
                    reaction_error = math.dist(raw['wrench'][i][:3], arithmetic_r)
                    moment_error = math.dist(raw['wrench'][i][3:], arithmetic_m)
                    comparison.update(reference_version=2, separated_checks=checks,
                        arithmetic_reaction_error_n=reaction_error, arithmetic_moment_error_nm=moment_error)
                    write(output, case['id']+'_force_comparison.json', comparison)
                    if (not checks['geometry_passed'] or not checks['arithmetic_passed'] or
                        reaction_error > 1e-5 or moment_error > 1e-6 or hessian_error > 1e-4 or
                        raw['ke'][i] != expected_k or raw['kd'][i] != expected_kd or raw['mu'][i] != expected_mu):
                        raise ValueError('Analytic force/Hessian/reaction reference mismatch')
                    rows.append({'global_contact_index': row['global_index'], 'expected_force_n': expected_f,
                        'native_force_n': raw['force'][i], 'expected_body_reaction_n': expected_r,
                        'native_body_wrench_force_then_moment': raw['wrench'][i], 'expected_body_moment_nm': expected_m,
                        'force_error_n': force_error, 'reaction_error_n': reaction_error, 'moment_error_nm': moment_error,
                        'hessian_error_n_m': hessian_error, 'independent_box_penetration_m': -phi,
                        'separated_checks': checks})
            if before != {'particles': state.particle_q.numpy().tolist(), 'body': state.body_q.numpy().tolist()}:
                raise ValueError('Force diagnostic unexpectedly changed physical state')
            write(output, case['id']+'_capture.json', snapshot)
            results.append({'id': case['id'], 'contact_count': count, 'parameters': parameters,
                            'expected_mixed_ke': avg_ke, 'expected_cold_penalty_ke': expected_k,
                            'records': rows, 'native_arrays': raw, 'state_unchanged': True})
        write(output, 'analytic_force_measurements.json', {'cases': results, 'force_evaluations': evaluations,
              'mechanical_steps': 0, 'collision_queries': 6,
              'reference_version': 2,
              'comparison_scope': 'Stationary axis-box fixtures only: geometry 1e-7 m / normal 1e-6; force exact fused binary32 replay; reaction 1e-5 N, moment 1e-6 Nm, Hessian 1e-4 N/m.',
              'historical_geometry_force_gate_passed': all(row['separated_checks']['historical_geometry_force_gate_passed'] for case in results for row in case['records']),
              'reaction_is_reconstructed_not_independently_measured': True,
              'physical_two_way_coupling_validated': False, 'real_blade_force_validated': False})
        write(output, 'worker_result.json', {'diagnostic_passed': True, 'shutdown_requested': True,
              'analytic_force_cases_completed': len(results), 'mechanical_steps': 0, 'force_evaluations': evaluations,
              'reference_version': 2, 'geometry_checks_passed': True, 'arithmetic_checks_passed': True,
              'training': False, 'real_blade_force_validated': False})
        return 0
    except BaseException:
        write(output, 'worker_failure.json', {'traceback': traceback.format_exc()})
        write(output, 'worker_result.json', {'diagnostic_passed': False, 'shutdown_requested': True})
        traceback.print_exc(); return 1


if __name__ == '__main__': raise SystemExit(main())
