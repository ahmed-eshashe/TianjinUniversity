from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate,vertex_fields
from response import snap,diff,passes
start=time.perf_counter();rows=[]
try:
 b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2];b.split([1,-1,1],1e-6);c=b.clone();a=Aggregate(b,1e-16);g=GPU(b.clone(),.0625e-6);tc=[];ta=[];tg=[];dt=.0625e-6
 for sample in range(2):
  for _ in range(16000):c.step(dt)
  for _ in range(640):a.step(1.5625e-6)
  g.step(16000);g.export();tc.append(snap(c));ta.append(snap(a.body));tg.append(snap(g.body));print('sample',sample+1,flush=True)
 ref=diff(tg,tc);cross=diff(ta,tc);row={'CPU_GPU_reference':ref,'candidate_CPU_reference':cross,'reference_dt_s':dt,'candidate_dt_s':1.5625e-6,'duration_s':.002,'CPU_GPU_reference_pass':ref['position_m']<=1e-6 and ref['velocity_m_s']<=1e-4,'candidate_pass':passes(cross)};rows.append(row)
 # Locate the material region carrying the largest velocity discrepancy.
 ptr=np.r_[0,np.cumsum([len(p) for p in b.polys])];dv=np.linalg.norm(ta[-1]['v']-tc[-1]['v'],axis=1);iv=int(np.argmax(dv));p=int(np.searchsorted(ptr,iv,side='right')-1);row['worst_region']={'index':p,'volume_m3':float(b.V[p]),'material_mass_fraction':float(b.V[p]/b.V.sum()),'vertex_m':b.polys[p][iv-ptr[p]].tolist(),'reference_velocity_m_s':tc[-1]['v'][iv].tolist(),'candidate_velocity_m_s':ta[-1]['v'][iv].tolist(),'reference_F':c.fields()[2][p].tolist(),'candidate_F':a.body.fields()[2][p].tolist()}
 result={'status':'diagnosis_complete','rows':rows,'wall_s':time.perf_counter()-start}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'rows':rows,'wall_s':time.perf_counter()-start}
(W/'heldout_reference_audit.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
