"""Serial bounded optimizer probes. No chunk is a physical trajectory step."""
import os,subprocess,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
previous=F/'probe5p25_finish';records=[];start=time.monotonic()
for depth in [5.5,5.75,6.,6.25,6.5,6.75,7.,7.25,7.5,7.75,8.,8.125]:
    guess=None;accepted=None
    for chunk in range(3):
        tag=f'static{depth:g}_{chunk:02d}';out=F/tag
        args=['rl/offline_tomato_contact_continuation.py','--depth-mm',str(depth),'--previous',str(previous),'--newton-steps','10','--output',str(out)]
        if guess:args+=['--guess',str(guess)]
        try:
            result=subprocess.run([str(R/'.venv-native/bin/python'),*args],cwd=R,env=ENV,capture_output=True,text=True,timeout=60)
            (F/(tag+'.log')).write_text(result.stdout+result.stderr)
            rec={'depth_mm':depth,'chunk':chunk,'returncode':result.returncode,'output':str(out.relative_to(R))}
        except subprocess.TimeoutExpired as e:
            (F/(tag+'.log')).write_bytes((e.stdout or b'')+(e.stderr or b''));rec={'depth_mm':depth,'chunk':chunk,'parent_wall_timeout':True};records.append(rec);break
        if result.returncode:records.append(rec);break
        if (out/'summary.json').exists():
            s=json.loads((out/'summary.json').read_text());rec.update({k:s[k] for k in ['passed','flags','runtime_s','peak_rss_bytes','force_residual','minimum_stability_eigenvalue','min_J']})
            records.append(rec);print(rec,flush=True)
            if s['passed']:
                audit=F/(tag+'_audit.json')
                result=subprocess.run([str(R/'.venv-native/bin/python'),'rl/audit_tomato_triangle_contact.py','--checkpoint',str(out),'--output',str(audit)],cwd=R,env=ENV,capture_output=True,text=True,timeout=60)
                (F/(tag+'_audit.log')).write_text(result.stdout+result.stderr)
                if not result.returncode and json.loads(audit.read_text())['passed']:accepted=out
            break
        s=json.loads((out/'candidate.json').read_text());assert s['optimization_only'] and not s['passed'];guess=out/'guess.npy'
        assert hashlib.sha256(guess.read_bytes()).hexdigest()==s['guess_sha256']
        rec.update({'optimization_only':True,'runtime_s':s['runtime_s'],'peak_rss_bytes':s['peak_rss_bytes']});records.append(rec);print(rec,flush=True)
    report={'records':records,'last_accepted':str((accepted or previous).relative_to(R)),'static_only':True,'damage_evolution_enabled':False,'full_cut':False,'runtime_s':time.monotonic()-start}
    (F/'static_probe_status.json').write_text(json.dumps(report,indent=2)+'\n')
    if not accepted:break
    previous=accepted
print(report,flush=True)
