"""Fixed Isaac startup worker with real resource monitoring and owned-group cleanup."""
import argparse
from contextlib import ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time

from tomato_preupgrade_guard import startup_decision, runtime_decision, stop_group, group_members

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / '.venv-native/bin/python'
WORKER = ROOT / 'rl/tomato_isaac_startup_worker.py'


def hardware_sample():
    available = next(int(line.split()[1]) * 1024 for line in
                     Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    raw = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
        text=True, timeout=1)
    rows = raw.strip().splitlines()
    if len(rows) != 1:
        raise ValueError('This check requires exactly one GPU')
    used, total = [int(value.strip()) * 1024**2 for value in rows[0].split(',')]
    if not 0 <= used <= total:
        raise ValueError('Invalid GPU reading')
    return available, total - used


def supervise(output, *, monitor=hardware_sample, wall_s=60, _fixture_command=None):
    """Only CLI route is the fixed startup worker; fixture injection is for stdlib tests."""
    if not 0 < wall_s <= 60:
        raise ValueError('Worker budget must be at most 60 seconds')
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    process = None
    reason = 'exception'
    errors = 0
    warning = False
    samples = []
    started = None
    returncode = None
    remaining = []
    timer = None
    timed_out = threading.Event()
    command = _fixture_command or [str(PYTHON), str(WORKER), '--output', str(output)]

    def interrupt(signum, frame):
        raise InterruptedError('Shutdown signal ' + str(signum))

    previous = {}
    with ExitStack() as stack:
        for name in ('offline_overnight.lock', 'right_arm_control.lock'):
            lock = stack.enter_context((ROOT / 'logs' / name).open('a'))
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            ram, vram = monitor()
            if not startup_decision(ram, vram):
                reason = 'startup_refused'
            else:
                for sig in (signal.SIGINT, signal.SIGTERM):
                    previous[sig] = signal.signal(sig, interrupt)
                env = os.environ.copy()
                env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUNBUFFERED='1')
                manifest = {
                    'command': command, 'worker_wall_budget_s': wall_s,
                    'cleanup_grace_s': 2, 'startup_available_ram_bytes': ram,
                    'startup_free_vram_bytes': vram,
                    'authorization': 'User approved launch protection and one bounded startup check, 2026-10-31',
                    'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in (Path(__file__), WORKER, ROOT/'rl/tomato_preupgrade_guard.py', ROOT/'rl/guard_benchmark.py')},
                    'training': False, 'checkpoint_resumable': False}
                (output/'launch_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
                log = stack.enter_context((output/'simulation.log').open('w'))
                stream = stack.enter_context((output/'resources.jsonl').open('w', buffering=1))
                started = time.monotonic()
                process = subprocess.Popen(command, cwd=ROOT, env=env, start_new_session=True,
                                           stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
                def expire():
                    timed_out.set()
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                timer = threading.Timer(max(0, started+wall_s-time.monotonic()), expire)
                timer.daemon = True
                timer.start()
                (output/'owned_pid.json').write_text(json.dumps({'pid': process.pid}))
                deadline = started + wall_s
                warning_deadline = deadline
                while True:
                    now = time.monotonic()
                    if now >= min(deadline, warning_deadline):
                        reason = 'warning_shutdown_timeout' if warning else 'wall_timeout'
                        break
                    if process.poll() is not None:
                        reason = 'memory_warning_stop' if warning else 'exited'
                        break
                    try:
                        ram, vram = monitor()
                        action = runtime_decision(ram, vram)
                        errors = 0
                        sample = {'wall_s': time.monotonic()-started, 'available_ram_bytes': ram,
                                  'free_vram_bytes': vram, 'action': action}
                        samples.append(sample)
                        stream.write(json.dumps(sample)+'\n')
                    except InterruptedError:
                        raise
                    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, StopIteration) as exc:
                        errors += 1
                        action = 'stop' if errors >= 3 else 'continue'
                        stream.write(json.dumps({'monitor_error': type(exc).__name__, 'consecutive_errors': errors})+'\n')
                    if action == 'stop':
                        reason = 'monitor_errors' if errors >= 3 else 'hard_memory_stop'
                        break
                    if action == 'checkpoint_and_stop' and not warning:
                        warning = True
                        warning_deadline = min(deadline, time.monotonic()+2)
                        (output/'stop.request').write_text('Startup has no resumable state; close and restart fresh.\n')
                        os.killpg(process.pid, signal.SIGTERM)
                    time.sleep(min(.2, max(0, deadline-time.monotonic())))
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, StopIteration, InterruptedError):
            reason = 'interrupted' if process else 'startup_unreadable'
        finally:
            if process is not None:
                stop_group(process, grace_s=2)
                if timer is not None:
                    timer.cancel()
                    timer.join()
                if timed_out.is_set():
                    reason = 'wall_timeout'
                returncode = process.returncode
                remaining = [pid for pid, state in group_members(process.pid) if state != 'Z']
            for sig, handler in previous.items():
                signal.signal(sig, handler)
            try:
                worker = json.loads((output/'worker_result.json').read_text())
            except (OSError, ValueError):
                worker = {}
            result = {'passed': reason == 'exited' and returncode == 0 and
                      worker.get('startup_step_passed') is True and worker.get('shutdown_requested') is True and
                      worker.get('steps') == 1 and not remaining,
                      'reason': reason, 'launched': process is not None, 'child_exit_code': returncode,
                      'elapsed_wall_s': time.monotonic()-started if started else 0,
                      'remaining_live_group_members': remaining, 'warning_requested': warning,
                      'samples': len(samples), 'monitor_errors': errors,
                      'min_available_ram_bytes': min((s['available_ram_bytes'] for s in samples), default=None),
                      'min_free_vram_bytes': min((s['free_vram_bytes'] for s in samples), default=None),
                      'scope': 'Isaac startup only; no robot/cutting/training validation', 'worker': worker}
            (output/'supervisor_result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = supervise(args.output)
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
