"""CPU/GPU geometric history loop, with every setup/export/reset cost counted.

These are geometric diagnostic events, never paid blade fracture or RL steps.
"""
from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body as RefBody
from local_geometry import Body as LocalBody
from aggregation import Aggregate as RefAggregate
from fast_aggregation import Aggregate as FastAggregate,vertex_fields
from reference_gpu_v19 import GPU as RefGPU
from selective_gpu import GPU
import warp as wp
dt=12.5e-6;rows=[];checks={};series={};timings=[]

def compare(a,b):
 topology=np.array_equal(a.ids,b.ids) and np.array_equal(a.codes,b.codes) and len(a.polys)==len(b.polys)
 if not topology:return {'topology_equal':False},False
 x,v=vertex_fields(a);y,w=vertex_fields(b)
 dx=float(np.max(np.linalg.norm(x-y,axis=1)));dv=float(np.max(np.linalg.norm(v-w,axis=1)));df=float(np.max(abs(a.fields()[2]-b.fields()[2])))
 return {'topology_equal':True,'position_m':dx,'velocity_m_s':dv,'F':df},dx<=1e-6 and dv<=1e-4 and df<=1e-4

def episode(optimized=True,n=4,events=True):
 B=LocalBody if optimized else RefBody;A=FastAggregate if optimized else RefAggregate;G=GPU if optimized else RefGPU
 timer={k:0. for k in ['body_reset','geometry_update','aggregate','GPU_setup_graph','material_advance','observation_export']}
 start=time.perf_counter();t=time.perf_counter();b=B(n=n);b.u[:,1]=-.001*b.grid[:,1];b.u[:,0]=.0005*b.grid[:,2];timer['body_reset']+=time.perf_counter()-t
 t=time.perf_counter();ag=A(b);timer['aggregate']+=time.perf_counter()-t;t=time.perf_counter();g=G(ag,dt);g.graph(64);wp.synchronize();timer['GPU_setup_graph']+=time.perf_counter()-t
 states=[];updates=[];maxenergy=0.;initialmass=b.mass.sum();initialenergy=b.metrics()['U']
 # Ten 50 Hz controls. Four on-the-fly front advances on one fixed plane.
 # Event geometry is chosen at each call, not supplied to reset or GPU setup.
 for frame in range(10):
  if events and frame in [1,3,5,7]:
   t=time.perf_counter();b=g.export().clone();timer['observation_export']+=time.perf_counter()-t
   front_y=[-.25,0,.25,.6][[1,3,5,7].index(frame)]*n*b.config['h']
   t=time.perf_counter();b.split([1,.27,.13],.001,cut_id=0,front=([0,1,0],front_y));timer['geometry_update']+=time.perf_counter()-t
   updates.append({'frame':frame,'regions':len(b.V),'nodes':len(b.u),'components':len(np.unique(b.components()[0])),'detail':getattr(b,'last_update',None)})
   t=time.perf_counter();ag=A(b);timer['aggregate']+=time.perf_counter()-t;t=time.perf_counter();g=G(ag,dt);g.graph(64);wp.synchronize();timer['GPU_setup_graph']+=time.perf_counter()-t
  t=time.perf_counter();g.step(1600);wp.synchronize();timer['material_advance']+=time.perf_counter()-t
  t=time.perf_counter();out=g.export().clone();states.append(out);timer['observation_export']+=time.perf_counter()-t
  m=out.metrics();maxenergy=max(maxenergy,abs(m['U']+m['T']-initialenergy)/initialenergy)
  if abs(m['mass']/initialmass-1)>1e-6 or maxenergy>.05:raise ValueError(('loop conservation failed',m,maxenergy))
 elapsed=time.perf_counter()-start
 return states,{'optimized':optimized,'n':n,'extent_m':n*.006,'controls':10,'simulated_duration_s':.2,'events':events,'wall_s':elapsed,'actual_diagnostic_transitions_per_s':10/elapsed,'phase_wall_s':timer,'other_checks_wall_s':elapsed-sum(timer.values()),'maximum_energy_residual_relative':maxenergy,'updates':updates,'scope':'Includes fresh reset, initial setup, four geometric front updates, aggregate reconstruction, GPU upload/graph rebuilding, CPU observations and conservation checks. No blade/fracture/contact/robot/policy.'}
try:
 assert json.loads((W/'local_validation.json').read_text())['status']=='pass'
 assert json.loads((W/'gpu_validation.json').read_text())['status']=='pass'
 # Kernel compilation excluded from paired warm timing; setup/capture counted.
 for ctor in [RefGPU,GPU]:
  g=ctor(FastAggregate(LocalBody(n=2)));g.step(64)
 for n in [4,10]:
  pairs=[]
  for optimized in [False,True]:
   states,metrics=episode(optimized,n=n);timings.append(metrics);pairs.append(states);print(metrics,flush=True)
  for frame,(a,b) in enumerate(zip(*pairs)):
   err,ok=compare(a,b);checks[f'n{n}_frame{frame}']=ok;rows.append({'n':n,'frame':frame,**err})
  checks[f'n{n}_final_separated_geometry']=len(np.unique(pairs[1][-1].components()[0]))==2
  series[str(n)]={'matched_speedup':timings[-2]['wall_s']/timings[-1]['wall_s']}
 # Same reset/episode repeated once checks repeatability and counts resets.
 states,metrics=episode(True,n=4);timings.append(metrics)
 checks['repeat_reset_finite']=all(np.isfinite(b.u).all() for b in states)
 result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'timings':timings,'comparisons':series,'physical_cut':False,'RL_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'rows':rows,'timings':timings,'comparisons':series}
(W/'changing_loop.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
