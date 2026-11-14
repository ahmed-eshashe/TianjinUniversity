from pathlib import Path
import subprocess,json,time,os,datetime,hashlib,traceback
W=Path(__file__).resolve().parent;V=W.parent/'disect_fracture_20261109_v23';R=W.parents[1];O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');L=W.parent/'disect_numerics_20261108_v05/run.sh'
def atomic(path,data):
 t=path.with_suffix('.tmp');t.write_text(json.dumps(data,indent=2));t.replace(path)
def phase(name,reason,live=None):
 atomic(W/'execution_status.json',dict(phase=name,reason=reason,pid=os.getpid(),updated=datetime.datetime.now(datetime.timezone.utc).isoformat(),section4_complete=False))
 d=json.loads((O/'disect-execution-checklist.json').read_text());d['current_work'].update(eyebrow='Section 4 · Gate B',title=name.replace('_',' '),description=reason,href='disect-section4-current.txt');d['live']=None;d['updated']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
 if live:
  label,folder,stem,end=live
  for k in ['progress','result']:
   p=O/f'section4-current-{k}.json'
   if p.is_symlink():p.unlink()
   elif p.exists():raise RuntimeError('Refusing to replace non-symlink status evidence')
   p.symlink_to(folder/f'{stem}_{k}.json')
  d['live']=dict(label=label,progress='section4-current-progress.json',result='section4-current-result.json',duration_s=end,kind='contact')
 atomic(O/'disect-execution-checklist.json',d)
def run(script,log,args=[]):
 with (W/log).open('w') as f:result=subprocess.run(['bash',str(L),str(W/script),*args],stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError(f'{script} exited {result.returncode}; see {log}')
try:
 while not (V/'shallow_result.json').exists():time.sleep(3)
 old=json.loads((V/'shallow_result.json').read_text());pid=json.loads((V/'shallow_status.json').read_text())['pid']
 while Path(f'/proc/{pid}').exists():time.sleep(1)
 if not old['physical_run_completed']:raise RuntimeError('Original attempt failed a physical/solver gate; review before correction')
 if old['nonzero_damage']:raise RuntimeError('Original attempt has actual damage; review/refine it before adopting another trajectory')
 if not json.loads((V/'gate_a_result.json').read_text())['passed']:raise RuntimeError('Gate A is not passed')
 phase('corrected_checkpoint_restart_control','The original attempt completed safely but did not fracture or unload. Approved edge alignment and two-stage horizontal retreat prepared; validating restart before a bounded corrected window.')
 run('restart_controls.py','restart_controls.log')
 if not json.loads((W/'restart_controls_result.json').read_text())['passed']:raise RuntimeError('Dynamic restart control failed')
 source={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in [V,W] for p in folder.glob('*.py')};source['correction_plan.json']=hashlib.sha256((W/'correction_plan.json').read_bytes()).hexdigest();atomic(W/'run_source_manifest.json',source)
 phase('corrected_loading_window_running','First 0.020s window of the corrected 1.060s trajectory. Actual edge alignment, unchanged fracture law and stops; 0.826us step, independent refinement still required.',('Corrected shallow loading',W,'coarse0001',.02))
 run('corrected_shallow.py','coarse0001.log',['--until','.02','--name','coarse0001'])
 result=json.loads((W/'coarse0001_result.json').read_text())
 if not result['completed_window']:raise RuntimeError('Corrected window did not complete admissibly: '+result['stop'])
 phase('corrected_window_complete_pending_review','First corrected loading window finished. Review physics and measured throughput before continuing the frozen trajectory. This is not a shallow-cut or separation pass.')
except Exception as e:
 phase('stopped_at_gate',str(e));(W/'execution_exception.txt').write_text(traceback.format_exc());raise
