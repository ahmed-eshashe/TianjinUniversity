from numerics import *
import argparse, resource, math
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['reference','refined','candidate','candidate_refined','candidate_graph','candidate_gather','candidate_fused'],required=True);args=p.parse_args();mode=args.mode
assert json.loads((W/'controls_result.json').read_text())['passed']
cap={'reference':1.5e-7,'refined':7.5e-8,'candidate':1.5e-5,'candidate_refined':7.5e-6,'candidate_graph':1.5e-5,'candidate_gather':1.5e-5,'candidate_fused':1.5e-5}[mode];interval=.001;sub=math.ceil(interval/cap);h=interval/sub
torch.cuda.reset_peak_memory_stats();t0=time.perf_counter();b=Bulk();b.geometry()
if mode=='candidate_graph':graph=b.capture_implicit(h)
if mode=='candidate_gather':b.enable_gather();graph=b.capture_implicit(h,iterations=64)
if mode=='candidate_fused':b.enable_gather();graph=b.capture_implicit(h,iterations=64,fused=True)
torch.cuda.synchronize();setup=time.perf_counter()-t0
tets=b.z['tet_indices'];fixed=b.z['fixed'];initial=b.z['x'];iv=np.linalg.det(initial[tets[:,1:]]-initial[tets[:,0]][:,None]);rows=[];positions=[];velocities=[];forces=[];reactions=[];output_time=0.;metrics=[];stop='completed';counts=[];residual=0.;start=time.perf_counter()
def sample(k):
    global output_time
    st=time.perf_counter();q,v=b.arrays();mat=b.material().cpu().numpy().copy();ratio=np.linalg.det(q[tets[:,1:]]-q[tets[:,0]][:,None])/iv
    f=b.f.clone()-b.damping(b.v);b.k.ground(b.x,b.v,b.mask,f);reaction=f[torch.as_tensor(fixed,device='cuda')].sum(0).cpu().numpy()
    row={'sample':k,'sim_s':k*interval,'finite':bool(np.isfinite(q).all() and np.isfinite(v).all() and np.isfinite(mat).all()),'min_volume_ratio':float(ratio.min()),'max_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'fixed_error_m':float(np.linalg.norm(q[fixed]-initial[fixed],axis=1).max()),'board_penetration_m':float(max(0,-q[:,1].min())),'force_norm_N':float(np.linalg.norm(mat)),'support_reaction_N':reaction.tolist(),'wall_s':time.perf_counter()-start}
    row['stable']=row['finite'] and row['min_volume_ratio']>.1 and row['fixed_error_m']<=1e-7 and row['board_penetration_m']<=.0001
    rows.append(row);positions.append(q);velocities.append(v);forces.append(mat);reactions.append(reaction);output_time+=time.perf_counter()-st
    (W/f'{mode}_progress.json').write_text(json.dumps(row));return row['stable']
sample(0)
try:
    for k in range(1,21):
        for i in range(sub):
            if mode in ['candidate_graph','candidate_gather','candidate_fused']:graph.replay()
            elif mode.startswith('candidate'):
                mm=b.implicit(h,profile=(i==0));counts.append(mm['iterations']);residual=max(residual,mm['relative_residual'])
                if i==0:metrics.append(mm)
            else:b.explicit(h)
        if mode in ['candidate_graph','candidate_gather','candidate_fused']:
            residual=b.graph_max_residual.item()
            if not np.isfinite(residual) or residual>1e-9:raise RuntimeError(f'Graph PCG residual {residual}')
        if not sample(k):stop='stability_failed';break
except Exception as e:
    stop='exception: '+str(e)
torch.cuda.synchronize();elapsed=time.perf_counter()-start;st=time.perf_counter();np.savez_compressed(W/f'{mode}_trajectory.npz',x=np.array(positions),v=np.array(velocities),f=np.array(forces),reaction=np.array(reactions),t=np.array([r['sim_s'] for r in rows]));output_time+=time.perf_counter()-st
result={'mode':mode,'scope':'20ms intact bulk only; fracture/separation, robot and blade contact not tested','dt_s':h,'steps':(len(rows)-1)*sub,'sim_s':rows[-1]['sim_s'],'setup_wall_s':setup,'total_wall_s':elapsed,'output_wall_s':output_time,'stepping_and_sampling_wall_s_per_sim_s':elapsed/max(rows[-1]['sim_s'],1e-30),'stop':stop,'stable':bool(stop=='completed' and all(a['stable'] for a in rows)),'pcg_max_relative_residual':residual,'pcg_mean_iterations':float(np.mean(counts)) if counts else None,'pcg_max_iterations':max(counts) if counts else None,'profiled_steps':metrics,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'peak_torch_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_torch_reserved_bytes':torch.cuda.max_memory_reserved(),'rows':rows}
(W/f'{mode}_result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['rows','profiled_steps']},indent=2));assert result['stable'],stop
