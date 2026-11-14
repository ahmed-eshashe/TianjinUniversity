"""One stationary Newton blade/coupon step; separate from the PhysX robot."""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import time
import traceback

from tomato_isaac_startup_worker import write

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stationary-sdf', action='store_true')
    parser.add_argument('--sdf-resolution', type=int, choices=(128, 256, 512), default=128)
    args = parser.parse_args()
    output = args.output
    count = 12 if args.stationary_sdf else 1
    def interrupt(signum, frame):
        raise InterruptedError('Diagnostic interrupted')
    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)
    try:
        from tomato_native_worker import validate_inputs
        config = json.loads(CONFIG.read_text())
        inputs = validate_inputs(ROOT, config)
        write(output, 'validated_inputs.json', {
            'historical_config_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
            'historical_config_execution_enabled': False,
            'scope': 'New separate guarded stationary diagnostic; historical worker remains disabled',
            'source_sha256': config['source_sha256'], 'blade': config['blade'],
            'trajectory': config['trajectory'], 'observer_helper_sha256': config['observer_helper_sha256']})
        write(output, 'worker_status.json', {'stage': 'native_imports'})
        import warp as wp
        wp.init()
        wp.set_device('cuda:0')
        from tomato_coupon_runtime_builder import build_runtime_candidate
        from tomato_soft_contact_observer import make_native_observer
        from tomato_coupon_segment import SegmentJournal, run_native_segment
        started = time.monotonic()
        write(output, 'worker_status.json', {'stage': 'building_model_and_sdf'})
        bundle = build_runtime_candidate(inputs['blade'], native_execution_authorized=True,
                                         sdf_resolution=args.sdf_resolution)
        if str(bundle['model'].device) != 'cuda:0':
            raise ValueError('Texture-SDF diagnostic requires the reviewed CUDA device')
        build_s = time.monotonic()-started
        write(output, 'model_built.json', {
            'device': str(bundle['model'].device), 'build_wall_s': build_s,
            'sdf_resolution': args.sdf_resolution, 'sdf_cooking_padding_m': 0.05,
            'blade_vertices': len(inputs['blade']['vertices']),
            'blade_triangles': len(inputs['blade']['triangles']),
            'particle_count': bundle['model'].particle_count, 'body_count': bundle['model'].body_count,
            'sdf_accuracy_validated': False, 'tomato_equivalence': False})
        observer = make_native_observer(expected_helper_sha256=config['observer_helper_sha256'],
                                        native_execution_authorized=True)
        if (output/'stop.request').exists():
            raise InterruptedError('Stop requested before mechanical step')
        initial = bundle['state0'].particle_q.numpy().copy()
        source_pins = dict(config['source_sha256'])
        for name in ('tomato_coupon_initial_worker.py', 'tomato_coupon_runtime_builder.py',
                     'tomato_isaac_startup_guard.py', 'tomato_isaac_startup_worker.py', 'tomato_sdf_native_probe.py'):
            source_pins['rl/'+name] = hashlib.sha256((ROOT/'rl'/name).read_bytes()).hexdigest()
        single = dict(config, max_steps=count, run_id=output.name, episode_id='stationary_initial_state',
                      source_sha256=source_pins)
        journal = SegmentJournal(output/'journal', run_id=single['run_id'], episode_id=single['episode_id'],
                                 source_sha256=source_pins)
        write(output, 'worker_status.json', {'stage': 'stationary_step_and_observer_compilation'})
        result = run_native_segment(bundle, inputs['trajectory'], single, journal, observer,
                                    native_execution_authorized=True)
        import numpy as np
        final = bundle['state0'].particle_q.numpy()
        if not np.isfinite(final).all():
            raise ValueError('Nonfinite native particle state')
        rows = [json.loads(p.read_text())['diagnostic'] for p in sorted((output/'journal').glob('step*.json'))]
        contacts = max(row['soft_contact_count'] for row in rows)
        if len(rows) != count or contacts != 0:
            raise ValueError('Incomplete sequence or unexpected contact in 2 mm-clear initial state')
        if not np.array_equal(initial, final):
            raise ValueError('Unexpected particle drift in stationary zero-gravity no-contact control')
        sdf_done = False
        if args.stationary_sdf:
            write(output, 'worker_status.json', {'stage': 'native_sdf_distance_and_normal_queries'})
            from tomato_sdf_native_probe import measure_native_sdf
            measurements = measure_native_sdf(bundle, inputs['blade'])
            measurements['sdf_resolution'] = args.sdf_resolution
            measurements['sdf_cooking_padding_m'] = 0.05
            write(output, 'sdf_measurements.json', measurements)
            sdf_done = True
        wp.synchronize()
        write(output, 'worker_status.json', {'stage': 'stationary_initial_step_completed'})
        write(output, 'worker_result.json', {
            'diagnostic_passed': True, 'shutdown_requested': True,
            'committed_steps': result['committed_steps'], 'dt_s': single['dt_s'],
            'simulated_time_s': count*single['dt_s'], 'soft_contact_count': contacts,
            'sdf_queries_completed': sdf_done,
            'sdf_resolution': args.sdf_resolution,
            'max_particle_displacement_m': float(np.linalg.norm(final-initial, axis=1).max()),
            'scope': 'Isolated Newton CUDA nonfracturing coupon, real blade, initial no-contact state only',
            'native_contact_accuracy_validated': False, 'force_accuracy_validated': False,
            'checkpoint_resumable': False, 'cutting_validated': False, 'robot_validated': False,
            'training': False})
        return 0
    except BaseException:
        write(output, 'worker_failure.json', {'traceback': traceback.format_exc()})
        write(output, 'worker_result.json', {'diagnostic_passed': False, 'shutdown_requested': True,
                                           'checkpoint_resumable': False, 'training': False})
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
