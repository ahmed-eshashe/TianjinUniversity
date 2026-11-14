"""Gate-B comparison on every saved common physical time; no event alignment."""
from pathlib import Path
import argparse,json,numpy as np
W=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--coarse',nargs='+',required=True);p.add_argument('--fine',nargs='+',required=True);p.add_argument('--output',default='comparison_result.json');a=p.parse_args()
def bundle(names):
 frames={};rows={};runs=[]
 for sequence_index,name in enumerate(names):
  result=json.loads((W/f'{name}_result.json').read_text());runs.append(result)
  if sequence_index:assert abs(result['start_step']*result['dt_s']-runs[-2]['duration_s'])<1e-12, 'missing continuation interval'
  z=np.load(W/f'{name}_trajectory.npz');arrays={k:z[k] for k in ['x','v','reaction','moment','history']}
  for i,t in enumerate(z['t']):
   key=round(float(t),12);frame={k:values[i] for k,values in arrays.items()}
   if key in frames:
    for k in ['x','v','history']:assert np.array_equal(frames[key][k],frame[k]),('inconsistent restart',key,k)
   frames[key]=frame
  for r in result['rows']:rows[round(r['sim_s'],12)]=r
 return frames,rows,runs
c,cr,cc=bundle(a.coarse);f,fr,ff=bundle(a.fine);assert cc[0]['dt_s']==2*ff[0]['dt_s'];times=sorted(c);assert set(c)==set(f) and times[0]==0
assert np.allclose(np.diff(times),.0005,rtol=0,atol=1e-12), 'missing saved physical times'
maxima=dict(position_m=0.,velocity_m_s=0.,force_relative=0.,sum_force_relative=0.,moment_relative=0.,damage_absolute=0.,dissipation_relative=0.);worst={}
def update(k,value,t):
 if value>maxima[k]:maxima[k]=float(value);worst[k]=t
for t in times:
 x,y=c[t],f[t];update('position_m',np.linalg.norm(x['x']-y['x'],axis=1).max(),t);update('velocity_m_s',np.linalg.norm(x['v']-y['v'],axis=1).max(),t)
 for key,floor,out in [('reaction',1e-6,'force_relative'),('moment',1e-8,'moment_relative')]:update(out,np.linalg.norm(x[key]-y[key])/max(np.linalg.norm(y[key]),floor),t)
 update('damage_absolute',np.abs(x['history'][:,1]-y['history'][:,1]).max(),t);update('sum_force_relative',abs(cr[t]['sum_force_N']-fr[t]['sum_force_N'])/max(fr[t]['sum_force_N'],1e-6),t);update('dissipation_relative',abs(cr[t]['fracture_dissipation_J']-fr[t]['fracture_dissipation_J'])/max(fr[t]['fracture_dissipation_J'],1e-8),t)
def events(frames):
 result={}
 for g in range(47):
  for kind,threshold in [('onset',0.),('failure',1.-1e-12)]:
   hits=[i for i,t in enumerate(times) if frames[t]['history'][g,1]>threshold]
   # Failure canonical damage equals one; use >= at the declared threshold.
   if kind=='failure':hits=[i for i,t in enumerate(times) if frames[t]['history'][g,1]>=1.]
   if hits:
    i=hits[0];result[f'{g}:{kind}']=[times[max(0,i-1)],times[i]]
 return result
ce,fe=events(c),events(f);event_set_equal=set(ce)==set(fe);event_time_bound=max([max(abs(ce[k][0]-fe[k][1]),abs(ce[k][1]-fe[k][0])) for k in set(ce)&set(fe)]+[0.]);failed_equal=np.array_equal(c[times[-1]]['history'][:,1]>=1,f[times[-1]]['history'][:,1]>=1)
limits=dict(position_m=1e-4,velocity_m_s=.005,force_relative=.05,sum_force_relative=.05,moment_relative=.05,damage_absolute=.01,dissipation_relative=.05)
physical=all(r['admissible'] for runs in [cc,ff] for run in runs for r in run['rows']) and all(runs[-1]['completed_window'] and all(run['stop'] in ['wall_cap','window_completed','completed','damage_event_window'] for run in runs) for runs in [cc,ff])
passed=bool(physical and all(maxima[k]<=limits[k] for k in maxima) and event_set_equal and event_time_bound<=.0005+1e-12 and failed_equal)
damage=bool(c[times[-1]]['history'][:,1].max()>0 and f[times[-1]]['history'][:,1].max()>0)
out=dict(scope='Fresh corrected-reference runs, all shared samples, no event shifting or resampling; component refinement alone is not a controlled cut/unload pass',shared_samples=len(times),end_time_s=times[-1],maxima=maxima,worst_times_s=worst,limits=limits,physical_passed=physical,event_set_equal=event_set_equal,event_time_conservative_bound_s=event_time_bound,coarse_event_intervals=ce,fine_event_intervals=fe,final_failed_sets_equal=failed_equal,both_nonzero_damage=damage,refinement_passed=passed,gate_b_passed=False)
(W/a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
