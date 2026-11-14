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
p=argparse.ArgumentParser();p.add_argument('--half',action='store_true');p.add_argument('--name',default='tomato_contact');p.add_argument('--frames',type=int,default=52);opt=p.parse_args();dt=3.125e-6 if opt.half else 6.25e-6;out=W/'runs'/(opt.name+('_half' if opt.half else ''));out.mkdir(exist_ok=False)
b=Body.restore(Path('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz'));a=Aggregate(b);start=time.perf_counter();s=Surface(a);build=time.perf_counter()-start;cad=CAD();edge=blade_edge(cad,np.zeros(3),cad.R);T0=np.array([0.,s.X[:,1].max()+.00004,0])-edge.mean(0);travel=np.array([0.,-.00007,0.]);fixed=np.isclose(a.body.grid[a.masters,1],a.body.grid[a.masters,1].min());start=time.perf_counter();g=ContactGPU(a,s,cad,T0,travel,dt=dt,fixed=fixed,capacity=2048,candidate_capacity=16384,exact_interior=True);setup=time.perf_counter()-start;rows=[];states=[];E0=a.metrics()['U']+a.metrics()['T'];status='completed';start=time.perf_counter()
try:
 for frame in range(opt.frames):
  t0=time.perf_counter();g.checked_step(round(.00025/dt));q,v=g.state();obs=g.observe();m=g.aggregates[0].metrics();res=m['U']+m['T']+obs['contact_energy']-E0-obs['tool_work_J']+obs['friction_J'];row={k:z.tolist() if isinstance(z,np.ndarray) else z for k,z in obs.items()};row.update(energy_residual_J=res,wall_s=time.perf_counter()-t0,profile=g.last_cost,certificate=g.last_certificate,active_domains=int(g.active.numpy()[0]),candidate_domains=int(g.candidate_count.numpy()[0]));rows.append(row);states.append((q.copy(),v.copy()));(out/'progress.json').write_text(json.dumps(row,indent=2))
except Exception as e:status='stopped';traceback.print_exc();(out/'exception.txt').write_text(repr(e));(out/'rejected_certificate.json').write_text(json.dumps(getattr(g,'last_certificate',{}),indent=2))
wall=time.perf_counter()-start;scale=max([abs(r['tool_work_J']) for r in rows]+[1e-8]);energy=max([abs(r['energy_residual_J'])/scale for r in rows]+[0]);checks=dict(complete=status=='completed',energy=energy<=.05,force=all(r['peak_N']<=2 for r in rows),volume=all(r['certificate']['passed'] for r in rows));result=dict(status=status,passed=all(checks.values()),checks=checks,dt=dt,simulated_s=len(rows)*.00025,wall_s=wall,wall_per_simulated_s=wall/max(len(rows)*.00025,1e-12),energy_relative=energy,initial_surface_build_s=build,runtime_setup_s=setup,bulk_regions=len(b.X),mechanical_nodes=g.n,boundary_triangles=g.nfaces,physical_cut=False,rl_ready=False,scope='Original-shape homogeneous tomato, intact supported CAD-contact pilot only. No fracture, robot, board, actions or policy; this is a material/contact cost measurement, not complete RL throughput.',rows=rows);(out/'result.json').write_text(json.dumps(result,indent=2));np.savez_compressed(out/'trajectory.npz',q=[s[0] for s in states],v=[s[1] for s in states]);print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
