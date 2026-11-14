"""Fresh clear-start 2 ms nonfracturing probe, fresh verified settled state at each timestep.
Not a shallow damage stroke and not a full Gate A/B qualification.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_normal_contact_20261109_v30'))
import json,time,sys,numpy as np
from scipy.interpolate import PchipInterpolator
from batched_blade import BatchedBlade as EdgeBlade,s,m,closure,torch,tensor
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_section4_completion_20261109_v29'))
from volume_guard_limit_resolution import WholeVolumeGuard
from embedded_dashpot import EmbeddedDashpot
from volume_certificate import certify
W=Path(__file__).resolve().parent

import argparse,numba,tomato_compiled_blade_query as query_backend
from precision_query import precise_query as fast_query
parser=argparse.ArgumentParser();parser.add_argument('--name',required=True);parser.add_argument('--dt',type=float,required=True);parser.add_argument('--backend',choices=['reference','fast'],required=True);parser.add_argument('--wall-cap',type=float,default=600.);args=parser.parse_args()
assert json.loads((W/'controls_result.json').read_text())['passed']
numba.set_num_threads(4)
if args.backend=='fast':query_backend._query=fast_query

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

assert json.loads((W.parent/'disect_normal_contact_20261109_v30/adapter_controls_result.json').read_text())['passed']
old=W.parent/'disect_shallow_20261109_v25'
plan=json.loads((old/'correction_plan.json').read_text())
clock=.010;u0=clock/plan['durations_s'][0]
depth=plan['downward_stroke_m']*(10*u0**3-15*u0**4+6*u0**5)
curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T)
placement=json.loads((W.parent/'disect_adaptive_contact_20261109_v27/correction_plan.json').read_text());T=np.array(placement['selected']['translation_m'])
saved=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')
tt=m['tets'];fixed=m['fixed'];fgpu=torch.as_tensor(fixed,device='cuda')
ttg=torch.as_tensor(tt,device='cuda')
iv=torch.linalg.det(tensor(m['x'][tt[:,1:]]-m['x'][tt[:,0]][:,None]))
mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'))
baseT=T.copy()
def pose(t):
 u=min(1.,max(0.,t/0.002));r=10*u**3-15*u**4+6*u**5;dr=30*u*u-60*u**3+30*u**4
 return baseT+[0,-42e-6*r,0],np.array([0,-42e-6*dr/0.002,0])
results=[];final=[];frames={}
for name,h in [(args.name,args.dt)]:
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
  step_motion=float(np.max(np.linalg.norm(h*v,axis=1)))+float(np.linalg.norm(pose(step*h)[0]-pose(max(0.,(step-1)*h))[0]));proof=guard.check(q,T,step_motion=step_motion);row['whole_volume_guard']=proof;row['passed']=bool(proof['passed'] and row['finite'] and row['sum_force_N']<=2 and row['penetration_m']<=1e-4 and row['minimum_volume_ratio']>.1 and row['board_penetration_m']<=1e-4 and row['fixed_error_m']<=1e-7 and margin>=.001)
  if info:row['solver']=info
  if step%round(3.125e-6/h)==0:frames[round(step*h,12)]=dict(x=q.copy(),v=v.copy(),force=force.copy(),history=b.fracture.state_dict()['history'])
  rows.append(row)
  return row['passed'],force
 clear=certify(b.x.cpu().numpy(),tt,b.cad.vertices@b.cad.rotation.T+T,b.cad.triangles,limit=-1e-6,max_depth=40)
 assert clear['passed'], 'Clear-start certificate failed'
 valid,_=record(0)
 if not valid:stop='initial_physical_stop'
 else:
  for step in range(round(0.002/h)):
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
    b.x.copy_(oldq);b.v.copy_(prev);T,tool_velocity=pose(accepted*h);b.blade_translation=T.copy();b.blade_velocity=tool_velocity.copy();stop='physical_trial_rejected_before_history_commit';break
   assert float(b.fracture.history[:,1].max())==0., 'Nonfracturing control unexpectedly damaged'
   b.accept_fracture();accepted+=1
   if round(accepted*h,12) in frames:frames[round(accepted*h,12)]['history']=b.fracture.state_dict()['history']
   if step%32==0:
    (W/f'{name}_progress.json').write_text(json.dumps(dict(run=name,backend=args.backend,accepted_steps=accepted,sim_s=accepted*h,planned_s=.002,wall_s=time.perf_counter()-start,running=True)))
    print(json.dumps(dict(run=name,accepted_steps=accepted,sim_s=accepted*h,wall_s=time.perf_counter()-start)),flush=True)
   if time.perf_counter()-start>args.wall_cap:
    stop='wall_cap';break
 q,v=b.arrays();_,force=record(accepted)
 np.savez_compressed(W/f'moving_probe_{name}_final.npz',x=q,v=v,history=b.fracture.state_dict()['history'],force=force)
 final.append((q.copy(),v.copy(),force.copy()))
 results.append(dict(name=name,dt_s=h,accepted_steps=accepted,wall_s=time.perf_counter()-start,stop=stop,rows=rows))
 out=dict(scope='Fresh clear-start 2 ms / 42 um complete-cut-edge candidate probe; same normal/material/fracture laws; backend and timestep identified per case; no Gate B pass',
          damping_dense_reference_passed=True,runs=results,gate_a_complete=False,gate_b_passed=False)
 (W/f'{name}_result.json').write_text(json.dumps(out,indent=2))
 if stop!='completed':break

times=sorted(t for t in frames if t<=accepted*h+1e-12)
np.savez_compressed(W/f'{args.name}_trace.npz',t=np.array(times),**{k:np.array([frames[t][k] for t in times]) for k in ['x','v','force','history']})
(W/f'{args.name}_progress.json').write_text(json.dumps(dict(run=args.name,backend=args.backend,accepted_steps=accepted,sim_s=accepted*h,planned_s=.002,wall_s=time.perf_counter()-start,running=False,stop=stop)))
print(json.dumps(dict(run=args.name,backend=args.backend,stop=stop,accepted_steps=accepted,sim_s=accepted*h,wall_s=time.perf_counter()-start),indent=2))
