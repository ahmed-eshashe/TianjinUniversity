import subprocess,os,json
from pathlib import Path
r=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');f=r/'runs/offline/tomato_triangle_contact_01'
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
jobs=[('surface_final',['rl/offline_tomato_triangle_geometry.py','--output',str(f/'surface_final')]),('audit5_final',['rl/audit_tomato_triangle_contact.py','--checkpoint',str(f/'validated5'),'--output',str(f/'audit5_final.json')]),('energy180_final',['rl/offline_tomato_triangle_energy.py','--steps','180','--output',str(f/'energy180_final.json')]),('energy360_final',['rl/offline_tomato_triangle_energy.py','--steps','360','--output',str(f/'energy360_final.json')])]
status=[]
for name,args in jobs:
 result=subprocess.run([str(r/'.venv-native/bin/python'),*args],cwd=r,env=env,capture_output=True,text=True,timeout=60)
 (f/(name+'.log')).write_text(result.stdout+result.stderr);status.append({'job':name,'returncode':result.returncode});print(status[-1],flush=True)
 if result.returncode:break
(f/'verification_jobs.json').write_text(json.dumps(status,indent=2)+'\n')
