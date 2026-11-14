"""Finite paired loading continuation; stops at first failed physical/accuracy gate.
No solver search, no force-law changes, no full-cut or training launch.
"""
from pathlib import Path
import subprocess,time,json,datetime,os,traceback,numpy as np
W=Path(__file__).resolve().parent;O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');L=W.parent/'disect_numerics_20261108_v05/run.sh';parts={'coarse':['screen'],'fine':[]};current={'coarse':.02,'fine':0.};last={'coarse':W/'screen_final.npz','fine':None};start=time.perf_counter()
def atomic(p,d):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(p)
def phase(name,reason,live=None):
 atomic(W/'loading_status.json',dict(phase=name,reason=reason,updated=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=os.getpid(),parts=parts,completed_sim_s=current,cutting_qualified=False))
 d=json.loads((O/'disect-execution-checklist.json').read_text());d['current_work'].update(eyebrow='Section 4 · paired corrected loading',title=name.replace('_',' '),description=reason,href='disect-section4-current.txt');d['updated']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds');d['live']=None
 if live:
  for k in ['progress','result']:
   p=O/f'section4-current-{k}.json'
   if p.is_symlink():p.unlink()
   elif p.exists():raise RuntimeError('Non-symlink live evidence cannot be replaced')
   p.symlink_to(W/f'{live[0]}_{k}.json')
  d['live']=dict(label=live[0],progress='section4-current-progress.json',result='section4-current-result.json',duration_s=live[1],kind='contact')
 atomic(O/'disect-execution-checklist.json',d)
def run(kind,end):
 name=f'{kind}{round(end*1000):04d}';args=['bash',str(L),str(W/'corrected_shallow.py'),'--until',str(end),'--name',name]
 if kind=='fine':args+=['--refined']
 if last[kind] is not None:args+=['--resume',str(last[kind])]
 phase(kind+'_loading_running',f'{kind.capitalize()} corrected loading to {end:.3f}s of the 0.160s stroke. Same original laws and stops; actual damage and smaller-step agreement remain required.',(name,end))
 with (W/f'{name}.log').open('w') as log:r=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(f'{name} exited{r.returncode}; see log')
 result=json.loads((W/f'{name}_result.json').read_text());parts[kind].append(name);current[kind]=result['duration_s'];last[kind]=W/f'{name}_final.npz'
 if not result['completed_window']:raise RuntimeError(f'{name} stopped: '+result['stop'])
def aggregate(kind,end):
 arrays={k:[] for k in ['t','x','v','reaction','moment','history']};rows=[];wall=0.
 for j,name in enumerate(parts[kind]):
  z=np.load(W/f'{name}_trajectory.npz');r=json.loads((W/f'{name}_result.json').read_text());sl=slice(None) if j==0 else slice(1,None)
  if j and abs(float(z['t'][0])-rows[-1]['sim_s'])>1e-12:raise RuntimeError('Checkpoint clock gap')
  for k in arrays:arrays[k].append(z[k][sl])
  rows+=r['rows'][sl];wall+=r['wall_s']
 out={k:np.concatenate(v) for k,v in arrays.items()};assert abs(out['t'][-1]-end)<1e-12;return out,rows,wall
def compare(end):
 a,ra,wa=aggregate('coarse',end);b,rb,wb=aggregate('fine',end);assert np.allclose(a['t'],b['t'],atol=1e-12,rtol=0)
 def rel(k,f):return float(np.max(np.linalg.norm(a[k]-b[k],axis=1)/np.maximum(np.linalg.norm(b[k],axis=1),f)))
 ha=a['history'];hb=b['history'];event=True
 for g in range(47):
  for threshold in [0.,1.-1e-12]:
   aa=np.flatnonzero(ha[:,g,1]>threshold);bb=np.flatnonzero(hb[:,g,1]>threshold)
   if bool(len(aa))!=bool(len(bb)) or (len(aa) and abs(a['t'][aa[0]]-b['t'][bb[0]])>.0005+1e-12):event=False
 da=np.array([r['fracture_dissipation_J'] for r in ra]);db=np.array([r['fracture_dissipation_J'] for r in rb]);out=dict(scope='Paired loading prefix only; full shallow-case withdrawal and qualification remain pending',prefix_sim_s=end,position_max_m=float(np.linalg.norm(a['x']-b['x'],axis=2).max()),velocity_max_m_s=float(np.linalg.norm(a['v']-b['v'],axis=2).max()),force_max_relative_or_floor=rel('reaction',1e-6),moment_max_relative_or_floor=rel('moment',1e-8),damage_max_absolute=float(abs(ha[:,:,1]-hb[:,:,1]).max()),dissipation_max_relative_or_floor=float(np.max(abs(da-db)/np.maximum(abs(db),1e-8))),events_agree=event,final_failed_groups_agree=bool(np.array_equal(ha[-1,:,1]>=1,hb[-1,:,1]>=1)),coarse_wall_s=wa,fine_wall_s=wb,coarse_actual_damage=bool(ha[-1,:,1].max()>0),fine_actual_damage=bool(hb[-1,:,1].max()>0),gate_b_passed=False)
 out['prefix_accuracy_passed']=bool(out['position_max_m']<=.0001 and out['velocity_max_m_s']<=.005 and out['force_max_relative_or_floor']<=.05 and out['moment_max_relative_or_floor']<=.05 and out['damage_max_absolute']<=.01 and out['dissipation_max_relative_or_floor']<=.05 and event and out['final_failed_groups_agree']);atomic(W/f'loading_compare_{round(end*1000):04d}.json',out)
 np.savez_compressed(W/f'loading_coarse_{round(end*1000):04d}.npz',**a);np.savez_compressed(W/f'loading_fine_{round(end*1000):04d}.npz',**b)
 if not out['prefix_accuracy_passed']:raise RuntimeError(f'Loading refinement failed at{end:.3f}s; see comparison')
 return out
try:
 assert json.loads((W/'screen_comparison_result.json').read_text())['passed']
 for end in [.04,.08,.12,.16]:
  run('coarse',end);run('fine',end);phase('comparing_loading_prefix',f'Reviewing common-time motion, force/moment, damage, energy and events through{end:.3f}s.');r=compare(end)
 phase('loading_complete_pending_review','Paired corrected loading completed and compared. Review genuine damage and controlled stop before any long retreat or full stroke. Gate B not automatically complete.')
except Exception as e:
 phase('stopped_at_loading_gate',str(e));(W/'loading_exception.txt').write_text(traceback.format_exc());raise
