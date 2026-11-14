from pathlib import Path
import sys,json,time,argparse,os,datetime,resource,numpy as np
W=Path(__file__).resolve().parent
from damage_blade import DamageBlade,s,m,closure,torch,tensor
p=argparse.ArgumentParser();p.add_argument('--refined',action='store_true');args=p.parse_args();name='shallow_refined' if args.refined else 'shallow';plan=json.loads((W/'shallow_plan.json').read_text());assert json.loads((W/'gate_a_result.json').read_text())['passed'];b=DamageBlade();saved=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz');b.x.copy_(tensor(saved['x']));b.v.copy_(tensor(saved['v']));b.blade_enabled=True;initial=np.array(plan['selected']['translation_m']);direction=np.array(plan['bodyward_direction_sim']);h=plan['refined_dt_s'] if args.refined else plan['dt_s'];sample_dt=plan['sample_interval_s'];sub=round(sample_dt/h);n=round(plan['total_s']/sample_dt);tt=m['tets'];ttg=torch.as_tensor(tt,device='cuda');iv=torch.linalg.det(torch.as_tensor((m['x'][tt[:,1:]]-m['x'][tt[:,0]][:,None]),device='cuda'));fixed=m['fixed'];fgpu=torch.as_tensor(fixed,device='cuda');qref=tensor(m['x']);mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'));A=tensor(mapping['rotation']);T=tensor(mapping['translation']);H=tensor(mapping['halfspaces']);base=b.mask.clone();rows=[];snap=[];start=time.perf_counter();max_res=0.;max_ledger=0.;stop='completed';step=0;limits=plan['physical_limits']
def atomic(path,obj):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2));os.replace(tmp,path)
def ramp(u):return 10*u**3-15*u**4+6*u**5,30*u*u-60*u**3+30*u**4
def pose(t):
 load,withdraw,observe=plan['durations_s'];depth=plan['downward_stroke_m']
 if t<=load:
  u,du=ramp(t/load);return initial+[0,-depth*u,0],np.array([0,-depth*du/load,0])
 if t<=load+withdraw:
  u,du=ramp((t-load)/withdraw);return initial+[0,-depth,0]+direction*plan['horizontal_withdrawal_m']*u,direction*plan['horizontal_withdrawal_m']*du/withdraw
 return initial+[0,-depth,0]+direction*plan['horizontal_withdrawal_m'],np.zeros(3)
def checkpoint(label):
 state=b.fracture.state_dict();np.savez_compressed(W/f'{name}_{label}.npz',x=b.x.cpu().numpy(),v=b.v.cpu().numpy(),history=state['history'],step=step,dt=h,blade_translation=b.blade_translation,blade_velocity=b.blade_velocity,eligibility=b.eligibility)
def sample(t):
 q,v=b.arrays();tr,vel=pose(t);ev=b.sampling.evaluate(b.cad,q,v,tr,vel);normal=ev['normal'];fd=-ev['kd'][:,None]*np.minimum(np.sum((v-vel)*normal,axis=1),0)[:,None]*normal;force=ev['force']+fd;reaction=-force.sum(0);com=b.cad.com_local@b.cad.rotation.T+tr;moment=-np.cross(q-com,force).sum(0);hist=b.fracture.state_dict()['history'];qv=q[tt[:,1:]]-q[tt[:,0]][:,None];vol=np.linalg.det(qv)/iv.cpu().numpy();world=q@mapping['rotation'].T+mapping['translation'];margin=-np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2]);diss=b.fracture.dissipation(b.fracture.history[:,0]).sum().item();row=dict(sim_s=t,finite=bool(np.isfinite(q).all() and np.isfinite(v).all()),reaction_N=reaction.tolist(),moment_Nm=moment.tolist(),force_norm_N=float(np.linalg.norm(reaction)),sum_force_N=float(np.linalg.norm(force,axis=1).sum()),CAD_penetration_m=ev['maximum_penetration_m'],active_nodes=ev['active_nodes'],minimum_volume_ratio=float(vol.min()),board_penetration_m=float(max(0,-q[:,1].min())),fixed_error_m=float(np.max(abs(q[fixed]-m['x'][fixed]))),board_edge_margin_m=float(margin),maximum_speed_m_s=float(np.linalg.norm(v,axis=1).max()),damage_max=float(hist[:,1].max()),damaged_groups=int((hist[:,1]>0).sum()),failed_groups=int((hist[:,1]>=1).sum()),maximum_opening_m=float(hist[:,0].max()),fracture_dissipation_J=diss,max_solver_residual=max_res,max_force_balance_N=max_ledger,wall_s=time.perf_counter()-start)
 row['admissible']=bool(row['finite'] and row['minimum_volume_ratio']>.1 and row['board_penetration_m']<=.0001 and row['fixed_error_m']<=1e-7 and margin>=.001 and row['force_norm_N']<=2 and row['sum_force_N']<=2 and row['CAD_penetration_m']<=.0001 and max_res<=1e-9 and max_ledger<=1e-6);rows.append(row);snap.append((q,v,reaction,moment,hist));atomic(W/f'{name}_progress.json',dict(**row,pid=os.getpid(),planned_duration_s=plan['total_s'],running=True,updated=datetime.datetime.now(datetime.timezone.utc).isoformat()));return row['admissible']
