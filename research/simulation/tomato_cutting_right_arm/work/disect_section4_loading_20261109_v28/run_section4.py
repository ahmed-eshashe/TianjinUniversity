"""Bounded Gate B loading: paired saved-state continuations, one GPU at a time.
Stops at a failed gate, a verified damage event, 40 ms, or the declared deadline.
Does not launch separation, robot coupling, training or a different physical model.
"""
from pathlib import Path
import subprocess,json,os,signal,time,datetime,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1]
O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
OLD=W.parent/'disect_adaptive_contact_20261109_v27'
PLAN=json.loads((W/'execution_plan.json').read_text())
START=time.monotonic();DEADLINE=START+PLAN['supervisor_wall_cap_s']
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(path,data):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2));os.replace(tmp,path)
def publish(title,text,name=None,target=None):
 p=O/'disect-execution-checklist.json';d=json.loads(p.read_text())
 d['updated']=stamp();d['live']=None
 d['current_work']={'eyebrow':'Section 4 · Gate B loading','title':title,'description':text,'href':'disect-section4-current.txt'}
 d['section4_execution']['current_job_directory']=str(W)
 if name:
  for label,suffix in [('disect-v28-progress.json','progress'),('disect-v28-result.json','result')]:
   p0=O/label
   if p0.is_symlink():p0.unlink()
   if p0.exists():raise RuntimeError('Non-symlink status file already exists')
   p0.symlink_to(W/f'{name}_{suffix}.json')
  d['live']={'label':'Gate B '+name,'kind':'contact','duration_s':target,'progress':'disect-v28-progress.json','result':'disect-v28-result.json'}
 atomic(p,d)
 lines=[d['title'],'Updated: '+d['updated'],'',title,text,'']
 for stage in d['stages']:
  lines.append(stage['title'])
  for item in stage['items']:lines.extend([f"[{item['status']}] {item['task']}",'  '+item.get('acceptance_or_limit','')])
  lines.append('')
 (O/'disect-execution-checklist.txt').write_text('\n'.join(lines)+'\n')
 status=json.loads((W/'job_status.json').read_text())
 (O/'disect-section4-current.txt').write_text((W/'EXECUTION.txt').read_text()+'\n\nLATEST JOB STATUS\n'+json.dumps(status,indent=2)+'\n')
def run(name,checkpoint,target,refined):
 cap=min(PLAN['fine_wall_cap_s'] if refined else PLAN['coarse_wall_cap_s'],DEADLINE-time.monotonic()-90)
 if cap<=0:raise RuntimeError('Declared supervisor deadline reached; checkpoints retained')
 command=['bash',str(R/'work/disect_numerics_20261108_v05/run.sh'),str(W/'loading.py'),'--resume',str(checkpoint),'--until',str(target),'--name',name,'--wall-cap',str(cap)]
 if refined:command.append('--refined')
 atomic(W/f'{name}_execution.json',dict(command=command,started=stamp(),checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest()))
 with (W/f'{name}.log').open('w') as log:
  p=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  atomic(W/'job_status.json',dict(running=True,phase=name,target_sim_s=target,pid=p.pid,supervisor_pid=os.getpid(),updated=stamp(),gate_b_passed=False))
  publish('Section 4 loading test running',f'Continuing the verified blade path to {target*1000:g} ms, then comparing the independent half-step run. Original physical limits remain active. No qualified cut or separation yet.',name,target)
  try:code=p.wait(timeout=min(cap+600,max(1,DEADLINE-time.monotonic())))
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=30)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   raise RuntimeError(f'{name}: supervisor deadline, saved checkpoint retained')
 if code:raise RuntimeError(f'{name}: exit {code}; inspect saved log')
 result=json.loads((W/f'{name}_result.json').read_text())
 if not result['completed_window']:
  raise RuntimeError(f"{name}: {result['stop']}; last accepted time {result['duration_s']:.9g} s. No gate pass. Inspect {name}_rejected_volume_guard.json if present.")
 return result
