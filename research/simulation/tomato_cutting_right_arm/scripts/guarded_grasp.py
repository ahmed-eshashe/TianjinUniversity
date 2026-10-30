"""Single-instance launch with a host-memory watchdog and recorded peak RSS."""
import fcntl,json,os,signal,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lock=(root/'logs/right_arm_control.lock').open('w')
try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError: sys.exit('Right-arm controller is already running.')
def available():
    return int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))
if available()<5_000_000: sys.exit('Close the full scene or other large apps first: less than 5 GB RAM available.')
report_path=root/'logs/kitchen_grasp_report.json'
report_path.unlink(missing_ok=True)
p=subprocess.Popen(['/home/omen/miniconda3/envs/isaaclab_6/bin/python',str(root/'scripts/kitchen_grasp.py'),*sys.argv[1:]],start_new_session=True)
peak=0; lowest=available(); reason='normal exit'
try:
    while p.poll() is None:
        mem=available(); lowest=min(lowest,mem)
        try:
            rss=int(next(l.split()[1] for l in Path(f'/proc/{p.pid}/status').read_text().splitlines() if l.startswith('VmRSS:')))
            peak=max(peak,rss)
        except (FileNotFoundError,StopIteration): pass
        if mem<2_000_000:
            reason='Stopped: less than 2 GB available RAM'
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)
            break
        time.sleep(0.5)
except KeyboardInterrupt:
    reason='User interrupted'
    os.killpg(p.pid,signal.SIGTERM)
finally:
    p.wait()
    report={'exit_code':p.returncode,'reason':reason,'peak_rss_gb':peak/1e6,'lowest_available_ram_gb':lowest/1e6}
    (root/'logs/kitchen_grasp_memory_report.json').write_text(json.dumps(report,indent=2))
    print('MEMORY_REPORT',json.dumps(report),flush=True)
validated=report_path.exists() and json.loads(report_path.read_text()).get('passed',False)
status_path=root/'logs/kitchen_grasp_status.json'
validated=validated and status_path.exists() and json.loads(status_path.read_text()).get('state')!='failed'
sys.exit(0 if p.returncode==0 and validated else 1)
