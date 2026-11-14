"""Single empty-scene Isaac startup check; no robot, cutting, or training."""
import argparse
import json
from pathlib import Path
import signal
import traceback


def write(root, name, data):
    temporary = root / (name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(root / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    app = sim = None
    passed = False
    stopped = False

    def stop(signum, frame):
        nonlocal stopped
        stopped = True
        raise InterruptedError('Supervisor or user requested shutdown')

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        write(args.output, 'worker_status.json', {'stage': 'importing', 'resumable': False})
        from isaaclab.app import AppLauncher
        launcher = AppLauncher(headless=True, device='cpu', visualizer=['none'])
        app = launcher.app
        write(args.output, 'worker_status.json', {'stage': 'app_started', 'resumable': False})
        from isaaclab.sim import SimulationCfg, SimulationContext
        from isaaclab_physx.physics import PhysxCfg
        sim = SimulationContext(SimulationCfg(
            device='cpu', dt=1/240, physics=PhysxCfg(), use_fabric=False,
            use_newton_actuators=False, log_dir=str(args.output)))
        sim.reset()
        if (args.output / 'stop.request').exists():
            raise InterruptedError('Stop requested before physics step')
        sim.step(render=False)
        write(args.output, 'worker_status.json', {
            'stage': 'one_empty_scene_step_completed', 'steps': 1, 'dt_s': 1/240,
            'physics_manager': sim.physics_manager.__module__, 'resumable': False})
        passed = True
    except BaseException:
        write(args.output, 'worker_failure.json', {'traceback': traceback.format_exc()})
        traceback.print_exc()
    finally:
        try:
            if sim is not None:
                sim.stop()
                SimulationContext.clear_instance()
            if app is not None:
                app.close()
        except BaseException:
            passed = False
            write(args.output, 'close_failure.json', {'traceback': traceback.format_exc()})
        write(args.output, 'worker_result.json', {
            'passed': passed and not stopped, 'clean_close_completed': passed and not stopped,
            'scope': 'empty CPU PhysX scene startup and one step only',
            'checkpoint_resumable': False, 'robot_validated': False,
            'cutting_validated': False, 'training': False})
    return 0 if passed and not stopped else 1


if __name__ == '__main__':
    raise SystemExit(main())
