from pathlib import Path
import sys,time,json,traceback,concurrent.futures,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from compiled_body import Body
from fast_aggregation import Aggregate
from fast_data import reduced_data
from pipeline_gpu import GPU
import warp as wp

def episode(template,groups=3,batch=8,overlap=True,workers=4,frames=10,variant=0,reuse=None):
 start=time.perf_counter();phases={k:0. for k in ['reset','GPU_initial','cut_and_aggregation','GPU_replace','submit','wait_and_observe','checks']};t=time.perf_counter()
 pool=concurrent.futures.ThreadPoolExecutor(max_workers=workers)
 def prepare(j):
  b=template.clone();b.u[:,1]=-(.001+j*.00002)*b.grid[:,1];b.u[:,0]=.0005*b.grid[:,2];a=Aggregate(b);a._prepared_gpu_data=reduced_data(a);return a
 ags=list(pool.map(prepare,range(groups*batch)));phases['reset']=time.perf_counter()-t;gs=[];states=[];m0=[];e0=[];maxmass=maxenergy=0.
 for i in range(groups):
  sub=ags[i*batch:(i+1)*batch];t=time.perf_counter()
  if reuse is not None and i<len(reuse):g=reuse[i];g.replace(sub)
  else:
   g=GPU(sub,capacity_factor=1.75)
   if reuse is not None:reuse.append(g)
  gs.append(g);phases['GPU_initial']+=time.perf_counter()-t
  m0.append([a.body.mass.sum() for a in sub]);e0.append([a.body.metrics()['U'] for a in sub]);states.append([])
 pointers=[g.q.ptr for g in gs];graphs=[id(g.graphs[64]) for g in gs]
 def event(arg):
  j,b,frame=arg;front=[-.25,0,.25,.6][[1,3,5,7].index(frame)]*.06
  normal=[1,.27+j*.013,.13-j*.007] if variant==0 else [1,.33+j*.011,.09-j*.005]
  offset=.001+j*.00005 if variant==0 else .0007+j*.00003
  b=b.clone();b.split(normal,offset,cut_id=0,front=([0,1,0],front));a=Aggregate(b);a._prepared_gpu_data=reduced_data(a);return a
 try:
  if overlap:
   for g in gs:t=time.perf_counter();g.step_async(1600);phases['submit']+=time.perf_counter()-t
  for frame in range(frames):
   for i,g in enumerate(gs):
    if not overlap:t=time.perf_counter();g.step_async(1600);phases['submit']+=time.perf_counter()-t
    t=time.perf_counter();bs=g.finish();states[i].append([b.clone() for b in bs]);phases['wait_and_observe']+=time.perf_counter()-t;t=time.perf_counter()
    for j,b in enumerate(bs):
     m=b.metrics();maxmass=max(maxmass,abs(m['mass']/m0[i][j]-1));maxenergy=max(maxenergy,abs(m['U']+m['T']-e0[i][j])/e0[i][j])
    if maxmass>1e-6 or maxenergy>.05:raise ValueError(('conservation failure',maxmass,maxenergy))
    phases['checks']+=time.perf_counter()-t
    if frame==frames-1:continue
    nextframe=frame+1
    if nextframe in [1,3,5,7]:
     t=time.perf_counter();new=list(pool.map(event,[(i*batch+j,b,nextframe) for j,b in enumerate(bs)]));phases['cut_and_aggregation']+=time.perf_counter()-t;t=time.perf_counter();g.replace(new);phases['GPU_replace']+=time.perf_counter()-t
    if overlap:t=time.perf_counter();g.step_async(1600);phases['submit']+=time.perf_counter()-t
 finally:pool.shutdown()
 wall=time.perf_counter()-start
 result=dict(groups=groups,batch_per_group=batch,workers=workers,variant=variant,overlap=overlap,frames=frames,simulated_s_per_body=frames*.02,wall_s=wall,diagnostic_transitions_s=groups*batch*frames/wall,phases=phases,mass_error_relative=float(maxmass),energy_residual_relative=float(maxenergy),graph_reuse=all(g.q.ptr==p and id(g.graphs[64])==r for g,p,r in zip(gs,pointers,graphs)),gpu_arrays_and_rollback_bytes=sum(g.memory() for g in gs),no_shared_future_cut_path=True,physical_cut=False,RL_qualified=False)
 return states,result

def compare(a,b):
 if not np.array_equal(a.ids,b.ids) or not np.array_equal(a.codes,b.codes):return dict(topology=False),False
 dx=dv=0.
 for p,(x,y) in enumerate(zip(a.polys,b.polys)):
  points=np.concatenate([x,y]);N=np.c_[np.ones(len(points)),points]@a.inv[p];M=np.c_[np.ones(len(points)),points]@b.inv[p]
  dx=max(dx,float(np.max(np.linalg.norm(N@a.u[a.ids[p]]-M@b.u[b.ids[p]],axis=1))));dv=max(dv,float(np.max(np.linalg.norm(N@a.v[a.ids[p]]-M@b.v[b.ids[p]],axis=1))))
 df=float(np.max(abs(a.fields()[2]-b.fields()[2])))
 return dict(topology=True,dx=dx,dv=dv,F=df),dx<=1e-6 and dv<=1e-4 and df<=1e-4

if __name__=='__main__':
 checks={};rows=[];errors=[]
 try:
  assert json.loads((W/'pipeline_validation.json').read_text())['status']=='pass'
  t=time.perf_counter();template=Body(n=10);template.prepare_geometry_cache();Aggregate(template);template_s=time.perf_counter()-t
  # Warm compiled helpers/driver and record this separately from resets/events.
  t=time.perf_counter();episode(template,groups=1,batch=1,frames=2);warm_s=time.perf_counter()-t
  for overlap in [False,True]:
   states,row=episode(template,groups=3,batch=8,overlap=overlap);rows.append(row);print(row,flush=True)
   if not overlap:serial=states
   else:
    for i in range(3):
     for f in [0,1,3,5,7,9]:
      for j in range(8):
       err,ok=compare(serial[i][f][j],states[i][f][j]);checks[f'group{i}_frame{f}_body{j}']=ok;errors.append(err)
  # Timing repeat includes all event work and reset from the pristine template.
  for run in range(2):
   _,row=episode(template,groups=3,batch=8,overlap=True);rows.append(row);print(row,flush=True)
  result=dict(status='pass' if all(checks.values()) else 'failed',checks=checks,rows=rows,errors=errors,template_preparation_s=template_s,initial_warmup_s=warm_s,RL_qualified=False,physical_cut=False)
 except Exception as e:traceback.print_exc();result=dict(status='exception',exception=repr(e),checks=checks,rows=rows,errors=errors)
 (W/'pipeline_loop.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
