from pathlib import Path
import sys,time,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from fast_aggregation import Aggregate,vertex_fields
from reference_gpu_v19 import GPU as Old
from selective_gpu import GPU as New
import warp as wp
rows=[];checks={}
for case,n,d in [('intact',None,0),('oblique',[1,.27,.13],.001),('corner',[1,1,1],1e-6)]:
 b=Body(n=10);b.u[:,1]=-.001*b.grid[:,1];b.u[:,0]=.0005*b.grid[:,2]
 if n is not None:b.split(n,d)
 gs=[G(Aggregate(b),12.5e-6,batch=8) for G in [Old,New]];initial=[[wp.clone(g.q),wp.clone(g.vh)] for g in gs];times=[[],[]]
 for g in gs:g.graph(64);g.step(1600)
 for repeat in range(5):
  for k in ([0,1] if repeat%2==0 else [1,0]):
   g=gs[k];wp.copy(g.q,initial[k][0]);wp.copy(g.vh,initial[k][1]);g.steps=0;wp.synchronize();t=time.perf_counter();g.step(1600);wp.synchronize();times[k].append(time.perf_counter()-t)
 a,z=[g.export() for g in gs];x,v=vertex_fields(a);y,w=vertex_fields(z);dx=float(np.max(np.linalg.norm(x-y,axis=1)));dv=float(np.max(np.linalg.norm(v-w,axis=1)));df=float(np.max(abs(a.fields()[2]-z.fields()[2])))
 checks[case]=dx<=1e-6 and dv<=1e-4 and df<=1e-4
 row={'case':case,'batch':8,'old_wall_s':times[0],'new_wall_s':times[1],'matched_speedup':float(np.median(times[0])/np.median(times[1])),'old_material_equivalents_s':float(8/np.median(times[0])),'new_material_equivalents_s':float(8/np.median(times[1])),'position_m':dx,'velocity_m_s':dv,'F':df};rows.append(row);print(row,flush=True)
result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'scope':'Material only, fixed topology, 60 mm cube / 6 mm grid / 0.1% compression / 0.05% shear / 12.5 us. Alternating-order five-repeat matched medians; setup/reset/export excluded.'}
(W/'matched_cost.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
