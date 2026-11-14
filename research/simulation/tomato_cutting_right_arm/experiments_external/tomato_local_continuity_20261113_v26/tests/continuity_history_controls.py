from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from local_continuity import Aggregate
from fast_aggregation import vertex_fields
rng=np.random.default_rng(7361);direction=np.array([0.,-np.cos(np.pi/6),-np.sin(np.pi/6)]);b=Body(n=2,h=.003);start=float(np.min(b.grid@direction));rows=[]
for k,(normal,offset,cut,front) in enumerate([([1,0,0],.00013,0,(direction,start+.001)),([1,0,0],.00013,0,(direction,start+.003)),([0,0,1],.00021,1,None),([0,1,0],-.00017,2,None)]):
 b.split(normal,offset,cut_id=cut,front=front);before=b.metrics();oldx,oldv=vertex_fields(b);a=Aggregate(b);after=a.metrics();x,v=vertex_fields(a.body);audit=a.audit();pos=float(np.max(abs(x-oldx)));vel=float(np.max(abs(v-oldv)));energy=abs(after['U']+after['T']-before['U']-before['T']);checks={'position':pos<1e-10,'velocity':vel<1e-10,'energy':energy<1e-12,'mass':a.report['mass_relative_error']<1e-12,'elastic_rank':audit['rank']==audit['expected_rank']}
 # Exercise every admissible coordinate before another event; no rest-state reset.
 a.q+=rng.normal(0,2e-7,a.q.shape);a.v+=rng.normal(0,.0002,a.v.shape);a.sync();path=W/'states'/f'history_{k}.npz';a.body.save(path);loaded=Body.restore(path);r=Aggregate(loaded);checks['reload_q']=np.max(abs(r.body.u-a.body.u))<1e-10;checks['reload_v']=np.max(abs(r.body.v-a.body.v))<1e-10;checks['reload_inertia']=np.max(abs(r.M.toarray()-a.M.toarray()))<1e-16;checks['reload_constraints']=r.report['constraint_rank']==a.report['constraint_rank'];row=dict(event=k,checks={key:bool(val) for key,val in checks.items()},mechanics=audit,transfer=a.transfer,continuity=a.report);rows.append(row);print(json.dumps(row),flush=True);assert all(checks.values());b=r.body
out={'passed':all(all(row['checks'].values()) for row in rows),'events':rows,'scope':'Geometry-only repeated-cut and checkpoint preservation; no fracture achievement.'};(W/'reports/continuity_history_controls.json').write_text(json.dumps(out,indent=2))
