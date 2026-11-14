from pathlib import Path
import sys,json,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));sys.path.insert(0,str(W/'tests'))
from compiled_body import Body
from fast_aggregation import Aggregate
from pipeline_gpu import GPU,CapacityError
from pipeline_loop import compare
checks={};errors=[]
try:
 b=Body(n=4);b.u[:,1]=-.001*b.grid[:,1];a=Aggregate(b);clone=b.clone();a2=Aggregate(clone)
 checks['immutable_operator_reused']=a.E is a2.E and a.M is a2.M
 checks['geometry_shared_not_state']=b.polys is clone.polys and not np.shares_memory(b.u,clone.u)
 try:clone.polys[0][0,0]+=.1;checks['geometry_write_rejected']=False
 except ValueError:checks['geometry_write_rejected']=True
 clone.u[:]=0.;checks['independent_displacement']=np.max(abs(b.u))>0
 oldids=b.ids.copy();oldcodes=b.codes.copy();clone.split([1,.27,.13],.001,front=([0,1,0],0));a3=Aggregate(clone)
 checks['cut_invalidates_operator']=a3.E is not a2.E
 checks['clone_cut_preserves_source']=np.array_equal(oldids,b.ids) and np.array_equal(oldcodes,b.codes) and not b.history
 alt=Aggregate(clone,support_threshold=1e-12);checks['selector_invalidates_cache']=alt.E is not a3.E
 clone.save(W/'states/partial_checkpoint.npz');restored=Body.restore(W/'states/partial_checkpoint.npz')
 for x in [clone,restored]:x.split([1,.27,.13],.001);x.split([0,1,.2],.003,cut_id=1)
 err,ok=compare(clone,restored);checks['continued_restart']=ok;errors.append({'case':'continued_restart',**err})
 # Two independent streams run at different elapsed times; then one fails.
 x=Body(n=4);x.u[:,1]=-.001*x.grid[:,1];y=Body(n=3);y.u[:,0]=.001*y.grid[:,0]
 g=GPU([Aggregate(x)]);h=GPU([Aggregate(y)]);r=GPU([Aggregate(y)])
 g.step_async(160);h.step_async(80)
 for name,action in [('pending_read',lambda:g.state()),('pending_replace',lambda:g.replace([Aggregate(x)])),('pending_step',lambda:g.step_async(80))]:
  try:action();checks[name]=False
  except ValueError:checks[name]=True
 gb=g.finish()[0].clone();hb=h.finish()[0].clone();r.step(80);err,ok=compare(hb,r.export());checks['different_stream_elapsed_time']=ok and abs(gb.time-.002)<1e-14 and abs(hb.time-.001)<1e-14
 vh=g.vh.numpy();vh[:g.n]=1e7*g.aggregates[0].body.grid[g.aggregates[0].masters];g.vh.assign(vh);before_q=g.q.numpy().copy();before_v=g.vh.numpy().copy();oldsteps=g.steps
 g.step_async(64);h.step_async(80)
 try:g.finish();checks['independent_failure_rejected']=False
 except ValueError:checks['independent_failure_rejected']=True
 checks['failed_stream_restored']=g.steps==oldsteps and np.array_equal(before_q,g.q.numpy()) and np.array_equal(before_v,g.vh.numpy())
 hb=h.finish()[0];r.step(80);err,ok=compare(hb,r.export());checks['other_stream_survives_failure']=ok;errors.append({'case':'other_stream_survives_failure',**err})
 result={'status':'pass' if all(checks.values()) else 'failed','checks':{k:bool(v) for k,v in checks.items()},'errors':errors}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'errors':errors}
(W/'invariants.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
