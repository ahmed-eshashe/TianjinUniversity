"""Matched force-cache accuracy and timing; no new physical approximation."""
from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from aggregation import Aggregate,vertex_fields
from selective_gpu import GPU
import warp as wp

dt=12.5e-6;steps=1600;rows=[];checks={};start=time.perf_counter()
b=Body(n=10);b.u[:,1]=-.001*b.grid[:,1];b.u[:,0]=.0005*b.grid[:,2];b.split([1,1,1],1e-6)
for batch in [1,8]:
 gs=[GPU(Aggregate(b,1e-8),dt,batch=batch,use_cached=cache) for cache in [False,True]]
 initial=[[wp.clone(g.q),wp.clone(g.vh)] for g in gs]
 for g in gs:g.graph(64);g.step(steps)
 times=[[],[]]
 for repeat in range(5):
  for k in ([0,1] if repeat%2==0 else [1,0]):
   g=gs[k];wp.copy(g.q,initial[k][0]);wp.copy(g.vh,initial[k][1]);g.steps=0;wp.synchronize();t=time.perf_counter();g.step(steps);wp.synchronize();times[k].append(time.perf_counter()-t)
 bs=[g.export() for g in gs];fields=[vertex_fields(body) for body in bs]
 dx=float(np.max(np.linalg.norm(fields[0][0]-fields[1][0],axis=1)));dv=float(np.max(np.linalg.norm(fields[0][1]-fields[1][1],axis=1)))
 fmax=float(np.max(abs(bs[0].fields()[2]-bs[1].fields()[2])));checks[f'cache_equivalence_batch_{batch}']=dx<=1e-6 and dv<=1e-4 and fmax<=1e-4
 rows.append({'batch':batch,'fused_wall_s':times[0],'cached_wall_s':times[1],'paired_speedup_medians':float(np.median(times[0])/np.median(times[1])),'fused_equivalent_steps_s':float(batch/np.median(times[0])),'cached_equivalent_steps_s':float(batch/np.median(times[1])),'position_max_m':dx,'velocity_max_m_s':dv,'F_max':fmax})
 print(rows[-1],flush=True)
# Short sustained material-only run: ten successive 20 ms controls, no resets.
g=gs[1];wp.copy(g.q,initial[1][0]);wp.copy(g.vh,initial[1][1]);g.steps=0;wp.synchronize();t=time.perf_counter()
for _ in range(10):g.step(steps)
wp.synchronize();wall=time.perf_counter()-t
out=g.export();m=out.metrics();e0=b.metrics()['U'];ed=abs(m['U']+m['T']-e0)/e0
checks['sustained_energy_screen']=ed<=.05
sustained={'batch':8,'duration_each_s':.2,'wall_s':wall,'equivalent_50Hz_steps_s':80/wall,'energy_residual_relative':ed,'scope':'Fixed topology, 0.1% compression + 0.05% shear, no observations/contact/history/robot. Energy screen only; not a long-horizon response validation.'}
result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'sustained':sustained,'dt_s':dt,'wall_s':time.perf_counter()-start}
(W/'cache_control.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