def compare(cname,fname):
 c=dict(np.load(W/f'{cname}_trajectory.npz'));f=dict(np.load(W/f'{fname}_trajectory.npz'))
 assert np.allclose(c['t'],f['t'],atol=1e-12,rtol=0)
 cr=json.loads((W/f'{cname}_result.json').read_text());fr=json.loads((W/f'{fname}_result.json').read_text())
 lim=PLAN['refinement_limits']
 pos=float(np.linalg.norm(c['x']-f['x'],axis=2).max());vel=float(np.linalg.norm(c['v']-f['v'],axis=2).max())
 force=float((np.linalg.norm(c['reaction']-f['reaction'],axis=1)/np.maximum(np.linalg.norm(f['reaction'],axis=1),lim['force_floor_N'])).max())
 moment=float((np.linalg.norm(c['moment']-f['moment'],axis=1)/np.maximum(np.linalg.norm(f['moment'],axis=1),lim['moment_floor_Nm'])).max())
 damage=float(np.max(abs(c['history'][:,:,1]-f['history'][:,:,1])))
 failed=bool(np.array_equal(c['history'][:,:,1]>=1,f['history'][:,:,1]>=1))
 energy=float(max(abs(a['fracture_dissipation_J']-b['fracture_dissipation_J'])/max(abs(b['fracture_dissipation_J']),lim['dissipation_floor_J']) for a,b in zip(cr['rows'],fr['rows'])))
 event_error=0.;event_match=True
 for g in range(c['history'].shape[1]):
  for threshold in [0.,1.]:
   ca=c['history'][:,g,1]>0 if threshold==0 else c['history'][:,g,1]>=1
   fa=f['history'][:,g,1]>0 if threshold==0 else f['history'][:,g,1]>=1
   if ca.any()!=fa.any():event_match=False
   elif ca.any():event_error=max(event_error,abs(float(c['t'][np.flatnonzero(ca)[0]]-f['t'][np.flatnonzero(fa)[0]])))
 passed=pos<=lim['position_m'] and vel<=lim['velocity_m_s'] and force<=lim['force_relative'] and moment<=lim['moment_relative'] and damage<=lim['damage_absolute'] and energy<=lim['dissipation_relative'] and failed and event_match and event_error<=lim['event_time_s']
 out=dict(scope='Gate B loading segment only; controlled withdrawal and complete shallow-cut qualification remain pending',position_m=pos,velocity_m_s=vel,force_relative=force,moment_relative=moment,damage_absolute=damage,dissipation_relative=energy,failed_sets_equal=failed,events_match=event_match,event_time_difference_s=event_error,loading_comparison_passed=bool(passed),both_nonzero_damage=bool(cr['nonzero_damage'] and fr['nonzero_damage']),gate_b_passed=False)
 atomic(W/f'{cname}_{fname}_comparison.json',out)
 if not passed:raise RuntimeError('Independent loading refinement failed; see saved comparison')
 return out
try:
 assert json.loads((OLD/'bounded_pair_endpoint_review.json').read_text())['component_comparison_passed']
 assert json.loads((W/'guard_controls_result.json').read_text())['passed']
 cp=Path(PLAN['coarse_checkpoint']);fp=Path(PLAN['fine_checkpoint']);last=None
 for target in PLAN['segment_targets_s']:
  tag=f'{round(target*1000):04d}';cname='coarse'+tag;fname='fine'+tag
  run(cname,cp,target,False);run(fname,fp,target,True)
  last=compare(cname,fname);cp=W/f'{cname}_final.npz';fp=W/f'{fname}_final.npz'
  if last['both_nonzero_damage']:break
 title='Damage-producing loading verified' if last and last['both_nonzero_damage'] else 'Bounded loading comparisons finished'
 reason='Independent loading results saved. Controlled stopping/withdrawal still require qualification; no full stroke or separation has been launched.'
 atomic(W/'job_status.json',dict(running=False,phase='finished',updated=stamp(),reason=reason,last_comparison=last,gate_b_passed=False))
except Exception as e:
 title='Section 4 stopped at a declared gate';reason=str(e)
 atomic(W/'job_status.json',dict(running=False,phase='stopped',updated=stamp(),reason=reason,gate_b_passed=False))
publish(title,reason)
(W/'RESULT.txt').write_text((W/'EXECUTION.txt').read_text()+'\n\nFINAL JOB STATUS\n'+(W/'job_status.json').read_text()+'\n')
subprocess.run(['python',str(O/'build_disect_checklist_page.py')],check=True)
print((W/'job_status.json').read_text())
