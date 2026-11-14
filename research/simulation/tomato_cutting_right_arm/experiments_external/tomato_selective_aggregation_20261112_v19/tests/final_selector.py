from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate
from response import snap,diff,passes
start=time.perf_counter();rows=[];prior=json.loads((W/'response.json').read_text());threshold=1e-16
cases=[('intact',None,0,None),('oblique',[1,.27,.13],.001,None),('partial',[1,.27,.13],.001,([0,-1,0],0))]+[(f'corner_{d}',[1,1,1],d,None) for d in [1.3e-4,1e-5,1e-6,1e-7]]
def run_gpu(b,dt):
 g=GPU(b.clone(),dt);tr=[];e0=b.metrics();e0=e0['U']+e0['T']
 for _ in range(20):g.step(round(.001/dt));g.export();tr.append(snap(g.body))
 return tr,max(abs(s['energy']-e0)/max(e0,1e-10) for s in tr)
try:
 for name,normal,offset,front in cases:
  b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2]
  if normal is not None:b.split(normal,offset,front=front)
  a=Aggregate(b,threshold);match=None
  for old in prior['rows']:
   if old['case']!=name or not(old['halfstep_pass'] and old['cross_model_pass']):continue
   aa=Aggregate(b,old['threshold'])
   if np.array_equal(a.masters,aa.masters) and a.E.shape==aa.E.shape and (a.E!=aa.E).nnz==0 and (a.M!=aa.M).nnz==0:match=old;break
  if match is not None:
   row={'case':name,'threshold':threshold,'status':'pass_identical_operator_reuse','reused_threshold':match['threshold'],'operator_identity_verified':True,'dt_s':match['dt_s'],'cross_model':match['cross_model'],'halfstep':match['halfstep'],'energy_drift_relative':match['energy_drift_relative'],'aggregated_nodes':a.report['aggregated_nodes']};rows.append(row);print(row,flush=True);continue
  assert a.report['aggregated_nodes']==0,(name,'new nonidentity operator requires independent CPU test')
  rr,er=run_gpu(b,.0625e-6);rrh,erh=run_gpu(b,.03125e-6);ref=diff(rr,rrh);assert passes(ref),(name,'reference',ref)
  dt=3.125e-6
  while dt>=.048828125e-6:
   ta,ea=run_gpu(b,dt);th,eh=run_gpu(b,dt/2);half=diff(ta,th);cross=diff(th,rrh);ok=passes(half) and passes(cross) and max(ea,eh,er,erh)<.05
   row={'case':name,'threshold':threshold,'status':'pass' if ok else 'rejected_timestep','identity_extension':True,'dt_s':dt,'cross_model':cross,'halfstep':half,'reference_halfstep':ref,'energy_drift_relative':max(ea,eh,er,erh),'aggregated_nodes':0};rows.append(row);print(row,flush=True);(W/'final_selector.partial.json').write_text(json.dumps(rows,indent=2))
   if ok:break
   dt*=.5
  assert ok,(name,'no accepted timestep')
 result={'status':'pass_dynamic_selector' if all(any(r['case']==name and r['status'].startswith('pass') for r in rows) for name,*_ in cases) else 'failed','threshold':threshold,'rows':rows,'wall_s':time.perf_counter()-start,'speed_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'failed_exception','exception':repr(e),'threshold':threshold,'rows':rows,'wall_s':time.perf_counter()-start}
(W/'final_selector.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
