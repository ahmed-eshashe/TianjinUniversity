from pathlib import Path
import sys,time,json,argparse,numpy as np,subprocess
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
p=argparse.ArgumentParser();p.add_argument('--envs',type=int,default=8);p.add_argument('--dt',type=float,default=.0002);p.add_argument('--name',default='full_training_benchmark');a=p.parse_args();out=W/'runs'/a.name;out.mkdir(exist_ok=False);E=CuttingEnv(a.envs,dt=a.dt,max_steps=5500);g=E.g;phase=np.zeros(a.envs,int);successes=np.zeros(a.envs,int);failures=np.zeros(a.envs,int);resets=0;history=[];start=time.perf_counter();latency=[];reward_sum=np.zeros(a.envs)
for k in range(6500):
 t0=time.perf_counter();count=E.count.copy();tool=g.tool.numpy()-g.offset;saw=np.sin((count-25)*.4);action=np.zeros((a.envs,6));cut=(count>=25)&(phase==0);action[cut,2]=.15*saw[cut];feed=cut&(tool[:,1]>.0034);action[feed,1]=-.0015*np.abs(saw[feed]);phase[(E.parts>=2)&(tool[:,1]<=.0034)]=1;action[phase==1,:3]=[0,0,.06]
 obs,r,t,tr,info=E.step(action);assert np.isfinite(obs).all() and np.isfinite(r).all();reward_sum+=r;ids=np.flatnonzero(t|tr)
 if len(ids):
  successes[ids]+=info['success'][ids];failures[ids]+=~info['success'][ids];resets+=len(ids);history.append({'step':k,'ids':ids.tolist(),'success':info['success'][ids].tolist(),'bad':info['bad'][ids].tolist(),'peak_force_N':info['peak_force_N'][ids].tolist(),'penetration_m':info['peak_penetration_m'][ids].tolist(),'parts':info['parts'][ids].tolist()});E.reset(ids);phase[ids]=0
 latency.append(time.perf_counter()-t0)
 if k%250==0 or len(ids):
  row={'step':k,'complete_transitions':(k+1)*a.envs,'wall_s':time.perf_counter()-start,'successes':successes.tolist(),'failures':failures.tolist(),'parts':E.parts.tolist()};print(json.dumps(row),flush=True);(out/'progress.json').write_text(json.dumps(row))
 if np.all(successes>=1):break
wall=time.perf_counter()-start;memory=subprocess.run(['nvidia-smi','--query-compute-apps=used_memory','--format=csv,noheader,nounits'],text=True,capture_output=True).stdout.strip();result={'envs':a.envs,'dt':a.dt,'vector_steps':k+1,'completed_transitions':(k+1)*a.envs,'wall_s':wall,'complete_task_transitions_s':(k+1)*a.envs/wall,'successes':successes.tolist(),'failures':failures.tolist(),'resets':resets,'p50_vector_step_s':float(np.median(latency)),'p95_vector_step_s':float(np.percentile(latency,95)),'gpu_compute_memory_MiB':memory,'events':history,'refinements':g.refinements,'pass':bool(np.all(successes>=1) and (k+1)*a.envs/wall>=100),'scope':'Complete approximate kinematic-blade task: from intact body through blade-generated separation, horizontal withdrawal, terminal reward and selective resets. Online scripted controller used instead of a learned policy. Original articulated robot, rendering and policy-network inference excluded. Identical starting cases at different batch offsets, not generalization evidence.'};(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
