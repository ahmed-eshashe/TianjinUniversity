"""Finite 50 us contact hold, fresh verified settled state at each timestep.
Not a shallow damage stroke and not a full Gate A/B qualification.
"""
from pathlib import Path
import json,time,sys,numpy as np
from scipy.interpolate import PchipInterpolator
from adaptive_blade import AdaptiveBlade as EdgeBlade,s,m,closure,torch,tensor
from contact_guard import WholeVolumeGuard
from embedded_dashpot import EmbeddedDashpot
W=Path(__file__).resolve().parent

# Independent assembled dense damping reference on an artificial three-node case.
ids=np.array([[0,1],[1,2],[0,0]]);u=np.array([.2,.7,0.])
normal=np.array([[1.,0,0],[0,1.,0],[0,0,1.]])
k=np.array([.3,.4,.8]);tool=np.array([.01,.02,.03])
bd=EmbeddedDashpot(ids,u,normal,k,tool,tensor)
v=np.array([[-.1,-.2,-.3],[-.4,-.5,-.6],[-.7,-.8,-.9]])
B=np.zeros((3,9))
for z in range(3):
 B[z,3*ids[z,0]:3*ids[z,0]+3]+=(1-u[z])*normal[z]
 B[z,3*ids[z,1]:3*ids[z,1]+3]+=u[z]*normal[z]
vn=B@v.ravel()-normal@tool
force_ref=(B.T@(k*np.minimum(vn,0))).reshape(-1,3)
matrix=B.T@np.diag(k*(vn<=0))@B
got=bd.apply(tensor(v)).cpu().numpy()
p=np.arange(9).reshape(3,3)*.01
assert np.max(abs(got-force_ref))<1e-12
assert np.max(abs(bd.hessian(tensor(p),tensor(v)).cpu().numpy().ravel()-matrix@p.ravel()))<1e-12
assert np.max(abs(bd.diagonal(tensor(v)).cpu().numpy().ravel()-np.diag(matrix)))<1e-12
assert np.linalg.eigvalsh(matrix).min()>-1e-12
assert abs(float(bd.energy(tensor(v)))-.5*np.dot(k*np.minimum(vn,0),np.minimum(vn,0)))<1e-12

old=W.parent/'disect_shallow_20261109_v25'
plan=json.loads((old/'correction_plan.json').read_text())
clock=.010;u0=clock/plan['durations_s'][0]
depth=plan['downward_stroke_m']*(10*u0**3-15*u0**4+6*u0**5)
curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T)
placement=json.loads((W/'probe_placement.json').read_text());assert placement['clear_start_passed'] and placement['hold_placement_passed'];T=np.array(placement['loaded_component_hold_translation_m'])
saved=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')
tt=m['tets'];fixed=m['fixed'];fgpu=torch.as_tensor(fixed,device='cuda')
ttg=torch.as_tensor(tt,device='cuda')
iv=torch.linalg.det(tensor(m['x'][tt[:,1:]]-m['x'][tt[:,0]][:,None]))
mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'))
baseT=T.copy()
def pose(t):
 u=min(1.,max(0.,t/50e-6));r=10*u**3-15*u**4+6*u**5;dr=30*u*u-60*u**3+30*u**4
 return baseT+[0,-2e-6*r,0],np.array([0,-2e-6*dr/50e-6,0])
