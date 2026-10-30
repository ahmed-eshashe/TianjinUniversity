"""Bounded post-soak test: request checkpoint stop, then resume for 15 seconds."""
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads(path.read_text())


def main():
    soak=ROOT/'runs/rl/phase2/camera_soak_30min_01'
    assert load(soak/'result.json')['passed'] and load(soak/'memory_report.json')['reason']=='normal exit', 'Complete the guarded soak first'
    stopped=ROOT/'runs/rl/phase2/checkpoint_stop_probe'
    command=[sys.executable,str(ROOT/'rl/guard_benchmark.py'),'--output',str(stopped),'--seconds','60','--max-updates','1','--camera','--resume',str(soak/'checkpoint.pt')]
    with (ROOT/'docs/rl/checkpoint_stop_probe.log').open('w') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
        deadline=time.monotonic()+120
        while process.poll() is None and not (stopped/'status.json').exists() and time.monotonic()<deadline:time.sleep(1)
        if process.poll() is not None:raise RuntimeError('Stop probe exited before checkpoint request; inspect its log')
        (stopped/'checkpoint_and_stop.request').write_text('Intentional graceful-stop test, not actual memory pressure.\n')
        try:code=process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            # Guard owns the child's process group; SIGINT asks it to terminate safely.
            import signal
            process.send_signal(signal.SIGINT);process.wait(timeout=15);raise
    result=load(stopped/'result.json')
    checks={'stop_returned_incomplete':code!=0,'stop_was_recorded':result['stopped_for_reserve'],
            'checkpoint_saved':(stopped/'checkpoint.pt').exists(),'no_crash':load(stopped/'memory_report.json')['child_exit_code']==0}
    assert all(checks.values()),checks
    resumed=ROOT/'runs/rl/phase2/after_stop_resume_probe'
    command=[sys.executable,str(ROOT/'rl/guard_benchmark.py'),'--output',str(resumed),'--seconds','15','--max-updates','1','--camera','--resume',str(stopped/'checkpoint.pt')]
    with (ROOT/'docs/rl/after_stop_resume_probe.log').open('w') as log:
        completed=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT,timeout=150)
    result2=load(resumed/'result.json')
    checks.update(resume_passed=completed.returncode==0 and result2['passed'],
                  rng_restored=result2['resume_checks']['rng_restored'],
                  learner_continued=result2['total_learner_updates']>result['total_learner_updates'])
    report={'passed':all(checks.values()),'checks':checks,'stop_probe':str(stopped.relative_to(ROOT)),
            'resume_probe':str(resumed.relative_to(ROOT)),'scope':'Injected checkpoint request with ample memory, followed by 15-second resume; no memory exhaustion or grasp training'}
    (ROOT/'docs/rl/graceful_resume_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
    assert report['passed']


if __name__=='__main__':main()
