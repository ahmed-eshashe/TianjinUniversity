import subprocess,os,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
jobs=[('tests_final',['runs/offline/tomato_contact_continuation_01/run_tests.py']),('continuation_surface',['rl/offline_tomato_continuation_geometry.py','--output',str(F/'continuation_surface')]),('continuation_energy180',['rl/offline_tomato_continuation_energy.py','--steps','180','--output',str(F/'continuation_energy180.json')]),('continuation_energy360',['rl/offline_tomato_continuation_energy.py','--steps','360','--output',str(F/'continuation_energy360.json')])]
for depth,old in [(5.25,'probe5p25_finish'),(5.5,'static5.5_01'),(5.75,'resumed_static5.75_00')]:
 name=f'final_static{depth:g}'
 jobs.append((name,['rl/offline_tomato_contact_continuation.py','--depth-mm',str(depth),'--guess',str(F/old/'positions.npy'),'--newton-steps','4','--output',str(F/name)]))
 jobs.append((name+'_audit',['rl/audit_tomato_triangle_contact.py','--checkpoint',str(F/name),'--output',str(F/(name+'_audit.json'))]))
records=[];start=time.monotonic()
for name,args in jobs:
 result=subprocess.run([str(R/'.venv-native/bin/python'),*args],cwd=R,env=ENV,capture_output=True,text=True,timeout=60)
 (F/(name+'.log')).write_text(result.stdout+result.stderr);rec={'job':name,'returncode':result.returncode};records.append(rec);print(rec,flush=True)
 (F/'verification_status.json').write_text(json.dumps({'records':records,'runtime_s':time.monotonic()-start},indent=2)+'\n')
 if result.returncode:break
