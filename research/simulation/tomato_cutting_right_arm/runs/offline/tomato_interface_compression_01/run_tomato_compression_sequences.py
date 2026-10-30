import json,os,subprocess,sys,time
from pathlib import Path
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');folder=root/'runs/offline/tomato_interface_compression_01'
sequences={
'indent_coarse':('indentation',0,[-.05,0,.025,.05,.025,0,-.05]),
'indent_fine':('indentation',0,[-.05,-.025,0,.0125,.025,.0375,.05,.0375,.025,.0125,0,-.025,-.05]),
'reclose_broken':('reclosure',1,[-.1,-.075,-.05,-.025,0,.025,.05,.025,0,-.025,-.05,-.075,-.1]),
'reclose_broken_fine':('reclosure',1,[round(-.1+.0125*i,6) for i in range(13)]+[round(.05-.0125*i,6) for i in range(1,13)]),
'reclose_intact':('reclosure',0,[0,.025,.05,.025,0]),
'reclose_partial':('reclosure',.5,[0,.025,.05,.025,0])}
(folder/'manifest.json').write_text(json.dumps(sequences,indent=2)+'\n')
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
python=str(root/'.venv-native/bin/python')
for name,(case,damage,drives) in sequences.items():
 previous=None
 for i,drive in enumerate(drives):
  out=folder/name/f'{i:02}';out.parent.mkdir(exist_ok=True)
  command=[python,'rl/offline_tomato_coupled.py','--case',case,'--damage',str(damage),'--drive-mm',str(drive),'--output',str(out)]
  if previous:command+=['--previous',str(previous)]
  result=subprocess.run(command,cwd=root,env=env,text=True,capture_output=True,timeout=60)
  (out.parent/f'{i:02}.log').write_text(result.stdout+result.stderr)
  if result.returncode:print(name,i,'FAILED',result.returncode,result.stdout,result.stderr,flush=True);sys.exit(1)
  summary=json.loads((out/'summary.json').read_text())
  print(name,i,drive,summary['passed'],summary['flags'],round(summary['runtime_s'],2),flush=True)
  if not summary['passed']:sys.exit(1)
  previous=out
for mode in ['opening','shear_y','shear_y_negative','shear_z','shear_z_negative']:
 command=[python,'rl/offline_tomato_interface_energy.py','--mode',mode,'--output',str(folder/f'energy_{mode}.json')]
 result=subprocess.run(command,cwd=root,env=env,text=True,capture_output=True,timeout=60)
 (folder/f'energy_{mode}.log').write_text(result.stdout+result.stderr)
 print(mode,result.returncode,result.stdout,result.stderr,flush=True)
 if result.returncode:sys.exit(1)
for script in ['audit_tomato_coupled.py','audit_tomato_coupled_stability.py']:
 result=subprocess.run([python,'rl/'+script,'--run-directory',str(folder)],cwd=root,env=env,text=True,capture_output=True,timeout=60)
 (folder/(script+'.log')).write_text(result.stdout+result.stderr)
 print(script,result.returncode,result.stderr,flush=True)
 if result.returncode:sys.exit(1)
print('COMPLETE',flush=True)
