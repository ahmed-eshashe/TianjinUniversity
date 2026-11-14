from pathlib import Path
import sys,os,time,json,resource,argparse
import numpy as np
w=Path(__file__).resolve().parent;repo=w/'vendor/roboninja';sys.path.insert(0,str(repo));os.chdir(repo)
p=argparse.ArgumentParser();p.add_argument('--scale',type=float,default=1);p.add_argument('--path',default='straight');args=p.parse_args();label=f'robo_{args.path}_{args.scale:g}'
import taichi as ti
from omegaconf import OmegaConf
from cut_simulation.engine.taichi_env import TaichiEnv
from cut_simulation.configs.macros import MEAT
np.random.seed(42)
start=time.perf_counter();env=TaichiEnv(quality=2,particle_density=8e6,max_steps_local=30,max_steps_global=1801,device_memory_GB=6,horizon=60)
knife=OmegaConf.load(repo/'roboninja/config/cut_env/knife.yaml').knife
env.setup_agent(knife)
# Primitive food block from upstream get_cut_env; no rigid core, renderer or loss.
center=np.array([.5,.1125,.5]);half=np.array([.1,.0875,.075])*args.scale
lower=center-half;upper=center+half;lower[1]=.025;upper[1]=.025+.175*args.scale
env.add_body(type='cube',lower=tuple(lower),upper=tuple(upper),material=MEAT)
env.setup_boundary(type='cube',lower=(.05,.025,.05),upper=(.95,.95,.95));env.build()
env.apply_agent_action_p(np.asarray([0.,float(upper[1]+.015),.5]));ti.sync();setup=time.perf_counter()-start
initial=env.simulator.get_state()['x'];rows=[];stepwall=[];kernelstart=time.perf_counter()
for i in range(60):
 a=np.array([0.,0. if args.path=='straight' else .15*np.sin(i*np.pi/30),0.])
 t=time.perf_counter();env.step(a);ti.sync();stepwall.append(time.perf_counter()-t)
 state=env.simulator.get_state();x=state['x'];v=state['v'];row=dict(step=i+1,sim_s=(i+1)*env.simulator.n_substeps*env.simulator.dt,wall_s=time.perf_counter()-kernelstart,step_wall_s=stepwall[-1],finite=bool(np.isfinite(x).all() and np.isfinite(v).all()),max_speed=float(np.linalg.norm(v,axis=1).max()),bounds=[x.min(0).tolist(),x.max(0).tolist()]);rows.append(row);(w/f'{label}_progress.json').write_text(json.dumps(row,indent=2))
 if not row['finite'] or row['max_speed']>1000:break
 if time.perf_counter()-kernelstart>600:break
knife=env.agent.effectors[0];force=knife.force.to_numpy()[:env.simulator.cur_step_global];work=knife.work.to_numpy()[:env.simulator.cur_step_global]
np.savez(w/f'{label}_final.npz',initial=initial,x=x,v=v,force=force,work=work)
report=dict(scope='RoboNinja original MLS-MPM and knife, upstream block size/density, no rigid core or rendering; forward-only grid gradients not allocated',scale=args.scale,path=args.path,n_particles=env.n_particles,grid=env.simulator.n_grid,grid_dx=env.simulator.dx,dt=env.simulator.dt,setup_wall_s=setup,total_step_wall_s=sum(stepwall),warm_step_wall_s=sum(stepwall[1:]),warm_sim_s=(len(stepwall)-1)*env.simulator.n_substeps*env.simulator.dt,wall_s_per_sim_s=sum(stepwall[1:])/((len(stepwall)-1)*env.simulator.n_substeps*env.simulator.dt),impulse_max=float(force.max()),impulse_mean=float(force.mean()),sum_force_magnitudes_max=float(force.max()/env.simulator.dt),force_semantics='upstream scalar sum of local impulse magnitudes, NOT force in newtons; divide by dt for sum of force magnitudes, not a six-axis resultant',peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,rows=rows)
(w/f'{label}_result.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='rows'},indent=2))
