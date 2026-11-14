from pathlib import Path
import sys,json,numpy as np,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
E=CuttingEnv(1);g=E.g;z=np.load(W/'runs/tomato_slow_saw/state.npz');source=json.loads((W/'runs/tomato_slow_saw/result.json').read_text());g.x.assign(z['x']);g.v.assign(z['v']);g.alive.assign(z['alive']);g.paid.assign(z['paid']);g.tool.assign(z['tool']);g.ledger.assign(np.array([source['rows'][-1]['ledger']],np.float32));g.peak.assign(np.array([source['rows'][-1]['peak']],np.float32));E.prev_paid[:]=z['paid'].sum();rows=[];start=time.perf_counter()
# Horizontal edgewise withdrawal first. Move bodyward only after clearance.
for k in range(180):
 action=[0,0,.06,0,0,0] if g.tool.numpy()[0,2]<.12 else [-.04,0,0,0,0,0]
 obs,r,t,tr,info=E.step(action);rows.append({k1:(v.tolist() if hasattr(v,'tolist') else v) for k1,v in info.items() if k1!='scope'})
 if info['bad'].any():break
 if t.any():break
out={'withdrawal_steps':len(rows),'wall_s':time.perf_counter()-start,'last':rows[-1],'success':bool(info['success'][0]),'pieces':np.bincount(E.labels[0]).tolist(),'mass_kg':float(g.model['mass'].sum()),'fracture_paid_error_relative':float(abs(z['paid'].sum()-80*g.model['fracture_area'][z['alive']==0].sum())/z['paid'].sum())}
# Test pieces are mechanically independent after blade clearance, with the fixture
# released and a small unilateral impulse; no visual displacement is prescribed.
if out['success']:
 g.fixed.zero_();vel=g.v.numpy();labels=E.labels[0].copy();vel[labels==0,0]-=.01;g.v.assign(vel);before=g.x.numpy().copy();other=labels!=0;v0=g.v.numpy()[other,0].mean();g.bad.zero_();g.step([0,0,0],2000);after=g.x.numpy();out['independence']={'other_horizontal_velocity_change':float(g.v.numpy()[other,0].mean()-v0),'piece_relative_COM_change_m':float((after[labels==0]-before[labels==0]).mean(0)[0]-(after[other]-before[other]).mean(0)[0]),'components':g.components()[0],'bad':g.bad.numpy().tolist()}
np.savez_compressed(W/'runs/tomato_withdrawn.npz',x=g.x.numpy(),v=g.v.numpy(),alive=g.alive.numpy(),paid=g.paid.numpy(),tool=g.tool.numpy(),labels=E.labels[0]);(W/'reports/withdrawal.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
