"""Only finish the declared 20 ms prefix and its independent half-step repeat.
Never launches a full stroke/training or marks Gate B complete automatically.
"""
from pathlib import Path
import subprocess,json,os,signal,datetime,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1]
O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
L=R/'work/disect_numerics_20261108_v05/run.sh'
def atomic(p,d):
 temp=p.with_suffix('.tmp');temp.write_text(json.dumps(d,indent=2));os.replace(temp,p)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def checklist(title,description,name=None):
 p=O/'disect-execution-checklist.json';d=json.loads(p.read_text())
 d['updated']=stamp();d['current_work']={'eyebrow':'Section 4 · bounded 20 ms comparison','title':title,'description':description,'href':'disect-section4-current.txt'}
 d['live']=None
 if name:
  for label,target in [('disect-v27-progress.json',f'{name}_progress.json'),('disect-v27-result.json',f'{name}_result.json')]:
   p0=O/label
   if p0.is_symlink():p0.unlink()
   if p0.exists():raise RuntimeError('Refusing to replace a non-symlink status file')
   p0.symlink_to(W/target)
  d['live']={'label':'Adaptive contact '+name,'kind':'contact','duration_s':.02,'progress':'disect-v27-progress.json','result':'disect-v27-result.json'}
 atomic(p,d)
 lines=[d['title'],'Updated: '+d['updated'],'',title,description,'']
 for stage in d['stages']:
  lines.append(stage['title'])
  for item in stage['items']:lines.extend([f"[{item['status']}] {item['task']}",'  '+item.get('acceptance_or_limit','')])
  lines.append('')
 (O/'disect-execution-checklist.txt').write_text('\n'.join(lines)+'\n')
def run(name,extra,cap):
 command=['bash',str(L),str(W/'resume_edge_shallow.py'),'--until','.02','--name',name,'--wall-cap',str(cap),*extra]
 atomic(W/f'{name}_execution.json',dict(command=command,started=stamp(),wall_cap_between_samples_s=cap))
 checklist('Bounded moving-stroke comparison running','Contact controls pass. Finishing the 20 ms prefix, then independently repeating at half the timestep. No qualified damage-producing cut or separation yet.',name)
 with (W/f'{name}.log').open('w') as log:
  p=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  atomic(W/'pair_status.json',dict(running=True,phase=name,pid=p.pid,supervisor_pid=os.getpid(),updated=stamp()))
  try:code=p.wait(timeout=cap+600)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=30)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   raise RuntimeError(f'{name}: supervisor timeout; last checkpoint preserved')
 if code:raise RuntimeError(f'{name}: process exit {code}; inspect preserved log/checkpoint')
 result=json.loads((W/f'{name}_result.json').read_text())
 if not result['completed_window']:raise RuntimeError(f"{name}: {result['stop']} at {result['duration_s']} s; checkpoint preserved, no qualification")
 return result
def compare():
 names=['moving0020','resume0020'];pieces=[dict(np.load(W/f'{n}_trajectory.npz')) for n in names]
 coarse={k:np.concatenate([pieces[0][k],pieces[1][k][1:]]) for k in pieces[0]}
 fine=dict(np.load(W/'fine0020_trajectory.npz'))
 assert np.allclose(coarse['t'],fine['t'],atol=1e-12,rtol=0)
 pos=float(np.linalg.norm(coarse['x']-fine['x'],axis=2).max())
 vel=float(np.linalg.norm(coarse['v']-fine['v'],axis=2).max())
 force=float((np.linalg.norm(coarse['reaction']-fine['reaction'],axis=1)/np.maximum(np.linalg.norm(fine['reaction'],axis=1),1e-6)).max())
 moment=float((np.linalg.norm(coarse['moment']-fine['moment'],axis=1)/np.maximum(np.linalg.norm(fine['moment'],axis=1),1e-8)).max())
 damage=float(np.max(abs(coarse['history'][:,:,1]-fine['history'][:,:,1])))
 failed=bool(np.array_equal(coarse['history'][:,:,1]>=1,fine['history'][:,:,1]>=1))
 passed=pos<=1e-4 and vel<=.005 and force<=.05 and moment<=.05 and damage<=.01 and failed
 return dict(scope='20 ms component prefix only; no completed damage/withdrawal qualification',position_m=pos,velocity_m_s=vel,force_relative=force,moment_relative=moment,damage_max_difference=damage,failed_sets_equal=failed,component_comparison_passed=bool(passed),gate_b_passed=False)
try:
 assert json.loads((W/'candidate_controls_gate.json').read_text())['passed']
 manifest={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in [W/'resume_edge_shallow.py',W/'run_bounded_pair.py',W/'adaptive_contact.py',W/'adaptive_blade.py',W/'correction_plan.json']}
 atomic(W/'bounded_pair_source_manifest.json',manifest)
 run('resume0020',['--resume',str(W/'moving0020_final.npz')],1200)
 run('fine0020',['--refined'],1800)
 comparison=compare();atomic(W/'bounded_pair_comparison.json',comparison)
 atomic(W/'pair_status.json',dict(running=False,phase='finished',updated=stamp(),**comparison))
 title='Bounded prefix comparison '+('passed' if comparison['component_comparison_passed'] else 'failed')
 text='The 20 ms moving prefix and independent half-step repeat have finished. This remains component evidence; damage-producing shallow-cut/withdrawal and separation qualification are pending. See the saved comparison.'
 checklist(title,text)
except Exception as e:
 title='Bounded comparison stopped; qualification pending';text=str(e)
 atomic(W/'pair_status.json',dict(running=False,phase='stopped',reason=text,updated=stamp(),gate_b_passed=False))
 checklist(title,text)
with (O/'disect-section4-current.txt').open('a') as f:f.write('\n\nBOUNDED PAIR STATUS — '+stamp()+'\n'+title+'\n'+text+'\nEvidence: '+str(W/'pair_status.json')+'\n')
subprocess.run(['python',str(O/'build_disect_checklist_page.py')],check=True)
print(json.dumps(json.loads((W/'pair_status.json').read_text()),indent=2))
