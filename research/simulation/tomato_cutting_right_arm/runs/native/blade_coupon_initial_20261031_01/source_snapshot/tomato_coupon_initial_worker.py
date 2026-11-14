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
    output = parser.parse_args().output
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
        wp.set_device('cpu')
        from tomato_native_coupon import build_native_candidate
        from tomato_soft_contact_observer import make_native_observer
        from tomato_coupon_segment import SegmentJournal, run_native_segment
        started = time.monotonic()
        write(output, 'worker_status.json', {'stage': 'building_model_and_sdf'})
        bundle = build_native_candidate(inputs['blade'], native_execution_authorized=True)
        if str(bundle['model'].device) != 'cpu':
            raise ValueError('This initial diagnostic requires the CPU device')
        build_s = time.monotonic()-started
        write(output, 'model_built.json', {
            'device': str(bundle['model'].device), 'build_wall_s': build_s,
            'blade_vertices': len(inputs['blade']['vertices']),
            'blade_triangles': len(inputs['blade']['triangles']),
            'particle_count': bundle['model'].particle_count, 'body_count': bundle['model'].body_count,
            'sdf_accuracy_validated': False, 'tomato_equivalence': False})
        observer = make_native_observer(expected_helper_sha256=config['observer_helper_sha256'],
                                        native_execution_authorized=True)
        if (output/'stop.request').exists():
            raise InterruptedError('Stop requested before mechanical step')
        initial = bundle['state0'].particle_q.numpy().copy()
        single = dict(config, max_steps=1, run_id=output.name, episode_id='stationary_initial_state')
        journal = SegmentJournal(output/'journal', run_id=single['run_id'], episode_id=single['episode_id'],
                                 source_sha256=config['source_sha256'])
        write(output, 'worker_status.json', {'stage': 'stationary_step_and_observer_compilation'})
        result = run_native_segment(bundle, inputs['trajectory'], single, journal, observer,
                                    native_execution_authorized=True)
        import numpy as np
        final = bundle['state0'].particle_q.numpy()
        if not np.isfinite(final).all():
            raise ValueError('Nonfinite native particle state')
        record = json.loads((output/'journal/step000000.json').read_text())['diagnostic']
        contacts = record['soft_contact_count']
        if contacts != 0:
            raise ValueError('Unexpected contact in prescribed 2 mm-clear initial state')
        wp.synchronize()
        write(output, 'worker_status.json', {'stage': 'stationary_initial_step_completed'})
        write(output, 'worker_result.json', {
            'diagnostic_passed': True, 'shutdown_requested': True,
            'committed_steps': result['committed_steps'], 'dt_s': single['dt_s'],
            'simulated_time_s': single['dt_s'], 'soft_contact_count': contacts,
            'max_particle_displacement_m': float(np.linalg.norm(final-initial, axis=1).max()),
            'scope': 'Isolated Newton CPU nonfracturing coupon, real blade, initial no-contact state only',
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
