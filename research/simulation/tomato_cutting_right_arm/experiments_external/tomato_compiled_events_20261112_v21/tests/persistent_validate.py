from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from compiled_body import Body
from fast_aggregation import Aggregate,vertex_fields
from selective_gpu import GPU as Rebuild,reduced_data as old_data
from fast_data import reduced_data
from persistent_gpu import GPU,CapacityError
rows=[];checks={};start=time.perf_counter()
def compare(a,b):
 if not np.array_equal(a.ids,b.ids) or not np.array_equal(a.codes,b.codes):return {'topology':False},False
 errx=errv=0.
 for i,(p,z) in enumerate(zip(a.polys,b.polys)):
  x=np.concatenate([p,z]);N=np.c_[np.ones(len(x)),x]@a.inv[i];M=np.c_[np.ones(len(x)),x]@b.inv[i]
  errx=max(errx,float(np.max(np.linalg.norm(N@a.u[a.ids[i]]-M@b.u[b.ids[i]],axis=1))))
  errv=max(errv,float(np.max(np.linalg.norm(N@a.v[a.ids[i]]-M@b.v[b.ids[i]],axis=1))))
 F=float(np.max(abs(a.fields()[2]-b.fields()[2])))
 return {'topology':True,'position_m':errx,'velocity_m_s':errv,'F':F},errx<=1e-6 and errv<=1e-4 and F<=1e-4
try:
 # Compiled data layout must equal the previously tested incidence/mass operator.
 for name,normal in [('intact',None),('oblique',[1,.27,.13]),('corner',[1,1,1])]:
  b=Body(n=4);b.u[:,1]=-.001*b.grid[:,1]
  if normal is not None:b.split(normal,1e-6)
  a=Aggregate(b);x=old_data(a);t=time.perf_counter();y=reduced_data(a);cost=time.perf_counter()-t;errors={k:float(np.max(abs(x[k]-y[k]))) if x[k].shape==y[k].shape else float('inf') for k in x}
  checks[name+'_data']=all(v<= (1e-8 if k=='mi' else 1e-10) for k,v in errors.items());rows.append({'case':name+'_data','errors':errors,'compile_or_prepare_s':cost})
  r=Rebuild(Aggregate(b));g=GPU([Aggregate(b)]);trace=[]
  for frame in range(10):
   r.step(80);g.step(80);err,ok=compare(r.export(),g.export());checks[f'{name}_trajectory_{frame}']=ok;trace.append(err)
  rows.append({'case':name+'_trajectory','duration_s':.01,'samples':trace})
 # Independent streams have different topology and loads, no shared future events.
 b0=Body(n=4);b1=Body(n=3);b1.split([1,.2,0],.001);force0=np.zeros_like(b0.u);force0[0]=[.01,0,0];force1=np.zeros_like(b1.u)
 g=GPU([Aggregate(b0),Aggregate(b1)],external=[force0,force1]);g.graph(64);graphid=id(g.graphs[64]);ptrs={k:a.ptr for k,a in g.arrays.items()};g.step(80);bs=[b.clone() for b in g.export_all()];checks['independent_streams']=np.max(abs(bs[1].u))==0 and np.max(abs(bs[0].u))>0
 # Only one stream changes geometry. Other stream fields must retain their state.
 bs[0].split([1,.1,0],.001,front=([0,1,0],0));ags=[Aggregate(b) for b in bs];ff=[np.zeros_like(b.u) for b in bs];g.replace(ags,external=ff)
 checks['storage_graph_reused']=all(a.ptr==ptrs[k] for k,a in g.arrays.items()) and id(g.graphs[64])==graphid
 refs=[Rebuild(Aggregate(b)) for b in bs];g.step(80)
 for j,r in enumerate(refs):r.step(80);err,ok=compare(r.export(),g.export(j));checks[f'changed_stream_{j}']=ok;rows.append({'case':f'changed_stream_{j}',**err})
 # Restart full physical states into a new persistent instance.
 states=[b.clone() for b in g.export_all()]
 for j,b in enumerate(states):b.save(W/'states'/f'persistent_{j}.npz')
 h=GPU([Aggregate(Body.restore(W/'states'/f'persistent_{j}.npz')) for j in range(2)]);g.step(80);h.step(80)
 for j in range(2):err,ok=compare(g.export(j),h.export(j));checks[f'restart_{j}']=ok
 # Capacity and invalid replacement must not mutate any running state.
 before=[b.clone() for b in g.export_all()];ids={k:a.ptr for k,a in g.arrays.items()};oldsteps=g.steps
 try:g.replace([Aggregate(Body(n=10))]);checks['capacity_rejected']=False
 except CapacityError:checks['capacity_rejected']=True
 for j,b in enumerate(before):err,ok=compare(b,g.export(j));checks[f'capacity_preserves_{j}']=ok
 bad=Aggregate(before[0]);bad.q=-2*bad.body.grid[bad.masters];bad.sync()
 try:g.replace([bad]);checks['invalid_replacement_rejected']=False
 except ValueError:checks['invalid_replacement_rejected']=True
 checks['replacement_failure_cursor']=g.steps==oldsteps and all(a.ptr==ids[k] for k,a in g.arrays.items())
 # Deliberately unstable manufactured velocity probes runtime rollback.
 h=GPU([Aggregate(Body(n=2))]);h.graph(64);vh=h.vh.numpy();vh[:h.n]=1e7*h.aggregates[0].body.grid[h.aggregates[0].masters];h.vh.assign(vh);x0=h.q.numpy().copy();v0=h.vh.numpy().copy()
 try:h.step(64);checks['invalid_step_rejected']=False
 except ValueError:checks['invalid_step_rejected']=True
 checks['invalid_step_rollback']=np.array_equal(h.q.numpy(),x0) and np.array_equal(h.vh.numpy(),v0) and h.steps==0
 result={'status':'pass' if all(checks.values()) else 'failed','checks':{k:bool(v) for k,v in checks.items()},'rows':rows,'wall_s':time.perf_counter()-start,'physical_cut':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':{k:bool(v) for k,v in checks.items()},'rows':rows,'wall_s':time.perf_counter()-start}
(W/'persistent_validation.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
