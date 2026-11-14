"""Finite fresh hold+half-step qualification; one GPU worker, no auto retries/cuts."""
from pathlib import Path
import os,sys,time,json,subprocess,datetime,traceback
W=Path(__file__).resolve().parent;O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');launch=W.parent/'disect_numerics_20261108_v05/run.sh'
def atomic(p,d):
 q=p.with_suffix('.tmp');q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p)
def workers():
 out=[]
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:
    argv=(p/'cmdline').read_bytes().split(b'\0')
    if str(W/'settle.py').encode() in argv:out.append(int(p.name))
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 return out
def publish(phase,running,detail,**kw):
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();state=dict(phase=phase,running=running,detail=detail,updated=now,supervisor_pid=os.getpid(),**kw);atomic(W/'qualification_status.json',state)
 p=O/'disect-execution-checklist.json';d=json.loads(p.read_text());d['updated']=now;d['current_work']={'eyebrow':'Section 4 · separate approved material candidate','title':phase.replace('_',' ').capitalize(),'description':detail,'href':'disect-section4-current.txt'};d['current_job_directory']=str(W);d['section4_execution'].update(current_job_directory=str(W),running=running,stop=None if running else phase,material_candidate_user_approved=True,material_candidate_qualified=False,next_action=detail,material_qualification_status=str(W/'qualification_status.json'));d['latest_section4_execution'].update(running=running,material_scope_decision_pending=False,candidate_directory=str(W))
 if running and phase in ['fresh_coarse_settling_running','fresh_half_step_settling_running']:
  stem='settle_contact_refined' if phase=='fresh_half_step_settling_running' else 'settle_contact'
  d['live']={'kind':'settling','label':'New material · '+('half-step' if 'refined' in stem else 'coarse')+' fresh hold','progress':'disect-material-'+stem+'_progress.json','result':'disect-material-'+stem+'_result.json','duration_s':1.}
 else:d['live']=None
 atomic(p,d)
 text=phase.replace('_',' ').upper()+'\n'+detail+'\n\nUpdated '+now+'\nNo new cutting milestone, damage or separation pass. Speed deferred; experimental validation pending.\nEvidence: '+str(W)+'\n';(W/'STATUS.txt').write_text(text);(O/'disect-section4-current.txt').write_text(text)
 lines=[d['title'],'Updated '+now,'',text]
 for i,stage in enumerate(d['stages'],1):
  lines.append(str(i)+'. '+stage.get('title',''))
  for item in stage['items']:lines.extend(['  ['+item['status']+'] '+item['task'],'    '+item.get('acceptance_or_limit','')])
 (O/'disect-execution-checklist.txt').write_text('\n'.join(lines)+'\n')
def load(name):return json.loads((W/name).read_text())
def wait_coarse():
 begin=time.monotonic()
 while True:
  procs=workers()
  if (W/'settle_contact_result.json').exists() and not procs:return
  if not procs and time.monotonic()-begin>20:raise RuntimeError('Coarse worker ended without complete result; no automatic restart')
  prog=load('settle_contact_progress.json') if (W/'settle_contact_progress.json').exists() else {}
  sim=prog.get('sim_s',0);wall=prog.get('wall_s',0)
  publish('fresh_coarse_settling_running',True,f'New E0.4MPa / nu0.3 candidate: fresh supported hold {sim:.3f}/1.000 simulated seconds. Independent constitutive and packet-isolation checks passed. Half-step run starts only if this hold passes. No cutting or separation qualification.',worker_pids=procs,completed_sim_s=sim,planned_sim_s=1.,wall_s=wall)
  time.sleep(10)
def run(script,log,*args):
 with (W/log).open('w') as f:
  p=subprocess.Popen(['bash',str(launch),str(W/script),*args],stdout=f,stderr=subprocess.STDOUT)
  while p.poll() is None:
   if script=='settle.py':
    prog=load('settle_contact_refined_progress.json') if (W/'settle_contact_refined_progress.json').exists() else {}
    sim=prog.get('sim_s',0)
    publish('fresh_half_step_settling_running',True,f'Coarse fresh hold passed its own guards. Independent half-step hold {sim:.3f}/1.000 simulated seconds; comparison still pending. No contact/cutting pass.',worker_pid=p.pid,completed_sim_s=sim,planned_sim_s=1.)
   time.sleep(10)
  if p.returncode:raise RuntimeError(f'{script} exited {p.returncode}; inspect {log}')
try:
 assert load('packet_isolation.json')['passed'] and load('constitutive_controls.json')['passed']
 wait_coarse()
 if not load('settle_contact_result.json')['settling_passed']:raise RuntimeError('Fresh coarse hold failed: '+load('settle_contact_result.json')['stop'])
 run('settle.py','settle_contact_refined.log','--refined')
 if not load('settle_contact_refined_result.json')['settling_passed']:raise RuntimeError('Independent fresh half-step hold failed: '+load('settle_contact_refined_result.json')['stop'])
 publish('reviewing_fresh_settling_comparison',True,'Both independent fresh holds completed; assessing unchanged motion, force, support and residual tolerances.')
 run('qualify_settling.py','settling_comparison.log')
 assert load('settling_qualification.json')['passed']
 publish('fresh_settling_qualified_contact_not_yet_qualified',False,'Fresh coarse and independent half-step hold plus comparison passed. This qualifies supported settling for the new candidate only. Next required work: recompute whole-material CAD clearance from the new settled state, freeze load/unload probe, and qualify contact before any cutting. No automatic cutting run launched.',fresh_settling_qualified=True)
except Exception as exc:
 (W/'sequence_exception.txt').write_text(traceback.format_exc());publish('stopped_at_fresh_material_gate',False,str(exc)+'. No follow-on simulation or retry launched.',error=str(exc))
