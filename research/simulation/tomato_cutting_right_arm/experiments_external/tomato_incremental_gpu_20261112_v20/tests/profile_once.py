from pathlib import Path
import sys,json,cProfile,pstats,io,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from aggregation import Aggregate
from selective_gpu import GPU,cache_force,advance_cached
import warp as wp
b=Body(n=10);b.u[:,1]=-.001*b.grid[:,1];b.u[:,0]=.0005*b.grid[:,2]
reports={}
for name,fn in [('geometry',lambda:b.split([1,1,1],1e-6)),('aggregate',lambda:Aggregate(b))]:
 p=cProfile.Profile();p.enable();value=fn();p.disable();s=io.StringIO();pstats.Stats(p,stream=s).sort_stats('cumulative').print_stats(25);(W/'reports'/f'profile_{name}.txt').write_text(s.getvalue());reports[name]=s.getvalue()
g=GPU(Aggregate(b),batch=8);g.graph(64);g.step(1600)
def force():wp.launch(cache_force,g.batch*g.n,inputs=[g.iptr,g.iidx,g.ig,g.P,g.external,g.force],device='cuda:0')
def mass():wp.launch(advance_cached,g.batch*g.n,inputs=[g.mptr,g.midx,g.mi,g.force,g.q,g.vh,0.,0.,g.bad],device='cuda:0')
rows=[]
for name,call in [('stress',g.stress),('gather_force',force),('inverse_mass_advance',mass)]:
 call();wp.synchronize();wp.capture_begin()
 for _ in range(1600):call()
 graph=wp.capture_end();wp.capture_launch(graph);wp.synchronize();times=[]
 for _ in range(3):
  a=wp.Event(enable_timing=True);z=wp.Event(enable_timing=True);wp.record_event(a);wp.capture_launch(graph);wp.record_event(z);wp.synchronize_event(z);times.append(wp.get_event_elapsed_time(a,z))
 rows.append({'kernel':name,'ms_per_1600':times});print(rows[-1],flush=True)
(W/'profile.json').write_text(json.dumps({'batch':8,'regions_per_body':g.p,'reduced_nodes_per_body':g.n,'kernels':rows,'scope':'Static-state repeated kernel graph microtiming; full benchmark measured separately.'},indent=2))
for k,v in reports.items():print(k,v,flush=True)
