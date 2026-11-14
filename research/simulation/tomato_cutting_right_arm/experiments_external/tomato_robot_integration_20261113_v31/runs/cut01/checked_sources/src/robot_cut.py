"""Measured-pose coupling to an explicitly approximate tomato, isolated v31."""
from pathlib import Path
import json,time,numpy as np
from scipy.spatial.transform import Rotation
from frames import pose_matrix,average_wrench,ExchangeClock
W=Path(__file__).resolve().parents[1]
def save(out,name,value):(out/name).write_text(json.dumps(value,indent=2))

def prepare(sim,args,cfg):
 import warp as wp
 wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
 from coupled_environment import CuttingEnv
 E=CuttingEnv(1,dt=.0001,max_steps=20000);appearance=None
 if not args.headless:
  from appearance import Appearance
  appearance=Appearance(sim.stage,E,np.array(cfg['material_to_world_rotation']),np.array(cfg['material_origin_world_m']))
 return E,appearance

def run(sim,r,tool,p,cfg,advance,set_dt,target,closed,right,out,args,capture,app,prepared=None):
 import torch,warp as wp
 wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
 from coupled_environment import CuttingEnv
 E,appearance=prepare(sim,args,cfg) if prepared is None else prepared;g=E.g
 Q=np.array(cfg['material_to_world_rotation']);anchor=np.array(cfg['material_origin_world_m']);L=np.array(cfg['proxy_to_knife_rotation']);C=np.array(cfg['proxy_origin_in_knife_m'])
 stepdt=args.exchange
 if stepdt not in [.002,.001]:raise ValueError('Unreviewed exchange step')
 set_dt(stepdt);clock=ExchangeClock();pending=np.zeros(6);record=[];cut_step=0;start=time.monotonic();last_info=None
 def actual():
  T=pose_matrix(tool.data.root_pose_w.torch[0].cpu().numpy());pos=Q.T@(T[:3,3]+T[:3,:3]@C-anchor);rot=Q.T@T[:3,:3]@L
  comlocal=tool.data.body_com_pose_b.torch[0,0,:3].cpu().numpy();com=T[:3,3]+T[:3,:3]@comlocal
  return T,pos,rot,com
 route_cache={}
 def target_at(route,t,initial=None):
  if id(route) not in route_cache:route_cache[id(route)]=(np.array([x['time'] for x in route]),np.array([x['q']for x in route]))
  times,qs=route_cache[id(route)];idx=np.searchsorted(times,t,side='right');idx=min(max(1,idx),len(route)-1)
  a,b=times[idx-1:idx+1];u=np.clip((t-a)/(b-a),0,1);q=qs[idx-1]*(1-u)+qs[idx]*u;v=(qs[idx]-qs[idx-1])/(b-a)
  full=closed.clone();full[:,right]=torch.tensor(q,dtype=torch.float32);velocity=torch.zeros_like(full);velocity[:,right]=torch.tensor(v,dtype=torch.float32)
  return full,velocity
 def route_run(name,route,coupled=False,limit=None):
  nonlocal pending,cut_step,last_info
  duration=route[-1]['time'] if limit is None else limit;num=round(duration/stepdt);contact_freeze=None;contact_hold_steps=0
  for j in range(num):
   t=(j+1)*stepdt;tar,vel=target_at(route,t if contact_freeze is None else contact_freeze)
   if contact_freeze is not None:vel.zero_();contact_hold_steps+=1
   if coupled:
    assert not tool.instantaneous_wrench_composer.active and not tool.permanent_wrench_composer.active
    if clock.step:
     clock.queue_once(clock.step-1)
     tool.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor(pending[:3][None,None],dtype=torch.float32),torques=torch.tensor(pending[3:][None,None],dtype=torch.float32),positions=None,is_global=True)
    T0,pos0,rot0,com0=actual()
   advance(tar,'research_'+name,vel)
   if coupled:
    assert not tool.instantaneous_wrench_composer.active,'Native force not consumed exactly once'
    T,pos,rot,com=actual();g.tool.assign(pos0[None].astype(np.float32));g.rotation.assign(Rotation.from_matrix(rot0).as_quat()[None].astype(np.float32))
    action=np.r_[(pos-pos0)/stepdt,Rotation.from_matrix(rot@rot0.T).as_rotvec()/stepdt]
    if np.max(np.abs(action[:3]))>.15 or np.max(np.abs(action[3:]))>1.:raise ValueError(('Actual blade velocity out of checked range',action))
    g.linear_impulse.zero_();g.angular_impulse.zero_();g.step(action,round(stepdt/g.base_dt));clock.accept(clock.step,clock.time,stepdt)
    endpoint_error=float(np.linalg.norm(g.tool.numpy()[0]-pos));pending=average_wrench(g.linear_impulse.numpy()[0],g.angular_impulse.numpy()[0],stepdt,Q,anchor,com)
    bad=int(g.bad.numpy()[0]);row=dict(time=clock.time,phase=name,pose=T.tolist(),proxy=pos.tolist(),rotation=rot.tolist(),wrench_generated=pending.tolist(),wrench_applied=record[-1]['wrench_generated'] if record else [0]*6,endpoint_error_m=endpoint_error,peak_N=float(g.peak.numpy()[0]),bad=bad)
    record.append(row);cut_step+=1
    if bad or endpoint_error>1e-6:
     save(out,'coupling_stop.json',row);raise ValueError(('Material/pose stop',row))
    if cut_step%25==0:
     E.count[0]=round(clock.time/.02);_,last_info=E.observe()
     status=dict(phase=name,material_s=clock.time,pieces=int(last_info['parts'][0]),peak_N=float(last_info['peak_force_N'][0]),broken=int(last_info['broken'][0]),bad=bad,wall_s=time.monotonic()-start,pid=__import__('os').getpid())
     save(out,'material_progress.json',status)
     if appearance:appearance.update()
    if args.mode=='contact':
     if contact_freeze is None and float(g.peak.numpy()[0])>=.05:contact_freeze=t
     if contact_hold_steps>=round(.1/stepdt):break
   if appearance and not coupled and j%25==0:appearance.update()
  return tar
 try:
  target=route_run('entry',cfg['entry'])
  if args.mode=='dry':
   target=route_run('dry_cut',cfg['cut']);target=route_run('dry_withdraw',cfg['withdraw']);capture('05_dry_withdraw')
   result={'pass':True,'mode':'dry','full_slice_success':False,'scope':'Native actual tracking and collision checks only; no material feedback.'}
  else:
   T,pos,rot,com=actual();g.tool.assign(pos[None].astype(np.float32));g.rotation.assign(Rotation.from_matrix(rot).as_quat()[None].astype(np.float32));g.save_initial()
   # Settle a fresh state while the measured blade is still clear.
   for _ in range(25):g.step(np.zeros(6),200)
   if g.bad.numpy().any():raise ValueError('Initial material settling stopped')
   np.savez_compressed(out/'material_start.npz',**{k:getattr(g,k).numpy() for k in g.initial})
   if args.mode=='contact':g.cut=0;g.graphs.clear()
   target=route_run('cut',cfg['cut'],True,limit=16.0 if args.mode=='contact' else None)
   _,info=E.observe();save(out,'before_withdraw.json',{k:np.asarray(v).tolist() for k,v in info.items()})
   if args.mode=='contact':
    result={'pass':bool(info['bad'][0]==0 and info['broken'][0]==0 and info['peak_force_N'][0]>.001),'mode':'contact','full_slice_success':False,'peak_N':float(info['peak_force_N'][0]),'maximum_applied_force_N':max(np.linalg.norm(z['wrench_applied'][:3])for z in record),'scope':'Bounded nonfracturing blade contact and native feedback only.'}
   else:
    if not(info['parts'][0]==2 and info['second_mass_fraction'][0]>=.05):raise ValueError(('Cut did not produce two substantial components',info))
    capture('05_separated_before_withdraw',True)
    target=route_run('withdraw',cfg['withdraw'],True)
    hold=[dict(time=0.,q=target[0,right].tolist()),dict(time=1.,q=target[0,right].tolist())];target=route_run('settle',hold,True)
    _,info=E.observe();success=bool(info['parts'][0]==2 and info['second_mass_fraction'][0]>=.05 and info['supported'][0] and info['clearance_m'][0]>.002 and info['bad'][0]==0)
    if appearance:appearance.update()
    capture('06_complete_cut',True)
    result={'pass':success,'mode':'cut','full_slice_success':success,'material_s':clock.time,'peak_N':float(info['peak_force_N'][0]),'parts':int(info['parts'][0]),'second_mass_fraction':float(info['second_mass_fraction'][0]),'clearance_m':float(info['clearance_m'][0]),'supported':bool(info['supported'][0]),'particle_penetration_m':float(info['peak_penetration_m'][0]),'bad':int(info['bad'][0]),'maximum_endpoint_error_m':max(x['endpoint_error_m']for x in record),'maximum_exchanged_force_N':max(np.linalg.norm(x['wrench_generated'][:3])for x in record),'exchange_s':stepdt,'material_dt_s':g.active_dt,'wall_s':time.monotonic()-start,'scope':'Approximate bond-network material, measured native blade poses, one-interval delayed wrench at native COM, fixed grip and bottom fixture; no learned policy or real-tomato calibration.'}
  save(out,'integration_result.json',result);return result
 finally:
  save(out,'coupling_trace.json',record)
  np.savez_compressed(out/'material_final.npz',x=g.x.numpy(),v=g.v.numpy(),alive=g.alive.numpy(),paid=g.paid.numpy(),tool=g.tool.numpy(),rotation=g.rotation.numpy(),ledger=g.ledger.numpy())