sample(0);checkpoint('initial')
try:
 for k in range(1,n+1):
  for j in range(sub):
   step=(k-1)*sub+j;t=step*h;b.blade_translation,b.blade_velocity=pose(t);world=b.x@A.T+T;b.mask=base*torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1);previous=b.v.clone();oldq=b.x.clone();b.eligibility_override=None
   for coupling in range(4):
    info=b.implicit(h);actual_force=b.blade_sample['force']+b.last_blade_dashpot.cpu().numpy();actual_eligible=s.eligibility_from_contact(actual_force)
    if np.array_equal(actual_eligible,b.eligibility):break
    b.x.copy_(oldq);b.v.copy_(previous);b.eligibility_override=actual_eligible
   else:raise RuntimeError('Blade eligibility fixed point failed without history commit')
   max_res=max(max_res,info['relative_residual'],info['inner_max_residual'])
   total=b.last_force+b.mass*b.gravity;support=-total[fgpu].sum(0);mom=(b.mass*(b.v-previous)/h).sum(0);ledger=(total.sum(0)+support-mom).norm().item();max_ledger=max(max_ledger,ledger)
   # Every accepted step checks current volumes, support, finite/board geometry and solver ledger before history commits.
   volume=torch.linalg.det(b.x[ttg[:,1:]]-b.x[ttg[:,0]][:,None])/iv
   valid=bool(torch.isfinite(b.x).all() and torch.isfinite(b.v).all() and volume.min()>.1 and b.x[:,1].min()>=-.0001 and torch.max(abs(b.x[fgpu]-qref[fgpu]))<=1e-7 and max_res<=1e-9 and ledger<=1e-6 and not int(closure.engine.invalid.numpy()[0]))
   ev=b.blade_sample
   if ev is not None:
    actual=tensor(ev['force'])+b.last_blade_dashpot;valid=valid and bool(torch.linalg.vector_norm(actual,dim=1).sum()<=2 and ev['maximum_penetration_m']<=.0001)
   if not valid:
    checkpoint('rejected_trial');b.x.copy_(oldq);b.v.copy_(previous);raise RuntimeError('Physical step rejected before fracture commit')
   b.accept_fracture();step+=1
  if not sample(k*sample_dt):stop='physical_stop';break
  if k%10==0:checkpoint('checkpoint')
  if time.perf_counter()-start>plan['wall_cap_s']:stop='wall_cap';break
except Exception as e:stop='exception: '+str(e)
checkpoint('final');np.savez_compressed(W/f'{name}_trajectory.npz',t=np.array([r['sim_s'] for r in rows]),x=np.array([a[0] for a in snap]),v=np.array([a[1] for a in snap]),reaction=np.array([a[2] for a in snap]),moment=np.array([a[3] for a in snap]),history=np.array([a[4] for a in snap]));out=dict(scope='Damage-enabled prescribed CAD shallow-cut attempt; original law and expanded approved contact sampling; no native robot qualification',stop=stop,dt_s=h,accepted_steps=step,duration_s=step*h,wall_s=time.perf_counter()-start,wall_scope='Stepping and sampling; excludes initialization',peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,peak_torch_allocated_bytes=torch.cuda.max_memory_allocated(),physical_run_completed=bool(stop=='completed' and all(r['admissible'] for r in rows)),nonzero_damage=bool(b.fracture.history[:,1].max()>0),refinement_pending=True,gate_b_passed=False,rows=rows);atomic(W/f'{name}_result.json',out);atomic(W/f'{name}_status.json',dict(running=False,stop=stop,pid=os.getpid(),completed_sim_s=step*h,planned_sim_s=plan['total_s'],updated=datetime.datetime.now(datetime.timezone.utc).isoformat()));atomic(W/f'{name}_progress.json',dict(**rows[-1],running=False,stop=stop,actual_accepted_sim_s=step*h));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
