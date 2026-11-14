from pathlib import Path
import subprocess,sys,json,time
W=Path(__file__).resolve().parents[1];started=time.perf_counter()
for name in ['half_probe','half_dt','half_event','restart','heldout','heldout_half_action']:
    print('RUN',name,flush=True)
    with (W/'runs'/(name+'.log')).open('w') as log:
        r=subprocess.run([sys.executable,str(W/'tests/run_case.py'),name],stdout=log,stderr=subprocess.STDOUT,timeout=600)
    if r.returncode:print('STOP case failed',name,flush=True);sys.exit(r.returncode)
    if name!='heldout':
        with (W/'runs'/('compare_'+name+'.log')).open('w') as log:
            r=subprocess.run([sys.executable,str(W/'tests/compare.py'),name],stdout=log,stderr=subprocess.STDOUT,timeout=120)
        p=json.loads((W/('comparison_'+name+'.json')).read_text());print('COMPARISON',name,p['status'],p['results'],flush=True)
        if r.returncode:print('STOP refinement failed',name,flush=True);sys.exit(r.returncode)
    else:print('COMPLETE heldout pilot',flush=True)
print('BOUNDED CAMPAIGN COMPLETE',time.perf_counter()-started,flush=True)
