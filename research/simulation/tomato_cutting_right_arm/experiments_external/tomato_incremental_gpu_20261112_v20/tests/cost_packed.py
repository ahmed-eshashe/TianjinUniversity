"""Synchronized fixed-topology material throughput; never full RL throughput."""
from pathlib import Path
import sys,json,time,gc,subprocess,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from fast_aggregation import Aggregate
from selective_gpu import GPU
import warp as wp
assert json.loads((W/'gpu_validation.json').read_text())['status']=='pass'
assert json.loads((W/'local_validation.json').read_text())['status']=='pass'
rows=[];prep=[];start=time.perf_counter();dt=12.5e-6;nsteps=1600
hardware=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used,temperature.gpu,power.draw','--format=csv,noheader'],text=True).strip()
power={str(p):p.read_text().strip() for p in Path('/sys/class/power_supply').glob('*/online')}
for case,normal,offset in [('intact',None,0),('oblique',[1,.27,.13],.001),('corner',[1,1,1],1e-6)]:
 b=Body(n=10);b.u[:,1]=-.001*b.grid[:,1];b.u[:,0]=.0005*b.grid[:,2];t=time.perf_counter()
 if normal is not None:b.split(normal,offset)
 split_s=time.perf_counter()-t;t=time.perf_counter();a=Aggregate(b,1e-8);aggregate_s=time.perf_counter()-t;m=a.metrics();e0=m['U']+m['T'];prep.append({'case':case,'geometric_cut_CPU_s':split_s,'aggregation_CPU_s':aggregate_s,'regions':len(b.V),'original_nodes':len(b.u),'reduced_nodes':len(a.q),'mass_block_max':a.report['max_mass_block'],'aggregated_nodes':a.report['aggregated_nodes']})
 for batch in [1,8]:
  t=time.perf_counter();g=GPU(Aggregate(b,1e-8),dt,batch=batch);initial=[wp.clone(g.q),wp.clone(g.vh)];g.graph(64);wp.synchronize();setup=time.perf_counter()-t;g.step(nsteps)
  wall=[]
  for repeat in range(3):
   wp.copy(g.q,initial[0]);wp.copy(g.vh,initial[1]);g.steps=0;wp.synchronize();t=time.perf_counter();g.step(nsteps);wp.synchronize();wall.append(time.perf_counter()-t)
  q,v=g.state();gb=g.export();m=gb.metrics();drift=abs(m['U']+m['T']-e0)/max(e0,1e-10);copies=float(max(np.max(abs(q-q[:1])),np.max(abs(v-v[:1]))));row={'case':case,'batch':batch,'dt_s':dt,'duration_per_body_s':nsteps*dt,'wall_repeats_s':wall,'median_wall_s':float(np.median(wall)),'aggregate_50Hz_step_equivalents_s':float(batch/np.median(wall)),'wall_s_per_simulated_s_per_body':float(np.median(wall)/(nsteps*dt)),'array_memory_bytes':g.memory()+sum(x.size*wp.types.type_size_in_bytes(x.dtype) for x in initial),'GPU_setup_and_graph_s':setup,'energy_residual_relative':drift,'identical_batch_difference':copies,'headless':True,'parallel_force':True,'changing_cut_contact_robot_policy_included':False};rows.append(row);print(row,flush=True);(W/'cost_packed.partial.json').write_text(json.dumps({'rows':rows,'preparation':prep,'hardware':hardware,'power':power},indent=2));assert drift<=.05 and copies<=1e-6
  del g,initial;gc.collect();wp.synchronize()
result={'status':'completed_fixed_topology_cost_screen','hardware':hardware,'power':power,'rows':rows,'preparation':prep,'wall_s':time.perf_counter()-start,'RL_qualified':False,'physical_cut':False,'scope':'60 mm cubic material blocks, 6 mm grid, 0.1% compression and 0.05% shear, exact same accepted material/timestep. Geometric cut states only. Timed 20 ms material steps include state backup and validity synchronization. Geometry construction, resets, observations, contact/fracture updates, robot, policy and rendering excluded. Startup and geometric preparation measured separately. Three reset-to-identical-state timing repeats.'}
(W/'cost_packed.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
