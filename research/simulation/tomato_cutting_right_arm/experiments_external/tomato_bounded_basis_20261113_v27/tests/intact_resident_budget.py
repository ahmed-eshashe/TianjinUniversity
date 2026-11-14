"""Measured independent-stream material-loop budget; deliberately NOT RL claim."""
from pathlib import Path
import os,sys,json,numpy as np,time,subprocess,hashlib,argparse
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from surface_cache import cached_surface
from hierarchical_contact_gpu import ContactGPU
from convex_guard_gpu import GPUConvexGuard
from compact_proof import CompactProof
from blade_geometry import CAD
from sharp_front import blade_edge
p=argparse.ArgumentParser();p.add_argument('--envs',type=int,default=8);p.add_argument('--frames',type=int,default=52);p.add_argument('--resolution',type=int,default=4);p.add_argument('--tag',default='');p.add_argument('--resident',action='store_true');args=p.parse_args();out=W/'runs'/f'intact_parallel_{args.envs}{args.tag}';out.mkdir(exist_ok=False)
(out/'inputs.json').write_text(json.dumps(dict(options=vars(args),source_sha256={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'src').glob('*.py')},script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2))
b=Body.restore(Path('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz'));cad=CAD();runtimes=[];dt=25e-6;n=10;start=time.perf_counter()
for i in range(args.envs):
 a=Aggregate(b);s=cached_surface(a,W/'states/tomato_surface_cache.npz');edge=blade_edge(cad,np.zeros(3),cad.R);T0=np.array([0.,s.X[:,1].max()+.00004,0])-edge.mean(0);fixed=np.isclose(a.body.grid[a.masters,1],a.body.grid[a.masters,1].min());g=ContactGPU(a,s,cad,T0,np.array([0.,-.00007,0.]),dt=dt,fixed=fixed,capacity=2048,resolution=args.resolution,candidate_capacity=16384,exact_interior=True,grid_query=True);g.volume_certificate=CompactProof(a,s,GPUConvexGuard(cad))
 with wp.ScopedStream(g.stream):g.graph(n)
 if args.resident:
  from resident_clearance import ResidentProof
  g.resident=ResidentProof(g,g.volume_certificate);g.resident.graph(n)
 runtimes.append(g)
wp.synchronize();setup=time.perf_counter()-start;data=[[] for g in runtimes];status='completed';cost=dict(GPU_enqueue_and_wait_s=0.,clearance_s=0.,state_observation_s=0.);start=time.perf_counter()
try:
 if args.resident:
  mark=time.perf_counter()
  for g in runtimes:g.resident.step_async(n*args.frames,block=n)
  for g in runtimes:wp.synchronize_stream(g.stream)
  cost['GPU_enqueue_and_wait_s']+=time.perf_counter()-mark
  for k,g in enumerate(runtimes):
   mark=time.perf_counter();g.finish();obs=g.observe(recompute=False);m=g.aggregates[0].metrics();res=m['U']+m['T']+obs['contact_energy']-obs['tool_work_J']+obs['friction_J'];forces=g.resident.trace.numpy()[:int(g.resident.cursor.numpy()[0])];cost['state_observation_s']+=time.perf_counter()-mark
   for i,force in enumerate(forces):data[k].append(dict(time=(i+1)*n*dt,force=float(force),work=obs['tool_work_J'],friction=obs['friction_J'],energy_residual=res,certificate_passed=True,peak=obs['peak_N']))
   np.savez_compressed(out/f'final_state_{k}.npz',q=g.aggregates[0].q,v=g.aggregates[0].v)
 else:
  for frame in range(args.frames):
   mark=time.perf_counter()
   for g in runtimes:g.step_async(n,block=n)
   for g in runtimes:wp.synchronize_stream(g.stream)
   cost['GPU_enqueue_and_wait_s']+=time.perf_counter()-mark
   for k,g in enumerate(runtimes):
    if g.bad_view[0]:g.finish()
    mark=time.perf_counter();q=g.q_view[:g.n].astype(float);T,_=g.pose((g.steps+n)*dt);motion=(float(g.maxspeed.numpy()[0])+np.linalg.norm(g.travel)*.5*np.pi/g.load)*n*dt;cert=g.volume_certificate(q,T,g.R,motion=motion);cost['clearance_s']+=time.perf_counter()-mark
    if not cert['passed']:g.bad_view[0]=4
    mark=time.perf_counter();g.finish();obs=g.observe(recompute=False);m=g.aggregates[0].metrics();res=m['U']+m['T']+obs['contact_energy']-obs['tool_work_J']+obs['friction_J'];cost['state_observation_s']+=time.perf_counter()-mark
    data[k].append(dict(time=(frame+1)*n*dt,force=obs['sum_force_N'],work=obs['tool_work_J'],friction=obs['friction_J'],energy_residual=res,certificate_passed=cert['passed'],peak=obs['peak_N']))
except Exception as e:status='stopped';(out/'exception.txt').write_text(repr(e))
wall=time.perf_counter()-start;sim=min(map(len,data))*n*dt;reference=json.loads((W/'runs/tomato_hierarchy_dt25_r2/result.json').read_text());force_errors=[];energy=[]
for rows in data:
 force_errors.append(max([abs(a['force']-b['sum_force_N']) for a,b in zip(rows,reference['rows'])]+[0.])/max([abs(x['sum_force_N']) for x in reference['rows']]+[1e-4]));scale=max([abs(x['work']) for x in rows]+[1e-8]);energy.append(max([abs(x['energy_residual']) for x in rows]+[0.])/scale)
checks=dict(complete=status=='completed',energy=max(energy)<.05,reference_force=max(force_errors)<.05,limits=all(r['certificate_passed'] and r['peak']<=2 for rows in data for r in rows));result=dict(status=status,physical_checks_passed=all(checks.values()),checks=checks,environments=args.envs,simulated_s_per_environment=sim,wall_s=wall,setup_and_graph_s=setup,wall_per_simulated_s_per_environment=wall/max(sim,1e-30),equivalent_50Hz_material_transitions_s=args.envs*sim/.02/wall,force_relative_error=max(force_errors),energy_relative=max(energy),cost=cost,memory=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total','--format=csv,noheader'],text=True).strip(),complete_RL_throughput=False,physical_cut=False,rl_ready=False,scope='Independent GPU streams, identical intact tomato approach/hold/retract trajectories. Timed complete material contact/clearance/observation loop; graph build outside timing. NO fracture updates, robot, policy, reward or reset. Equivalent transitions are only a material-loop budget estimate, not measured RL steps.',resident=args.resident,rows=data);(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2));assert all(checks.values())