results=[];final=[]
for name,h in [('coarse',3.125e-6),('fine',1.5625e-6)]:
 T,tool_velocity=pose(0.);b=EdgeBlade();b.x.copy_(tensor(saved['x']));b.v.copy_(tensor(saved['v']))
 b.blade_enabled=True;b.blade_translation=T.copy();b.blade_velocity=tool_velocity.copy()
 start=time.perf_counter();rows=[];stop='completed';accepted=0;guard=WholeVolumeGuard(b.cad,tt)
 def record(step,info=None):
  q,v=b.arrays();ev,bd=b.contact(q,v,T,b.blade_velocity)
  force=ev['force'] if bd is None else ev['force']-bd.apply(b.v).cpu().numpy()
  vol=np.linalg.det(q[tt[:,1:]]-q[tt[:,0]][:,None])/iv.cpu().numpy()
  world=q@mapping['rotation'].T+mapping['translation']
  margin=-np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2])
  row=dict(step=step,sim_s=step*h,force_N=float(np.linalg.norm(force.sum(0))),
           sum_force_N=float(np.linalg.norm(force,axis=1).sum()),penetration_m=ev['maximum_penetration_m'],
           energy_J=ev['energy_J'],active_samples=ev['active_samples'],minimum_volume_ratio=float(vol.min()),
           board_penetration_m=float(max(0,-q[:,1].min())),fixed_error_m=float(np.max(abs(q[fixed]-m['x'][fixed]))),
           board_margin_m=float(margin),damage_max=float(b.fracture.history[:,1].max()),
           finite=bool(np.isfinite(q).all() and np.isfinite(v).all()))
  proof=guard.check(q,T,step_motion=2e-6);row['whole_volume_guard']=proof;row['passed']=bool(proof['passed'] and row['finite'] and row['sum_force_N']<=2 and row['penetration_m']<=1e-4 and row['minimum_volume_ratio']>.1 and row['board_penetration_m']<=1e-4 and row['fixed_error_m']<=1e-7 and margin>=.001)
  if info:row['solver']=info
  rows.append(row)
  return row['passed'],force
 valid,_=record(0)
 if not valid:stop='initial_physical_stop'
 else:
  for step in range(round(50e-6/h)):
   T,tool_velocity=pose(step*h);b.blade_translation=T.copy();b.blade_velocity=tool_velocity.copy();prev=b.v.clone();oldq=b.x.clone();b.eligibility_override=None
   for coupling in range(4):
    info=b.implicit(h)
    actual_force=b.blade_sample['force']+b.last_blade_dashpot.cpu().numpy()
    eligible=s.eligibility_from_contact(actual_force)
    if np.array_equal(eligible,b.eligibility):break
    b.x.copy_(oldq);b.v.copy_(prev);b.eligibility_override=eligible
   else:raise RuntimeError('Eligibility fixed point failed')
   total=b.last_force+b.mass*b.gravity
   ledger=(total.sum(0)-total[fgpu].sum(0)-(b.mass*(b.v-prev)/h).sum(0)).norm().item()
   T,tool_velocity=pose((step+1)*h);b.blade_translation=T.copy();b.blade_velocity=tool_velocity.copy();valid,force=record(step+1,info)
   valid=valid and np.linalg.norm(actual_force,axis=1).sum()<=2 and b.blade_sample['maximum_penetration_m']<=.0001
   valid=valid and ledger<=1e-6 and info['relative_residual']<=1e-9 and info['inner_max_residual']<=1e-9 and not int(closure.engine.invalid.numpy()[0])
   if not valid:
    b.x.copy_(oldq);b.v.copy_(prev);stop='physical_trial_rejected_before_history_commit';break
   b.accept_fracture();accepted+=1
 q,v=b.arrays();_,force=record(accepted)
 np.savez_compressed(W/f'moving_probe_{name}_final.npz',x=q,v=v,history=b.fracture.state_dict()['history'],force=force)
 final.append((q.copy(),v.copy(),force.copy()))
 results.append(dict(name=name,dt_s=h,accepted_steps=accepted,wall_s=time.perf_counter()-start,stop=stop,rows=rows))
 out=dict(scope='50 us nonfracturing 2 um moving-blade component test; original settled state, fixed CAD pose, distributed contact candidate',
          damping_dense_reference_passed=True,runs=results,gate_a_complete=False,gate_b_passed=False)
 (W/'moving_probe_result.json').write_text(json.dumps(out,indent=2))
 if stop!='completed':break
if len(final)==2:
 a,b=final
 comparison=dict(position_m=float(np.max(np.linalg.norm(a[0]-b[0],axis=1))),
                 velocity_m_s=float(np.max(np.linalg.norm(a[1]-b[1],axis=1))),
                 force_relative=float(np.linalg.norm(a[2]-b[2])/max(np.linalg.norm(b[2]),1e-6)))
 comparison['passed']=bool(comparison['position_m']<=1e-4 and comparison['velocity_m_s']<=.005 and comparison['force_relative']<=.05 and all(r['stop']=='completed' for r in results))
 out['comparison']=comparison
 (W/'moving_probe_result.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='runs'},indent=2))
