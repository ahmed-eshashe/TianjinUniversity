from pathlib import Path
import os,sys,json,numpy as np,time,traceback,argparse
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from poly_surface import Surface
from supported_contact_gpu import ContactGPU
from blade_geometry import CAD
from sharp_front import blade_edge
p=argparse.ArgumentParser();p.add_argument('--hierarchical',action='store_true');p.add_argument('--grid-query',action='store_true');p.add_argument('--sparse-contact',action='store_true');p.add_argument('--reduced-quadrature',action='store_true');p.add_argument('--resolution',type=int,default=4);p.add_argument('--dt',type=float,default=None);p.add_argument('--half',action='store_true');p.add_argument('--name',default='tomato_contact');p.add_argument('--frames',type=int,default=52);opt=p.parse_args();
if opt.sparse_contact:
 from sparse_contact_gpu import ContactGPU
 if opt.hierarchical:
  from hierarchical_contact_gpu import ContactGPU
dt=opt.dt if opt.dt else (3.125e-6 if opt.half else 6.25e-6);out=W/'runs'/(opt.name+('_half' if opt.half else ''));out.mkdir(exist_ok=False)
b=Body.restore(Path('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz'));a=Aggregate(b);start=time.perf_counter();
from surface_cache import cached_surface
s=cached_surface(a,W/'states/tomato_surface_cache.npz');build=time.perf_counter()-start;cad=CAD();edge=blade_edge(cad,np.zeros(3),cad.R);T0=np.array([0.,s.X[:,1].max()+.00004,0])-edge.mean(0);travel=np.array([0.,-.00007,0.]);fixed=np.isclose(a.body.grid[a.masters,1],a.body.grid[a.masters,1].min());start=time.perf_counter();g=ContactGPU(a,s,cad,T0,travel,dt=dt,fixed=fixed,capacity=2048,resolution=opt.resolution,candidate_capacity=16384,exact_interior=True,**({'grid_query':opt.grid_query} if opt.sparse_contact else {}),reduced_quadrature=opt.reduced_quadrature);
from convex_guard_gpu import GPUConvexGuard
from compact_proof import CompactProof
g.volume_certificate=CompactProof(a,s,GPUConvexGuard(cad));setup=time.perf_counter()-start;rows=[];states=[];E0=a.metrics()['U']+a.metrics()['T'];status='completed';start=time.perf_counter()
trajectory=np.load(W/'runs/tomato_gpu_proof/trajectory.npz');frame=23
q=trajectory['q'][frame];v=trajectory['v'][frame]
with wp.ScopedStream(g.stream):
 qp=np.zeros((g.ncap,3),np.float32);vp=qp.copy();qp[:g.n]=q;vp[:g.n]=v;g.q.assign(qp);g.vh.assign(vp);g.clock.assign(np.array([.00025*(frame+1)]));g.one()
wp.synchronize_stream(g.stream)
with wp.ScopedTimer('five warm RK4 microsteps',cuda_filter=wp.TIMING_ALL,print=False) as timer:
 with wp.ScopedStream(g.stream):
  for _ in range(5):g.one()
wp.synchronize_stream(g.stream)
items={}
for r in timer.timing_results:
 d=items.setdefault(r.name,dict(count=0,total_ms=0.));d['count']+=1;d['total_ms']+=r.elapsed
report=dict(kernels=sorted([dict(name=k,**v) for k,v in items.items()],key=lambda x:-x['total_ms']),scope='Instrumented, non-graph GPU activity timings on an intact contact state; not environment throughput.');(out/'profile.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
