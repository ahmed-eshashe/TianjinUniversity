from pathlib import Path
import sys,json,time,argparse,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
p=argparse.ArgumentParser();p.add_argument('--name',default='task_full_cycle');p.add_argument('--envs',type=int,default=1);p.add_argument('--scale',type=float,default=1.);p.add_argument('--dt',type=float,default=.0001);p.add_argument('--angle',type=float,default=0.);p.add_argument('--offset',type=float,default=.00175);a=p.parse_args();out=W/'runs'/a.name;out.mkdir(exist_ok=False)
E=CuttingEnv(a.envs,scale=a.scale,dt=a.dt,max_steps=5500,offset=a.offset);g=E.g
if a.angle:
 theta=np.deg2rad(a.angle);g.rotation.assign(np.tile([0,np.sin(theta/2),0,np.cos(theta/2)],(a.envs,1)));g.save_initial();E.reset()
axis=np.array([np.sin(np.deg2rad(a.angle)),0,np.cos(np.deg2rad(a.angle))]);phase=np.zeros(a.envs,int);rows=[];start=time.perf_counter();snapshots=[];saved_partial=False
for k in range(5500):
 tool=g.tool.numpy()-g.offset;actions=np.zeros((a.envs,6));saw=np.sin((k-25)*.4)
 for e in range(a.envs):
  if k<25:continue
  if phase[e]==0:
   actions[e,:3]=axis*.15*saw
   if tool[e,1]>.0034:actions[e,1]=-.0015*abs(saw)
   if E.parts[e]>=2 and tool[e,1]<=.0034:phase[e]=1
  if phase[e]==1:actions[e,:3]=axis*.06
 obs,r,t,tr,info=E.step(actions)
 if k%25==0:snapshots.append(g.x.numpy()[:g.n].copy())
 if not saved_partial and info['broken'][0]>500 and E.parts[0]==1 and a.envs==1 and a.scale==1 and a.angle==0:
  np.savez_compressed(W/'runs/task_partial_state.npz',**{key:getattr(g,key).numpy() for key in ['x','v','alive','paid','tool','rotation','ledger','peak','penetration_peak']});saved_partial=True
 if k%100==0 or t.any() or tr.any():
  row={'frame':k,'phase':phase.tolist(),'broken':info['broken'].tolist(),'parts':E.parts.tolist(),'bad':info['bad'].tolist(),'peak':info['peak_force_N'].tolist(),'penetration':info['peak_penetration_m'].tolist(),'clearance':info['clearance_m'].tolist(),'tool':tool.tolist(),'wall_s':time.perf_counter()-start};rows.append(row);print(json.dumps(row),flush=True);(out/'progress.json').write_text(json.dumps(row))
 if t.any() or tr.any():break
wall=time.perf_counter()-start
np.savez_compressed(out/'state.npz',**{key:getattr(g,key).numpy() for key in g.initial},labels=E.labels[0],snapshots=snapshots)
result={'success':info['success'].tolist(),'bad':info['bad'].tolist(),'parts':E.parts.tolist(),'second_mass_fraction':info['second_mass_fraction'].tolist(),'frames':k+1,'wall_s':wall,'complete_task_transitions_s':(k+1)*a.envs/wall,'sim_s':.02*(k+1),'peak_N':g.peak.numpy().tolist(),'penetration_m':g.penetration_peak.numpy().tolist(),'fracture_work_J':info['fracture_work_J'].tolist(),'rows':rows,'config':vars(a)};(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
