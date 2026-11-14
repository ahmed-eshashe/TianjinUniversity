from pathlib import Path
import sys,json,time,math,resource,argparse,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_precontact_20261108_v06'
sys.path.insert(0,str(V));sys.path.insert(0,str(V/'backend'))
from assembly import Assembled,z,cohesion,closure
from numerics import tensor,torch
p=argparse.ArgumentParser();p.add_argument('--refined',action='store_true');args=p.parse_args();args.ground_implicit=True
name='settle_contact_refined' if args.refined else 'settle_contact'
if args.refined:assert json.loads((W/'settle_contact_result.json').read_text())['settling_passed']
mapping=dict(np.load(V/'board_mapping.npz'));hmax=.0000125/(2 if args.refined else 1);sub=math.ceil(.001/hmax);h=.001/sub
torch.cuda.reset_peak_memory_stats();t0=time.perf_counter();b=Assembled(z);b.enable_gather()
fixed=b.z['fixed'];tt=b.z['tet_indices'];q0=b.z['x'];vol0=np.linalg.det(q0[tt[:,1:]]-q0[tt[:,0]][:,None]);original_mask=b.mask.clone();A=tensor(mapping['rotation']);T=tensor(mapping['translation']);H=tensor(mapping['halfspaces']);fixed_gpu=torch.as_tensor(fixed,device='cuda');setup=time.perf_counter()-t0
rows=[];snapshots=[];start=time.perf_counter();stop='duration_completed';max_residual=0.;iterations=[];max_ledger_error=0.
def sample(k,ledger_error=0.):
    q,v=b.arrays();material=b.material().cpu().numpy().copy();from board_contact import force as ground_force
    fg=ground_force(q,v,mapping,b.z['contact_mask']);ratio=np.linalg.det(q[tt[:,1:]]-q[tt[:,0]][:,None])/vol0
    world=q@mapping['rotation'].T+mapping['translation'];margin=-np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2]);fixed_reaction=-(material+fg+b.z['physical_mass'][:,None]*b.z['gravity'])[fixed].sum(0)
    row={'step':k*sub,'sim_s':k*.001,'wall_s':time.perf_counter()-start,'finite':bool(np.isfinite(q).all() and np.isfinite(v).all() and np.isfinite(material).all()),'minimum_volume_ratio':float(ratio.min()),'maximum_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'board_penetration_m':float(max(0,-q[:,1].min())),'fixed_error_m':float(np.linalg.norm(q[fixed]-q0[fixed],axis=1).max()),'board_edge_margin_m':float(margin),'ground_force_N':fg.sum(0).tolist(),'fixed_reaction_N':fixed_reaction.tolist(),'internal_force_resultant_N':material.sum(0).tolist(),'last_step_discrete_force_balance_error_N':float(ledger_error),'max_linear_residual':max_residual}
    row['admissible']=bool(row['finite'] and row['minimum_volume_ratio']>.1 and row['board_penetration_m']<=.0001 and row['fixed_error_m']<=1e-7 and row['board_edge_margin_m']>=.001)
    rows.append(row);tmp=W/f'{name}_progress.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(W/f'{name}_progress.json')
    if k%10==0 or not row['admissible']:snapshots.append({'sim_s':k*.001,'x':q,'v':v,'f':material,'reaction':fixed_reaction})
    if k%100==0 or not row['admissible']:np.savez_compressed(W/f'{name}_checkpoint.npz',x=q,v=v,sim_s=k*.001,initial=q0,tets=tt,fixed=fixed)
    return row['admissible']
sample(0)
try:
    for k in range(1,1001):
        for j in range(sub):
            world=b.x@A.T+T;b.mask=original_mask*torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1)
            if j==sub-1:previous_v=b.v.clone()
            info=b.implicit(h)
            if int(cohesion.invalid.numpy()[0]) or int(closure.engine.invalid.numpy()[0]):raise RuntimeError('Invalid cohesive frame/contact geometry')
            max_residual=max(max_residual,info['relative_residual'],info.get('inner_max_residual',0.));iterations.append(info['iterations'])
        # IMEX force is evaluated at old q, new v. Check that exact discrete
        # force, not a mismatched new-position force, against measured momentum.
        total=(b.last_force if args.ground_implicit else b.f-b.damping(b.v))+b.mass*b.gravity;support=-total[fixed_gpu].sum(0);momentum=(b.mass*(b.v-previous_v)/h).sum(0);ledger_error=(total.sum(0)+support-momentum).norm().item();max_ledger_error=max(max_ledger_error,ledger_error)
        if not sample(k,ledger_error):stop='stability_or_support_gate_failed';break
        if ledger_error>1e-6:stop='discrete_force_balance_failed';break
        if time.perf_counter()-start>(7200 if args.refined else 3600):stop='wall_cap';break
except Exception as e:
    stop='exception: '+str(e)
torch.cuda.synchronize();elapsed=time.perf_counter()-start;late=[r for r in rows if r['sim_s']>=.9];settled=bool(stop=='duration_completed' and len(late)>=101 and max(r['maximum_speed_m_s'] for r in late)<=.001 and all(r['admissible'] for r in rows));q,v=b.arrays();np.savez_compressed(W/f'{name}_final.npz',x=q,v=v,initial=q0,tets=tt,fixed=fixed,sim_s=rows[-1]['sim_s'])
np.savez_compressed(W/f'{name}_trajectory.npz',t=np.array([a['sim_s'] for a in snapshots]),x=np.array([a['x'] for a in snapshots]),v=np.array([a['v'] for a in snapshots]),f=np.array([a['f'] for a in snapshots]),reaction=np.array([a['reaction'] for a in snapshots]))
result={'scope':'Approved v18 split assembly with full-surface moving-frame cohesion and preserved closure proxy; damage disabled; original finite board and supports; speed deferred by user','ground_friction_implicit':args.ground_implicit,'dt_s':h,'substeps_per_ms':sub,'setup_wall_s':setup,'stepping_and_sampling_wall_s':elapsed,'sim_s':rows[-1]['sim_s'],'wall_s_per_sim_s':elapsed/max(rows[-1]['sim_s'],1e-30),'stop':stop,'finite_admissible_hold_completed':bool(stop=='duration_completed' and all(r['admissible'] for r in rows)),'settling_passed':settled,'late_maximum_speed_m_s':max(r['maximum_speed_m_s'] for r in late) if late else None,'max_linear_true_residual':max_residual,'maximum_discrete_force_balance_error_N':max_ledger_error,'mean_cg_iterations':float(np.mean(iterations)) if iterations else 0.,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'peak_torch_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_torch_reserved_bytes':torch.cuda.max_memory_reserved(),'rows':rows}
(W/f'{name}_result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
