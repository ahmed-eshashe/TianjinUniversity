from pathlib import Path
import sys,json,time,numpy as np
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent
from stable_blade import StableBlade,s,m,closure,torch,tensor
sys.path.insert(0,str(W.parent/'disect_section4_completion_20261109_v29'))
from volume_guard_limit_resolution import WholeVolumeGuard
assert json.loads((W/'precision_controls_result.json').read_text())['passed']
V=W.parent/'disect_normal_timestep_20261109_v31'
z=np.load(V/'loading0080_final.npz');t0=float(z['step'])*float(z['dt'])
plan=json.loads((V/'correction_plan.json').read_text());curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T)
def pose(t):
    duration=plan['durations_s'][0];u=t/duration;r=10*u**3-15*u**4+6*u**5;dr=30*u*u-60*u**3+30*u**4
    depth=plan['downward_stroke_m']*r;speed=plan['downward_stroke_m']*dr/duration
    return np.array(plan['selected']['translation_m'])+[float(curve(depth)),-depth,0],np.array([float(curve.derivative()(depth))*speed,-speed,0])
mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'))
tt=m['tets'];iv=np.linalg.det(m['x'][tt[:,1:]]-m['x'][tt[:,0]][:,None]);fixed=m['fixed']
runs=[];states=[]
for name,h,count in [('coarse',6.25e-6,1),('fine',3.125e-6,2)]:
    b=StableBlade();b.debug_line_search=True;b.x.copy_(tensor(z['x']));b.v.copy_(tensor(z['v']))
    b.fracture.load_state_dict({'history':z['history']});b.blade_enabled=True
    hist=b.fracture.state_dict()['history'].copy();guard=WholeVolumeGuard(b.cad,tt);steps=[];start=time.perf_counter()
    for j in range(count):
        t=t0+j*h;b.blade_translation,b.blade_velocity=pose(t)
        oldq=b.x.clone();oldv=b.v.clone();b.eligibility_override=None
        for coupling in range(4):
            info=b.implicit(h)
            actual=b.blade_sample['force']+b.last_blade_dashpot.cpu().numpy()
            eligible=s.eligibility_from_contact(actual)
            if np.array_equal(eligible,b.eligibility):break
            b.x.copy_(oldq);b.v.copy_(oldv);b.eligibility_override=eligible
        else:raise RuntimeError('Eligibility fixed point failed')
        total=b.last_force+b.mass*b.gravity;fg=torch.as_tensor(fixed,device='cuda')
        ledger=(total.sum(0)-total[fg].sum(0)-(b.mass*(b.v-oldv)/h).sum(0)).norm().item()
        q,v=b.arrays();T,_=pose(t+h);motion=float(torch.linalg.vector_norm(b.x-oldq,dim=1).max())+float(np.linalg.norm(T-b.blade_translation));proof=guard.check(q,T,step_motion=motion)
        volume=np.linalg.det(q[tt[:,1:]]-q[tt[:,0]][:,None])/iv
        world=q@mapping['rotation'].T+mapping['translation'];margin=-np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2])
        checks=dict(finite=bool(np.isfinite(q).all() and np.isfinite(v).all()),minimum_volume_ratio=float(volume.min()),board_penetration_m=float(max(0,-q[:,1].min())),fixed_error_m=float(abs(q[fixed]-m['x'][fixed]).max()),board_margin_m=float(margin),force_balance_N=ledger,sum_actual_force_N=float(np.linalg.norm(actual,axis=1).sum()),whole_volume_passed=proof['passed'])
        passed=bool(checks['finite'] and checks['minimum_volume_ratio']>.1 and checks['board_penetration_m']<=1e-4 and checks['fixed_error_m']<=1e-7 and margin>=.001 and ledger<=1e-6 and checks['sum_actual_force_N']<=2 and proof['passed'] and info['relative_residual']<=1e-9 and info['inner_max_residual']<=1e-9 and not int(closure.engine.invalid.numpy()[0]))
        assert passed
        steps.append(dict(sim_s=t+h,solver=info,checks=checks,newton=b.contact_trace,line_search=b.line_search_trace))
        # These isolated numerical trials deliberately do not commit material
        # history. All damage is zero; this is not a physical cutting episode.
        assert np.array_equal(hist,b.fracture.state_dict()['history'])
    T,vel=pose(t0+6.25e-6);ev,bd=b.contact(q,v,T,vel);force=ev['force'] if bd is None else ev['force']-bd.apply(tensor(v)).cpu().numpy()
    com=b.cad.com_local@b.cad.rotation.T+T;reaction=-force.sum(0);moment=-np.cross(q-com,force).sum(0)
    states.append((q.copy(),v.copy(),reaction.copy(),moment.copy(),force.copy()))
    np.savez_compressed(W/f'stable_{name}_uncommitted_trial.npz',x=q,v=v,history=hist,force=force)
    runs.append(dict(name=name,dt_s=h,steps=steps,wall_s=time.perf_counter()-start,fracture_history_unmodified=True))
a,b=states
comparison=dict(position_m=float(np.linalg.norm(a[0]-b[0],axis=1).max()),velocity_m_s=float(np.linalg.norm(a[1]-b[1],axis=1).max()),force_relative=float(np.linalg.norm(a[2]-b[2])/max(np.linalg.norm(b[2]),1e-6)),moment_relative=float(np.linalg.norm(a[3]-b[3])/max(np.linalg.norm(b[3]),1e-8)),nodal_force_relative=float(np.linalg.norm(a[4]-b[4])/max(np.linalg.norm(b[4]),1e-6)))
passed=bool(comparison['position_m']<=1e-4 and comparison['velocity_m_s']<=.005 and comparison['force_relative']<=.05 and comparison['moment_relative']<=.05)
out=dict(scope='One saved-state arithmetic-repair retest: one step versus two half steps, uncommitted history; no trajectory/model/tolerance change and no cutting qualification',source_time_s=t0,comparison=comparison,runs=runs,passed=passed,gate_b_passed=False)
(W/'local_retest_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='runs'},indent=2));assert passed
