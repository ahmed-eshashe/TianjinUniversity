"""Finite, gate-preserving loading campaign. Stops on any failure/cap/damage.
No cutting milestone is promoted here; withdrawal/refinement remain separate.
"""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time
W=Path(__file__).resolve().parent;R=W.parents[1];O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');runner=W.parent/'disect_numerics_20261108_v05/run.sh';python=W.parent/'solver_comparison_20261108/env311/bin/python';contract=json.loads((W/'continuation_contract.json').read_text());source=json.loads((W/'execution_contract.json').read_text())
assert json.loads((W.parent/'disect_batched_contact_20261110_v39/fresh_control_review.json').read_text())['combined_candidate_nonfracturing_component_passed']
assert json.loads((W/'paired_loaded_review.json').read_text())['passed']
for path,sha in source['sources'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
start=time.monotonic();current=.0505;resume=W/'batch00505_final.npz';assert resume.exists();windows=[];active=None

def atomic(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');os.replace(t,p)
def publish(running,note,progress=None):
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();completed=progress.get('actual_accepted_sim_s',progress.get('sim_s',current)) if progress else current
 state={'running':running,'completed_sim_s':completed,'planned_loading_end_s':.18,'updated_utc':now,'pid':os.getpid(),'child_pid':None if active is None or active.poll() is not None else active.pid,'note':note,'windows':windows,'wall_s':time.monotonic()-start,'gate_b_passed':False};atomic(W/'campaign_status.json',state)
 p=O/'disect-execution-checklist.json';d=json.loads(p.read_text());d['updated']=now;d['live']=None;d['section4_execution'].update(running=running,current_job_directory=str(W),last_accepted_time_s=completed,stop=None if running else note,latest_review=str(W/'campaign_status.json'));d['current_work'].update(eyebrow='Section 4 · progressive loading '+('running' if running else 'stopped'),title=('Batched contact validated; loading continues' if running else 'Loading campaign stopped — gate review'),description=f'Accepted {completed*1000:.3f} ms / 180 ms loading horizon. {note} No complete cutting milestone qualified; speed deferred, experimental validation pending.',href='disect-section4-current.txt');atomic(p,d)
 text=f'SECTION 4 — {"RUNNING" if running else "STOPPED"}\nAccepted {completed*1000:.6f} ms of the 180 ms loading horizon.\n{note}\nUpdated {now}\nNo Gate B/full slice qualification. All six milestones remain open.\n';(O/'disect-section4-current.txt').write_text(text);(W/'STATUS.txt').write_text(text)
try:
 while current<.18-1e-12:
  remaining=contract['max_total_wall_s']-(time.monotonic()-start)
  if remaining<1:publish(False,'Overall finite loading wall cap reached; no automatic resumption');break
  target=min(.18,round(current+.005,7));name='load'+str(round(target*1e6)).zfill(6);cap=min(contract['per_window_wall_cap_s'],remaining)
  command=['bash',str(runner),str(W/'loading.py'),'--resume',str(resume),'--until',str(target),'--name',name,'--wall-cap',str(cap),'--stop-at-damage']
  atomic(W/f'{name}_execution.json',{'command':command,'resume_sha256':hashlib.sha256(resume.read_bytes()).hexdigest(),'until_s':target,'wall_cap_s':cap,'physics_and_limits_unchanged':True,'no_auto_retry':True})
  with (W/f'{name}_launcher.log').open('w') as log:
   active=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
   while active.poll() is None:
    path=W/f'{name}_progress.json';progress=json.loads(path.read_text()) if path.exists() else None;publish(True,'Stop at first damage, physical/numerical failure or finite cap.',progress);time.sleep(10)
  rp=W/f'{name}_result.json'
  if active.returncode or not rp.exists():publish(False,f'{name}: child failure / missing result. Inspect preserved launcher log.');break
  result=json.loads(rp.read_text());current=result['duration_s'];windows.append({'name':name,'stop':result['stop'],'completed_sim_s':current,'wall_s':result['wall_s'],'damage':result['nonzero_damage'],'peak_force_N':max(row['sum_force_N'] for row in result['rows'])})
  reviewed=subprocess.run([str(python),str(W/'review_window.py'),name],stdout=(W/f'{name}_review.log').open('w'),stderr=subprocess.STDOUT)
  if reviewed.returncode:publish(False,f'{name}: evidence review failed; no continuation');break
  review=json.loads((W/f'{name}_review.json').read_text());windows[-1]['recent_next_5ms_forecast_s']=review['estimated_next_5ms_wall_s']
  if result['nonzero_damage']:publish(False,'First damage event: independent half-step and controlled withdrawal required before Gate B');break
  if result['stop'] not in ['window_completed','completed'] or not result['completed_window'] or not review['all_accepted_sample_guards_passed']:publish(False,'Stopped at '+result['stop']+'; diagnosis required before further loading');break
  resume=W/f'{name}_final.npz'
  if current>=.18-1e-12:publish(False,'Loading horizon completed without damage: saved-state diagnosis required, not a cut pass');break
except Exception as exc:
 publish(False,'Supervisor exception: '+repr(exc));raise
