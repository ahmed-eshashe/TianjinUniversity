"""Compare same loaded material at identical sample times, before GPU optimization."""
from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate,vertex_fields
rows=[];start=time.perf_counter()
def snapshot(b):
 x,v=vertex_fields(b);m=b.metrics();U,f=b.energy_force()
 return dict(x=x.copy(),v=v.copy(),force=f.copy(),energy=m['U']+m['T'])
def compare(t,r):
 df=np.array([a['force']-b['force'] for a,b in zip(t,r)]);rf=np.array([b['force'] for b in r]);fa=float(np.sqrt(np.mean(np.sum(df*df,axis=-1))));fr=float(np.sqrt(np.mean(np.sum(rf*rf,axis=-1))))
 return {'position_m':max(float(np.max(np.linalg.norm(a['x']-b['x'],axis=1))) for a,b in zip(t,r)), 'velocity_m_s':max(float(np.max(np.linalg.norm(a['v']-b['v'],axis=1))) for a,b in zip(t,r)),'force_rms_error_N':fa,'force_rms_reference_N':fr,'force_relative':fa/max(fr,1e-5)}
def accepted(d):return d['position_m']<=1e-4 and d['velocity_m_s']<=.005 and d['force_rms_error_N']<=max(1e-5,.05*d['force_rms_reference_N'])
try:
 for name,normal,offset,front in [('intact',None,0,None),('oblique',[1,.27,.13],.001,None),('corner1um',[1,1,1],1e-6,None),('partial_oblique',[1,.27,.13],.001,([0,-1,0],0))]:
  b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2]
  if normal is not None:b.split(normal,offset,front=front)
  a=Aggregate(b);c=Aggregate(b);ref=GPU(b.clone(),dt=.5e-6);ta=[];tc=[];tr=[];e0=snapshot(b)['energy'];t0=time.perf_counter();dt=12.5e-6
  for sample in range(20):
   for _ in range(round(.001/dt)):a.step(dt)
   for _ in range(round(.001/(dt/2))):c.step(dt/2)
   ref.step(2000);ref.export();ta.append(snapshot(a.body));tc.append(snapshot(c.body));tr.append(snapshot(ref.body))
  er=max(abs(s['energy']-e0)/e0 for s in ta+tc);half=compare(ta,tc);original=compare(tc,tr)
  row={'case':name,'n':4,'h_m':.006,'duration_s':.02,'aggregate_dt_s':dt,'half_dt_s':dt/2,'v17_dt_s':.5e-6,'halfstep':half,'v17_comparison':original,'energy_drift_relative':er,'halfstep_pass':accepted(half) and er<=.05,'v17_comparison_pass':accepted(original),'wall_s':time.perf_counter()-t0,'aggregate_nodes':len(a.q),'mass_block_max':a.report['max_mass_block']}
  rows.append(row);print(row,flush=True);a.body.save(W/'states'/f'{name}_aggregate_final.npz');ref.body.save(W/'states'/f'{name}_v17_final.npz');(W/'dynamic_screen.partial.json').write_text(json.dumps(rows,indent=2))
 result={'status':'pass' if all(r['halfstep_pass'] and r['v17_comparison_pass'] for r in rows) else 'failed_accuracy_gate','rows':rows,'wall_s':time.perf_counter()-start,'physical_cut_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'failed_exception','exception':repr(e),'rows':rows,'wall_s':time.perf_counter()-start}
(W/'dynamic_screen.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
