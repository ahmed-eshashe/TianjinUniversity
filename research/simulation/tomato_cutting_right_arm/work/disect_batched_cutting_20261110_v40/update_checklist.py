"""Publish only observed process/result state; never qualifies a cutting milestone."""
from pathlib import Path
import datetime,json,os,sys
W=Path(__file__).resolve().parent;O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');name=sys.argv[1] if len(sys.argv)>1 else 'initial0045'
p=json.loads((W/f'{name}_progress.json').read_text());rp=W/f'{name}_result.json';r=json.loads(rp.read_text()) if rp.exists() else None
pid=p.get('pid');alive=False
if pid:
 try:alive='loading.py' in Path(f'/proc/{pid}/cmdline').read_bytes().decode(errors='replace')
 except FileNotFoundError:pass
running=bool(alive and r is None);s=p.get('actual_accepted_sim_s',p['sim_s']);horizon=.045 if name=='initial0045' else (r['window_until_s'] if r else p.get('window_until_s',None));stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
headline='Fresh corrected-contact loading in progress' if running else 'Loading window finished — review required'
summary=f"Accepted {s*1000:.3f} ms; damage {p['damage_max']:.6g}; sampled blade force {p['sum_force_N']:.6g} N. {'Running' if running else 'Stopped'}; no cutting milestone qualified. Speed deferred; experimental validation pending."
report='SECTION 4 — '+headline.upper()+'\n'+summary+'\nObserved '+stamp+'\nSource '+str(W/f'{name}_progress.json')+'\n'
if r:report+='Stop: '+r['stop']+'\nStepping/sampling wall seconds: '+str(r['wall_s'])+'\n'
for target in [W/'STATUS.txt',O/'disect-section4-current.txt']:
 tmp=target.with_suffix('.tmp');tmp.write_text(report);os.replace(tmp,target)
target=O/'disect-execution-checklist.json';d=json.loads(target.read_text());d['updated']=stamp;d['current_work'].update(eyebrow='Section 4 · '+('bounded loading running' if running else 'bounded loading stopped'),title=headline,description=summary,href='disect-section4-current.txt');d['section4_execution'].update(running=running,current_job_directory=str(W),last_accepted_time_s=s,next_runner_launched=True,stop=None if running else r['stop'] if r else 'Process exited without result; inspect log',latest_review=str(W/f'{name}_review.json') if (W/f'{name}_review.json').exists() else str(W/f'{name}_progress.json'));tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');os.replace(tmp,target);print(summary)

lines=['DiSECt execution checklist', 'Updated: '+stamp, report.strip(), '']
for stage in d['stages']:
 lines.extend([stage['title'],''])
 if stage.get('component_checks'):
  lines.append('Prerequisite controls (separate from cutting milestones):')
  for item in stage['component_checks']:lines.extend(['['+item['status']+' component] '+item['task'],'  '+item['acceptance_or_limit']])
  lines.extend(['','Cutting milestones:'])
 for item in stage['items']:lines.extend(['['+item['status']+'] '+item['task'],'  '+item['acceptance_or_limit']])
 lines.append('')
target=O/'disect-execution-checklist.txt';tmp=target.with_suffix('.tmp');tmp.write_text('\n'.join(lines)+'\n');os.replace(tmp,target)
