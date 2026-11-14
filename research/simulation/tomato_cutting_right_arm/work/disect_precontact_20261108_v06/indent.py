from pathlib import Path
import sys,json,time,argparse,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'backend'))
from numerics import torch,tensor
from blade_contact import BladeBulk
from board_contact import force as ground_force
p=argparse.ArgumentParser();p.add_argument('--refined',action='store_true');args=p.parse_args();name='indent_refined' if args.refined else 'indent';assert json.loads((W/'settling_qualification.json').read_text())['passed'];plan=json.loads((W/'indent_plan.json').read_text());b=BladeBulk();saved=np.load(W/'settle_contact_final.npz');b.x.copy_(tensor(saved['x']));b.v.copy_(tensor(saved['v']));b.blade_enabled=True;fixed=b.z['fixed'];fgpu=torch.as_tensor(fixed,device='cuda');tt=b.z['tet_indices'];iv=np.linalg.det(b.z['x'][tt[:,1:]]-b.z['x'][tt[:,0]][:,None]);mapping=dict(np.load(W/'board_mapping.npz'));A=tensor(mapping['rotation']);T=tensor(mapping['translation']);H=tensor(mapping['halfspaces']);base=b.mask.clone();initial=np.array(plan['initial_translation_m']);direction=np.array(plan['bodyward_direction_sim']);distance=plan['horizontal_withdrawal_m'];sub=plan['substeps_per_sample']*(2 if args.refined else 1);h=.0005/sub;rows=[];snap=[];start=time.perf_counter();stop='completed';max_residual=0.;max_ledger=0.;qref=b.z['x']
def ramp(s):return 10*s**3-15*s**4+6*s**5,30*s*s-60*s**3+30*s**4
def pose(t):
    if t<=.015:
        u,du=ramp(t/.015);return initial+np.array([0.,-60e-6*u,0.]),np.array([0.,-60e-6*du/.015,0.])
    if t<=.035:
        u,du=ramp((t-.015)/.020);return initial+np.array([0.,-60e-6,0.])+direction*distance*u,direction*distance*du/.020
    return initial+np.array([0.,-60e-6,0.])+direction*distance,np.zeros(3)
def sample(k):
    t=k*.0005;q,v=b.arrays();translation,velocity=pose(t);ev=b.cad.evaluate(q,v,b.surface_ids,translation,velocity);relative=v-velocity;normal=ev['normal'];fd=-ev['kd'][:,None]*np.minimum(np.sum(relative*normal,axis=1),0)[:,None]*normal;force=ev['force']+fd;reaction=-force.sum(0);com=b.cad.com_local@b.cad.rotation.T+translation;moment=-np.cross(q-com,force).sum(0);material=b.material().cpu().numpy().copy();ratio=np.linalg.det(q[tt[:,1:]]-q[tt[:,0]][:,None])/iv;world=q@mapping['rotation'].T+mapping['translation'];margin=-np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2]);row={'sim_s':t,'finite':bool(np.isfinite(q).all() and np.isfinite(v).all() and np.isfinite(force).all()),'reaction_N':reaction.tolist(),'moment_about_blade_COM_Nm':moment.tolist(),'force_norm_N':float(np.linalg.norm(reaction)),'sum_force_magnitudes_N':float(np.linalg.norm(force,axis=1).sum()),'maximum_CAD_penetration_m':ev['maximum_penetration_m'],'active_nodes':int((np.linalg.norm(force,axis=1)>0).sum()),'minimum_volume_ratio':float(ratio.min()),'board_penetration_m':float(max(0,-q[:,1].min())),'fixed_error_m':float(np.max(abs(q[fixed]-qref[fixed]))),'board_edge_margin_m':float(margin),'maximum_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'max_solver_residual':max_residual,'max_discrete_force_balance_error_N':max_ledger,'wall_s':time.perf_counter()-start};row['admissible']=bool(row['finite'] and row['minimum_volume_ratio']>.1 and row['board_penetration_m']<=.0001 and row['fixed_error_m']<=1e-7 and margin>=.001 and row['force_norm_N']<=2 and row['sum_force_magnitudes_N']<=2 and row['maximum_CAD_penetration_m']<=.0001 and max_ledger<=1e-6);rows.append(row);snap.append((q,v,reaction,moment));(W/f'{name}_progress.json').write_text(json.dumps(row,indent=2));return row['admissible']
sample(0)
try:
    for k in range(1,91):
        for j in range(sub):
            time_n=((k-1)*sub+j)*h;b.blade_translation,b.blade_velocity=pose(time_n);world=b.x@A.T+T;b.mask=base*torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1)
            if j==sub-1:previous=b.v.clone()
            info=b.implicit(h);max_residual=max(max_residual,info['relative_residual'],info['inner_max_residual'])
        total=b.last_force+b.mass*b.gravity;support=-total[fgpu].sum(0);momentum=(b.mass*(b.v-previous)/h).sum(0);max_ledger=max(max_ledger,(total.sum(0)+support-momentum).norm().item())
        if not sample(k):stop='physical_stop';break
        if time.perf_counter()-start>600:stop='wall_cap';break
except Exception as e:
    stop='exception: '+str(e);(W/f'{name}_failure_trace.json').write_text(json.dumps(getattr(b,'contact_trace',[]),indent=2))
late=[r for r in rows if r['sim_s']>=.040];loaded=max(r['force_norm_N'] for r in rows)>1e-5;unloaded=bool(len(late)>=11 and max(r['force_norm_N'] for r in late)<=1e-5);passed=bool(stop=='completed' and all(r['admissible'] for r in rows) and rows[0]['force_norm_N']<=1e-10 and loaded and unloaded and max_residual<=1e-9);np.savez_compressed(W/f'{name}_trajectory.npz',t=np.array([r['sim_s'] for r in rows]),x=np.array([r[0] for r in snap]),v=np.array([r[1] for r in snap]),reaction=np.array([r[2] for r in snap]),moment=np.array([r[3] for r in snap]));out={'scope':'Nonfracturing exact-original-CAD prescribed translation on intact corrected FEM; surface-node collocation; no native robot or cut-assembly qualification','force_sample_clock':'Independent contact-law reaction at common sampled q,v,tool pose. Discrete solver force/momentum audited at each sampled final step separately. Not motor effort.','dt_s':h,'duration_s':rows[-1]['sim_s'],'stop':stop,'wall_s':time.perf_counter()-start,'loaded':loaded,'unloaded':unloaded,'component_passed':passed,'fracture_enabled':False,'topology_changed':False,'rows':rows};(W/f'{name}_result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
