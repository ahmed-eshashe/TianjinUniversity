from pathlib import Path
import sys,json,time,math,argparse,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'backend'))
from numerics import torch,tensor
from contact_numerics import ContactBulk
from board_contact import force as ground_force
args=argparse.ArgumentParser();args.add_argument('--refined',action='store_true');a=args.parse_args();name='contact_segment_refined' if a.refined else 'contact_segment';assert json.loads((W/'contact_control_result.json').read_text())['passed'];b=ContactBulk();state=np.load(W/'settle_final.npz');b.x.copy_(tensor(state['x']));b.v.copy_(tensor(state['v']));mapping=dict(np.load(W/'board_mapping.npz'));A=tensor(mapping['rotation']);T=tensor(mapping['translation']);H=tensor(mapping['halfspaces']);base=b.mask.clone();sub=268 if a.refined else 134;h=.001/sub;tets=b.z['tet_indices'];fixed=b.z['fixed'];vol0=np.linalg.det(b.z['x'][tets[:,1:]]-b.z['x'][tets[:,0]][:,None]);rows=[];snap=[];max_res=0.;start=time.perf_counter();stop='completed'
def sample(k):
    q,v=b.arrays();material=b.material().cpu().numpy().copy();fg=ground_force(q,v,mapping,b.z['contact_mask']);reaction=-(material+fg+b.z['physical_mass'][:,None]*b.z['gravity'])[fixed].sum(0);ratio=np.linalg.det(q[tets[:,1:]]-q[tets[:,0]][:,None])/vol0;world=q@mapping['rotation'].T+mapping['translation'];margin=-np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2]);row={'sim_s':k*.001,'maximum_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'min_volume_ratio':float(ratio.min()),'board_penetration_m':float(max(0,-q[:,1].min())),'fixed_error_m':float(np.max(abs(q[fixed]-b.z['x'][fixed]))),'board_margin_m':float(margin),'finite':bool(np.isfinite(q).all() and np.isfinite(v).all()),'max_residual':max_res,'wall_s':time.perf_counter()-start};row['admissible']=bool(row['finite'] and row['min_volume_ratio']>.1 and row['board_penetration_m']<=.0001 and row['fixed_error_m']<1e-7 and margin>.001);rows.append(row);snap.append((q,v,material,reaction));(W/f'{name}_progress.json').write_text(json.dumps(row));return row['admissible']
sample(0)
try:
    for k in range(1,11):
        for j in range(sub):
            world=b.x@A.T+T;b.mask=base*torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1);mm=b.implicit(h);max_res=max(max_res,mm['relative_residual'])
        if not sample(k):stop='admissibility_failed';break
        if time.perf_counter()-start>300:stop='wall_cap';break
except Exception as exc:
    stop='exception: '+str(exc)
    (W/f'{name}_failure_trace.json').write_text(json.dumps(getattr(b,'contact_trace',[]),indent=2))
q,v=b.arrays();np.savez_compressed(W/f'{name}_final.npz',x=q,v=v);np.savez_compressed(W/f'{name}_trajectory.npz',t=np.array([r['sim_s'] for r in rows]),x=np.array([r[0] for r in snap]),v=np.array([r[1] for r in snap]),f=np.array([r[2] for r in snap]),reaction=np.array([r[3] for r in snap]));out={'scope':'10ms continuation from preserved failed-settling state; does not qualify fresh1s settling','stop':stop,'dt_s':h,'wall_s':time.perf_counter()-start,'max_residual':max_res,'admissible':bool(stop=='completed' and all(r['admissible'] for r in rows)),'rows':rows};(W/f'{name}_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
