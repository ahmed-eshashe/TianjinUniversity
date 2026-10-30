"""Single-instance RAM/VRAM watchdog for bounded resource benchmarks only."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PYTHON = '/home/omen/miniconda3/envs/isaaclab_6/bin/python'
HOST_START = 5_000_000 * 1024
HOST_WARNING = 3_000_000 * 1024
HOST_STOP = 2_000_000 * 1024
# Measured one-environment peak incremental use plus checkpoint reserve.
BENCHMARK_HOST_START = 10_000_000_000
GPU_START_FREE = 4 * 1024**3


def host_memory():
    fields = {x.split(':')[0]: int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemAvailable:', 'MemTotal:'))}
    return fields['MemAvailable'] * 1024


def gpu_memory():
    raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'], text=True, timeout=4).strip().splitlines()[0]
    used, total = [int(x.strip()) * 1024**2 for x in raw.split(',')]
    return used, total


def resource_action(available_ram, free_vram, monitor_errors=0):
    """Evaluate reserves without allocating memory; hard stops take priority."""
    if available_ram < HOST_STOP or free_vram < 1024**3 or monitor_errors >= 3:
        return 'stop'
    if available_ram < HOST_WARNING or free_vram < 1536 * 1024**2:
        return 'checkpoint_and_stop'
    return 'continue'


def startup_allowed(available_ram, free_vram):
    return available_ram >= max(HOST_START, BENCHMARK_HOST_START) and free_vram >= GPU_START_FREE


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--seconds', type=int, default=60)
    p.add_argument('--camera', action='store_true')
    p.add_argument('--resume', type=Path)
    p.add_argument('--max-updates', type=int, default=12)
    p.add_argument('--width', type=int, default=128)
    a = p.parse_args()
    if not 10 <= a.seconds <= 1800 or not 1 <= a.max_updates <= 24 or a.width not in [64, 96, 128]:
        p.error('Benchmark limited to 10–1800 seconds, 1–24 tiny PPO updates and 64/96/128-pixel camera')
    a.output = a.output.resolve()
    a.output.mkdir(parents=True, exist_ok=False)
    lock = (ROOT / 'logs/right_arm_control.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('Another robot controller/benchmark is running; start refused.')
    used, total = gpu_memory()
    if not startup_allowed(host_memory(), total-used):
        raise SystemExit('Start refused: this measured benchmark requires 10 GB available RAM and 4 GiB free VRAM. Close other large apps first.')
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUNBUFFERED='1')
    command = [PYTHON, str(ROOT / 'rl/benchmark.py'), '--output', str(a.output), '--seconds', str(a.seconds),
               '--max-updates', str(a.max_updates), '--width', str(a.width)]
    if a.camera:
        command.append('--camera')
    if a.resume:
        command += ['--resume', str(a.resume.resolve())]
    manifest = {'command': command, 'scope': 'Phase 2 resource benchmark only; not knife skill training',
                'guard_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'thresholds_bytes': {'host_start': BENCHMARK_HOST_START, 'original_host_start_floor': HOST_START,
                                     'host_warning': HOST_WARNING, 'host_stop': HOST_STOP,
                                     'gpu_start_free': GPU_START_FREE, 'gpu_warning_free': 1536 * 1024**2, 'gpu_stop_free': 1024**3},
                'same_lock_as_scripted_controller': True, 'configuration': vars(a).copy()}
    manifest['configuration'] = {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()}
    (a.output / 'guard_configuration.json').write_text(json.dumps(manifest, indent=2))
    log = (a.output / 'simulation.log').open('w')
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT, start_new_session=True)
    start = time.monotonic(); samples = []; reason = 'normal exit'; warning_at = None; monitor_errors = 0
    def terminate():
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        with (a.output / 'resources.jsonl').open('w', buffering=1) as stream:
            while process.poll() is None:
                available = host_memory()
                rss = 0
                try:
                    rss = int(next(x.split()[1] for x in Path(f'/proc/{process.pid}/status').read_text().splitlines() if x.startswith('VmRSS:'))) * 1024
                except (FileNotFoundError, StopIteration):
                    pass
                try:
                    used, total = gpu_memory(); monitor_errors = 0
                except (subprocess.SubprocessError, ValueError):
                    monitor_errors += 1
                sample = {'wall_s': time.monotonic() - start, 'available_ram_bytes': available,
                          'rss_bytes': rss, 'gpu_used_bytes': used, 'gpu_free_bytes': total - used}
                samples.append(sample); stream.write(json.dumps(sample) + '\n')
                action = resource_action(available, total-used, monitor_errors)
                if action == 'stop':
                    reason = 'hard memory stop' if monitor_errors < 3 else 'GPU monitoring failed'; terminate(); break
                if action == 'checkpoint_and_stop':
                    if warning_at is None:
                        warning_at = time.monotonic()
                        (a.output / 'checkpoint_and_stop.request').write_text('Memory reserve warning: checkpoint and stop safely.\n')
                    if time.monotonic() - warning_at > 12:
                        reason = 'memory warning shutdown timeout'; terminate(); break
                if time.monotonic() - start > a.seconds + 240:
                    reason = 'benchmark wall timeout'; terminate(); break
                time.sleep(1)
    except KeyboardInterrupt:
        reason = 'user interrupted'; terminate()
    finally:
        process.wait(); log.close()
        report = {'reason': reason, 'child_exit_code': process.returncode, 'warning_requested': warning_at is not None,
                  'elapsed_wall_s': time.monotonic() - start, 'samples': len(samples),
                  'peak_rss_gb': max((x['rss_bytes'] for x in samples), default=0) / 1e9,
                  'min_available_ram_gb': min((x['available_ram_bytes'] for x in samples), default=0) / 1e9,
                  'peak_gpu_used_mib': max((x['gpu_used_bytes'] for x in samples), default=0) / 1024**2,
                  'min_gpu_free_mib': min((x['gpu_free_bytes'] for x in samples), default=0) / 1024**2}
        (a.output / 'memory_report.json').write_text(json.dumps(report, indent=2))
        print(json.dumps(report), flush=True)
    result = a.output / 'result.json'
    valid = result.exists() and json.loads(result.read_text()).get('passed', False)
    return 0 if process.returncode == 0 and reason == 'normal exit' and not warning_at and valid else 1


if __name__ == '__main__':
    sys.exit(main())
