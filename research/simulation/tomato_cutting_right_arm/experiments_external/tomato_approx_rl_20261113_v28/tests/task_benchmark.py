from pathlib import Path
import sys,time,json,argparse,subprocess,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
p=argparse.ArgumentParser();p.add_argument('--envs',type=int,default=8);p.add_argument('--steps',type=int,default=250);p.add_argument('--name',required=True);p.add_argument('--loaded',action='store_true');p.add_argument('--dt',type=float,default=.0001);a=p.parse_args();out=W/'runs'/a.name;out.mkdir(exist_ok=False)
start=time.perf_counter();env=CuttingEnv(a.envs,max_steps=100,dt=a.dt);g=env.g;setup=time.perf_counter()-start
# Timing comprises real actions, deformable dynamics, fracture/contact, observation,
# connected components, reward, both termination modes and repeated selective resets.
# Loaded benchmark uses a recorded partial cut, with damage paid by blade motion.
if a.loaded:
 z=np.load(W/'runs/tomato_slow_saw/state.npz');source=json.loads((W/'runs/tomato_slow_saw/result.json').read_text())
 # Prefer actual saved partial state created by full_cycle.py; never invent damage.
 z=np.load(W/'runs/task_partial_state.npz')
 for key in ['x','v','alive','paid','tool','rotation','ledger','peak','penetration_peak']:
  v=z[key]
  if key=='x':v=np.concatenate([v+g.offset[e] for e in range(a.envs)])
  elif key=='tool':v=np.repeat(v,a.envs,axis=0)+g.offset
  elif v.ndim==2 and v.shape[0]==1:v=np.repeat(v,a.envs,axis=0)
  else:v=np.tile(v,(a.envs,1)) if v.ndim==2 else np.tile(v,a.envs)
  getattr(g,key).assign(v)
 g.save_initial();env.reset()
for _ in range(3):env.step([0,0,0,0,0,0])
env.reset();times=[];resets=0;failures=0;success=0;observed_broken=[];start=time.perf_counter()
for k in range(a.steps):
 phase=env.count.astype(float)*.4;saw=.15*np.sin(phase);feed=-.0015*np.abs(np.sin(phase));actions=np.c_[np.zeros(a.envs),feed,saw,np.zeros((a.envs,3))];t0=time.perf_counter();obs,r,term,trunc,info=env.step(actions);ids=np.flatnonzero(term|trunc)
 if len(ids):resets+=len(ids);success+=int(info['success'][ids].sum());failures+=int((info['bad'][ids]!=0).sum());env.reset(ids)
 times.append(time.perf_counter()-t0);observed_broken.append(info['broken'].tolist())
 if k%100==0:print(json.dumps({'step':k,'envs':a.envs,'resets':resets,'steps_s':(k+1)*a.envs/(time.perf_counter()-start)}),flush=True)
wall=time.perf_counter()-start
memory=subprocess.run(['nvidia-smi','--query-compute-apps=used_memory','--format=csv,noheader,nounits'],text=True,capture_output=True).stdout.strip()
result={'envs':a.envs,'steps_per_env':a.steps,'completed_transitions':a.steps*a.envs,'wall_s':wall,'complete_task_transitions_s':a.steps*a.envs/wall,'sim_s_per_env':a.steps*.02,'aggregate_wall_s_per_sim_s':wall/(a.steps*a.envs*.02),'p50_vector_step_s':float(np.median(times)),'p95_vector_step_s':float(np.percentile(times,95)),'resets':resets,'failures':failures,'success':success,'broken_min_max':[int(np.min(observed_broken)),int(np.max(observed_broken))],'setup_graph_compile_s':setup,'gpu_compute_process_memory_MiB':memory,'scope':'Complete approximate kinematic-blade task. Includes live physics, online actions, observation, connectivity, reward, terminal/timeout and reset. Excludes articulated robot, rendering and policy inference. Loaded state from blade-generated partial cut.'};(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
