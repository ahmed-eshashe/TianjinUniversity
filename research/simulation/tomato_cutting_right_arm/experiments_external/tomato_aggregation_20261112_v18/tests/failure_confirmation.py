"""Bounded diagnosis: distinguish time integration error from reduced-space error."""
from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate,vertex_fields
def snapshot(b):
 x,v=vertex_fields(b);U,f=b.energy_force();m=b.metrics()
 return {'x':x.copy(),'v':v.copy(),'force':f.copy(),'energy':U+m['T']}
def compare(t,r):
 df=np.array([a['force']-b['force'] for a,b in zip(t,r)]);rf=np.array([b['force'] for b in r]);fa=float(np.sqrt(np.mean(np.sum(df*df,axis=-1))));fr=float(np.sqrt(np.mean(np.sum(rf*rf,axis=-1))))
 return {'position_m':max(float(np.max(np.linalg.norm(a['x']-b['x'],axis=1))) for a,b in zip(t,r)), 'velocity_m_s':max(float(np.max(np.linalg.norm(a['v']-b['v'],axis=1))) for a,b in zip(t,r)),'force_rms_error_N':fa,'force_rms_reference_N':fr,'force_relative':fa/max(fr,1e-5)}
def accepted(d):return d['position_m']<=1e-4 and d['velocity_m_s']<=.005 and d['force_rms_error_N']<=max(1e-5,.05*d['force_rms_reference_N'])
rows=[];start=time.perf_counter()
try:
 for n,h,duration in [(4,.006,.02),(10,.006,.005),(20,.003,.002)]:
  b=Body(n=n,h=h);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2];b.split([1,.27,.13],.001)
  a=Aggregate(b);aa=Aggregate(b);r=GPU(b.clone(),.5e-6);rr=GPU(b.clone(),.25e-6);ta=[];taa=[];tr=[];trr=[];e0=b.metrics()['U'];dt=6.25e-6;t0=time.perf_counter()
  for i in range(round(duration/.001)):
   for j in range(round(.001/dt)):a.step(dt)
   for j in range(round(.001/(dt/2))):aa.step(dt/2)
   r.step(2000);r.export();rr.step(4000);rr.export();ta.append(snapshot(a.body));taa.append(snapshot(aa.body));tr.append(snapshot(r.body));trr.append(snapshot(rr.body))
   print('progress',n,i+1,flush=True)
  ah=compare(ta,taa);rh=compare(tr,trr);diff=compare(taa,trr);er=max(abs(x['energy']-e0)/e0 for x in ta+taa+tr+trr)
  row={'n':n,'h_m':h,'extent_m':n*h,'duration_s':duration,'aggregate_dt_s':dt,'aggregate_half_dt_s':dt/2,'reference_dt_s':.5e-6,'reference_half_dt_s':.25e-6,'aggregate_halfstep':ah,'reference_halfstep':rh,'cross_model':diff,'aggregate_halfstep_pass':accepted(ah),'reference_halfstep_pass':accepted(rh),'cross_model_pass':accepted(diff),'all_energy_residual_relative':er,'energy_pass':er<=.05,'unresolved_nodes':len(a.report['unresolved_nodes']),'max_mass_block':a.report['max_mass_block'],'wall_s':time.perf_counter()-t0}
  rows.append(row);print(row,flush=True);(W/'failure_confirmation.partial.json').write_text(json.dumps(rows,indent=2))
 result={'status':'diagnosis_complete','rows':rows,'wall_s':time.perf_counter()-start}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'rows':rows,'wall_s':time.perf_counter()-start}
(W/'failure_confirmation.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
