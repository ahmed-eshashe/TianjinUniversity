from pathlib import Path
import sys,time,json,traceback,numpy as np,concurrent.futures
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from local_geometry import Body as V20Body
from compiled_body import Body
from fast_aggregation import Aggregate
from selective_gpu import GPU as RebuildGPU
from persistent_gpu import GPU
from fast_data import reduced_data
import warp as wp
timings=[];checks={};differences=[]
def compare(a,b):
 if not np.array_equal(a.ids,b.ids) or not np.array_equal(a.codes,b.codes):return {'topology':False},False
 dx=dv=0.
 for i,(p,z) in enumerate(zip(a.polys,b.polys)):
  x=np.concatenate([p,z]);N=np.c_[np.ones(len(x)),x]@a.inv[i];M=np.c_[np.ones(len(x)),x]@b.inv[i]
  dx=max(dx,float(np.max(np.linalg.norm(N@a.u[a.ids[i]]-M@b.u[b.ids[i]],axis=1))));dv=max(dv,float(np.max(np.linalg.norm(N@a.v[a.ids[i]]-M@b.v[b.ids[i]],axis=1))))
 F=float(np.max(abs(a.fields()[2]-b.fields()[2])))
 return {'topology':True,'position_m':dx,'velocity_m_s':dv,'F':F},dx<=1e-6 and dv<=1e-4 and F<=1e-4
def episode(new=True,n=10,batch=1,warm_template=None,workers=1):
 B=Body if new else V20Body;phases={k:0. for k in ['reset','cut_and_aggregation','GPU_initial','GPU_replace','material','observations','checks']};start=time.perf_counter();t=time.perf_counter()
 bodies=[]
 for j in range(batch):
  b=B(n=n) if warm_template is None else warm_template.clone();b.u[:,1]=-(.001+j*.00002)*b.grid[:,1];b.u[:,0]=.0005*b.grid[:,2];bodies.append(b)
 ags=[Aggregate(b) for b in bodies];phases['reset']+=time.perf_counter()-t;t=time.perf_counter()
 if new:g=GPU(ags,capacity_factor=1.75)
 else:
  assert batch==1;g=RebuildGPU(ags[0])
 g.graph(64);wp.synchronize();phases['GPU_initial']+=time.perf_counter()-t;pointer0=g.q.ptr;graph0=id(g.graphs[64]);rows=[];states=[];m0=[b.mass.sum() for b in bodies];e0=[b.metrics()['U'] for b in bodies];maxenergy=0.;maxmass=0.
 def cut_task(args):
  j,b,frame=args
  # Distinct plane/offset and front sequence for each independent environment.
  front=[-.25,0,.25,.6][[1,3,5,7].index(frame)]*n*.006
  b.split([1,.27+j*.013,.13-j*.007],.001+j*.00005,cut_id=0,front=([0,1,0],front));return Aggregate(b)
 pool=concurrent.futures.ThreadPoolExecutor(max_workers=workers) if workers>1 else None
 try:
  for frame in range(10):
   if frame in [1,3,5,7]:
    t=time.perf_counter();bs=[b.clone() for b in g.export_all()] if new else [g.export().clone()];phases['observations']+=time.perf_counter()-t;t=time.perf_counter()
    args=[(j,b,frame) for j,b in enumerate(bs)];ags=list(pool.map(cut_task,args)) if pool else [cut_task(x) for x in args];phases['cut_and_aggregation']+=time.perf_counter()-t;t=time.perf_counter()
    if new:g.replace(ags)
    else:g=RebuildGPU(ags[0]);g.graph(64)
    wp.synchronize();phases['GPU_replace']+=time.perf_counter()-t
   t=time.perf_counter();g.step(1600);wp.synchronize();phases['material']+=time.perf_counter()-t;t=time.perf_counter()
   bs=[b.clone() for b in g.export_all()] if new else [g.export().clone()];states.append(bs);phases['observations']+=time.perf_counter()-t;t=time.perf_counter()
   for j,b in enumerate(bs):
    m=b.metrics();maxmass=max(maxmass,abs(m['mass']/m0[j]-1));maxenergy=max(maxenergy,abs(m['U']+m['T']-e0[j])/e0[j])
   if maxmass>1e-6 or maxenergy>.05:raise ValueError(('conservation failure',maxmass,maxenergy))
   phases['checks']+=time.perf_counter()-t
 finally:
  if pool:pool.shutdown()
 wall=time.perf_counter()-start
 metrics={'new':new,'n':n,'batch':batch,'workers':workers,'warm_geometry_template':warm_template is not None,'simulated_duration_per_body_s':.2,'controls_per_body':10,'geometry_events_per_body':4,'wall_s':wall,'diagnostic_transitions_per_s':10*batch/wall,'phases':phases,'maximum_mass_error_relative':maxmass,'maximum_energy_residual_relative':maxenergy,'graphs_and_storage_reused':new and g.q.ptr==pointer0 and id(g.graphs[64])==graph0,'array_memory_bytes':g.memory(),'scope':'Includes reset, four independent geometric events/body, aggregate preparation, GPU initialization/replacement, observations and conservation checks. No blade/contact/fracture/robot/policy.'}
 return states,metrics
try:
 assert json.loads((W/'native_validation.json').read_text())['status']=='pass'
 assert json.loads((W/'persistent_validation.json').read_text())['status']=='pass'
 # Compilation separate; reset-time preparation remains included in episodes.
 for new in [False,True]:
  a=Aggregate(Body(n=2));reduced_data(a);g=GPU([a]) if new else RebuildGPU(a);g.step(64)
 for n in [4,10]:
  pair=[]
  for new in [False,True]:
   s,m=episode(new,n);pair.append(s);timings.append(m);print(m,flush=True)
  for frame,(a,b) in enumerate(zip(*pair)):
   err,ok=compare(a[0],b[0]);checks[f'n{n}_frame{frame}']=ok;differences.append({'n':n,'frame':frame,**err})
  checks[f'n{n}_reuse']=timings[-1]['graphs_and_storage_reused']
 # Warm reset copies a pristine material template with NO future cut history.
 t=time.perf_counter();template=Body(n=10);template.prepare_geometry_cache();template_s=time.perf_counter()-t
 for workers in [1,4]:
  s,m=episode(True,10,batch=8,warm_template=template,workers=workers);timings.append(m);checks[f'batch8_workers{workers}_reuse']=m['graphs_and_storage_reused'];print(m,flush=True)
  if workers==1:serial=s
  else:
   for j in range(8):err,ok=compare(serial[-1][j],s[-1][j]);checks[f'parallel_identical_{j}']=ok;differences.append({'case':'thread_equivalence','environment':j,**err})
 result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'timings':timings,'differences':differences,'warm_template_preparation_s':template_s,'RL_qualified':False,'physical_cut':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'timings':timings,'differences':differences,'RL_qualified':False}
(W/'combined_loop.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
