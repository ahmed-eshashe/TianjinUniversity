from pathlib import Path
import sys,os,json,numpy as np,time,collections
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from poly_surface import Surface
from supported_contact_gpu import ContactGPU
from blade_geometry import CAD
from sharp_front import blade_edge
b=Body.restore(W/'states/tomato_baseline.npz');a=Aggregate(b);z=np.load(W/'runs/tomato_contact/trajectory.npz');a.q=z['q'][19];a.v=z['v'][19];a.sync();s=Surface(a);cad=CAD();T=np.array([0.,s.X[:,1].max()+.00004,0])-blade_edge(cad,np.zeros(3),cad.R).mean(0);fixed=np.isclose(b.grid[a.masters,1],b.grid[a.masters,1].min());g=ContactGPU(a,s,cad,T,[0.,-.00007,0.],dt=6.25e-6,fixed=fixed,capacity=2048,candidate_capacity=16384)
with wp.ScopedStream(g.stream):g.clock.assign(np.array([.005]));g.one()
wp.synchronize_stream(g.stream)
with wp.ScopedTimer('four physical microsteps',cuda_filter=wp.TIMING_ALL,print=False) as timer:
 with wp.ScopedStream(g.stream):
  for _ in range(4):g.one()
cost=collections.defaultdict(float);count=collections.Counter()
for r in timer.timing_results:cost[r.name]+=r.elapsed;count[r.name]+=1
rows=[dict(name=k,total_ms=v,calls=count[k],mean_ms=v/count[k]) for k,v in sorted(cost.items(),key=lambda x:-x[1])];out=dict(rows=rows,total_cuda_ms=sum(cost.values()),source='saved 5 ms loaded original tomato',scope='Profiling only; no new physical or RL pass');(W/'reports/tomato_kernel_profile.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
