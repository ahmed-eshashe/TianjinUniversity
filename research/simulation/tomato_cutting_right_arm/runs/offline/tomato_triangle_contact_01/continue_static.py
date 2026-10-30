"""A bounded static optimization, never a committed mechanical trajectory."""
import os,subprocess,json,sys,hashlib
from pathlib import Path
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');F=R/'runs/offline/tomato_triangle_contact_01'
depth=float(sys.argv[1]);name=sys.argv[2];guess=Path(sys.argv[3]);start=int(sys.argv[4]) if len(sys.argv)>4 else 0
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'};records=[];last=None
for i in range(start,start+12):
    out=F/name/f'{i:02d}';out.parent.mkdir(exist_ok=True)
    cmd=[str(R/'.venv-native/bin/python'),'rl/offline_tomato_triangle_contact.py','--depth-mm',str(depth),'--guess',str(guess),'--output',str(out)]
    result=subprocess.run(cmd,cwd=R,env=env,capture_output=True,text=True,timeout=60)
    (out.parent/f'{i:02d}.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        records.append({'chunk':i,'returncode':result.returncode,'passed':False});break
    if (out/'summary.json').exists():
        s=json.loads((out/'summary.json').read_text());records.append({'chunk':i,'passed':s['passed'],'flags':s['flags'],'runtime_s':s['runtime_s'],'peak_rss_bytes':s['peak_rss_bytes']})
        if s['passed']:last=str(out.relative_to(R))
        break
    s=json.loads((out/'candidate.json').read_text());assert s['optimization_only'] and not s['passed']
    guess=out/'guess.npy';assert hashlib.sha256(guess.read_bytes()).hexdigest()==s['guess_sha256']
    records.append({'chunk':i,'optimization_only':True,'runtime_s':s['runtime_s'],'peak_rss_bytes':s['peak_rss_bytes']})
    print(records[-1],flush=True)
report={'depth_mm':depth,'accepted':last,'records':records,'optimization_guesses_only':True,'full_cut':False}
(F/(name+'_status.json')).write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
