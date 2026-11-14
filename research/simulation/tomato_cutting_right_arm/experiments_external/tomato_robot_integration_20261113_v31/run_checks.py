from pathlib import Path
import subprocess,json,time,os
W=Path(__file__).resolve().parent;python='/home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python';env=dict(os.environ,OPENBLAS_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');results=[]
for mode,name in [('contact','contact02'),('cut','cut01')]:
 out=W/'runs'/name
 if out.exists():raise FileExistsError(out)
 print('START',mode,flush=True);start=time.monotonic()
 with (W/(name+'.log')).open('w') as f:
  proc=subprocess.run([python,'-u',str(W/'robot_worker.py'),'--headless','--mode',mode,'--output',str(out)],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
 result=json.loads((out/'integration_result.json').read_text()) if (out/'integration_result.json').exists() else {'pass':False}
 record=dict(mode=mode,returncode=proc.returncode,wall_s=time.monotonic()-start,result=result);results.append(record);(W/'reports/native_checks_progress.json').write_text(json.dumps(results,indent=2));print(json.dumps(record),flush=True)
 if proc.returncode!=0 or not result['pass']:break
