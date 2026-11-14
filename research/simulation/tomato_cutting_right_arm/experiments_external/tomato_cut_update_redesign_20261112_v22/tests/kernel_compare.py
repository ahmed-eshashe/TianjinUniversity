from pathlib import Path
import sys,time,json,numpy as np,traceback
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from compiled_body import Body
from fast_aggregation import Aggregate
from persistent_gpu import GPU as Old
from fused_gpu import GPU as Four
from warp_gpu import GPU as One
import warp as wp
checks={};rows=[]
try:
 template=Body(n=10);template.u[:,1]=-.001*template.grid[:,1];template.split([1,.27,.13],.001);a=Aggregate(template)
 for C in [Old,Four,One]:g=C([a]);g.step(64)
 for batch in [1,8,32]:
  ags=[Aggregate(template) for j in range(batch)];states=[]
  for name,C in [('reference',Old),('four',Four),('one',One)]:
   g=C(ags);g.graph(64);times=[]
   for run in range(3):
    g.replace(ags);wp.synchronize();t=time.perf_counter();g.step(1600);wp.synchronize();times.append(time.perf_counter()-t)
   state=g.state();states.append(state);rows.append({'batch':batch,'method':name,'samples_s':times,'aggregate_material_control_steps_s':batch/np.median(times)});print(rows[-1],flush=True)
  for name,s in zip(['four','one'],states[1:]):
   dx=np.max(np.linalg.norm(s[0]-states[0][0],axis=1));dv=np.max(np.linalg.norm(s[1]-states[0][1],axis=1));checks[f'{name}_{batch}']=bool(dx<=1e-6 and dv<=1e-4);rows.append({'method':name,'batch':batch,'dx':float(dx),'dv':float(dv)})
 result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'scope':'Material-only; synthetic oblique cut, same dt and coupled inertia. Not an RL pass.'}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'rows':rows}
(W/'kernel_compare.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
