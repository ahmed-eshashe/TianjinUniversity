from pathlib import Path
import subprocess,os,json
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');folder=root/'runs/offline/tomato_unloading_01'
assert json.loads((folder/'tests.json').read_text())['passed']
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
manifest={'scope':'offline damaged wedge withdrawal and explicitly supported normal reclosure/reopening; no full cut',
 'seed':'runs/offline/tomato_blade_damage_01/insertion_refined/08','withdrawal_steps_mm':[.25,.125],
 'reclosure_drives_mm':[0,.025,.05,.025,0,-.025,-.05,-.025,0,0],
 'energy_tolerance_relative':.01,'energy_tolerance_absolute_j':1e-12,'contact_tolerance_m':1e-9,'force_residual_tolerance':1e-6,'volume_floor':.1,
 'damage_is_evolving_not_manually_frozen':True,'simulator':False,'training':False,'full_cut':False}
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for name,step in [('coarse',.25),('fine',.125)]:
 sequence=[('withdrawal',d,0) for d in [4,4]+[round(4-i*step,6) for i in range(1,round(4/step)+1)]]
 sequence += [('reclosure',0,d) for d in manifest['reclosure_drives_mm']]
 previous=None
 for i,(phase,depth,drive) in enumerate(sequence):
  out=folder/name/f'{i:02}';out.parent.mkdir(exist_ok=True)
  command=[str(root/'.venv-native/bin/python'),'rl/offline_tomato_unloading.py','--phase',phase,'--depth-mm',str(depth),'--drive-mm',str(drive),'--output',str(out)]
  if previous:command+=['--previous',str(previous)]
  result=subprocess.run(command,cwd=root,env=env,text=True,capture_output=True,timeout=60)
  (out.parent/f'{i:02}.log').write_text(result.stdout+result.stderr)
  print(name,i,result.returncode,result.stdout,result.stderr,flush=True)
  if result.returncode:raise SystemExit(1)
  summary=json.loads((out/'summary.json').read_text())
  if not summary['passed']:raise SystemExit(1)
  previous=out
print('COMPLETE',flush=True)
