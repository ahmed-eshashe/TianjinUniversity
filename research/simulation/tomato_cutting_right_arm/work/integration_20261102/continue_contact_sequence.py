"""Bounded serialized qualification sequence; no cuts or training routes."""
from pathlib import Path
import json,time,subprocess,sys,hashlib,os,traceback
from tomato_isaac_startup_guard import supervise
root=Path(__file__).resolve().parents[2];work=root/'work/integration_20261102';status=work/'continuous_contact_status.json';python=root/'.venv-native/bin/python'
def note(stage,**kw):status.write_text(json.dumps(dict(stage=stage,pid=os.getpid(),pgid=os.getpgrp(),unix_s=time.time(),**kw),indent=2)+'\n');print(stage,flush=True)
def cpu(script,args,log):
 note('independent_readback',script=script,args=args)
 with (work/log).open('w')as stream:subprocess.run([str(python),str(work/script),*args],cwd=root,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=1800)
def freeze_check():
 contract=json.loads((root/'runs/offline/integration_contract_20261102_40/contract.json').read_text())
 for name,h in contract['source_sha256'].items():
  if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h:raise ValueError(('Moving contract source changed',name))
try:
 note('waiting_for_protected_preload_repeat')
 parent=root/'runs/native/mounted_target_com_r128_20261102_02';deadline=time.monotonic()+3600
 while not(parent/'supervisor_result.json').exists():
  if time.monotonic()>deadline:raise TimeoutError('Protected preload repeat did not finish within its declared wall allowance')
  time.sleep(1)
 assert json.loads((parent/'supervisor_result.json').read_text())['passed'],'Protected preload native component did not pass'
 body='runs/offline/robot_work_com_r128_20261102_02';pressure='runs/offline/mounted_com_readback_r128_20261102_02';refine='runs/offline/mounted_com_refinement_20261102_01';energy='runs/offline/preload_contact_work_r128_20261102_02'
 cpu('validate_robot_work_com_trace.py',['--run',str(parent),'--output',body],'robot_work_com_r128_02_console.txt')
 cpu('validate_mounted_target_com.py',['--run',str(parent),'--output',pressure],'mounted_com_readback_r128_02_console.txt')
 cpu('compare_mounted_com_refinement.py',['--fine-run',str(parent),'--output',refine],'mounted_com_refinement_01_console.txt')
 cpu('evaluate_preload_contact_work.py',['--run',str(parent),'--body-readback',body,'--output',energy],'preload_contact_work_r128_02_console.txt')
 assert json.loads((root/body/'measurements.json').read_text())['component_passed']
 assert json.loads((root/pressure/'measurements.json').read_text())['passed']
 assert json.loads((root/refine/'measurements.json').read_text())['refinement_passed']
 assert json.loads((root/energy/'measurements.json').read_text())['preload_fixture_work_passed']
 note('protected_preload_fixture_gates_passed',full_23B_qualified=False)
 for factor,direction in [(1,'down'),(2,'down'),(4,'down'),(4,'up')]:
  freeze_check();mode=f'moving_contact_c{factor}_{direction}';directory=root/f'runs/native/{mode}_20261102_01';note('moving_native_component',mode=mode,output=str(directory))
  result=supervise(directory,mode=mode,wall_s=3600)
  assert result['passed'],('Moving native component failed; sequence halted',mode,result.get('reason'))
  # Body/knife work is quick; retain individual force/moment failures as flags.
  cpu('validate_moving_robot_work.py',['--run',str(directory),'--output',f'runs/offline/moving_robot_work_c{factor}_{direction}_20261102_01'],f'moving_robot_work_c{factor}_{direction}_01_console.txt')
 note('moving_native_cohort_complete_pending_independent_pressure_work_and_convergence',full_23B_qualified=False,cutting_qualified=False)
except BaseException:
 note('sequence_stopped_on_failure',traceback=traceback.format_exc(),full_23B_qualified=False,cutting_qualified=False)
 raise
