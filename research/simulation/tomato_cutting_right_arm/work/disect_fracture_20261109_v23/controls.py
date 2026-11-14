from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1];sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from full_surface import FullSurface
from progressive_gpu import ProgressiveGPU,torch
s=FullSurface();g=ProgressiveGPU(s);x=s.mesh['x'].copy();right=np.unique(s.ri.numpy());left=np.unique(s.li.numpy());start=time.perf_counter();rows=[]
def gpu(q,e):return g.evaluate(torch.as_tensor(q,dtype=torch.float64,device='cuda'),e)
def compare(name,q,e):
 old=g.state_dict()['history'];a=s.evaluate(q,eligible=e,history=old);b=gpu(q,e)
 err=np.linalg.norm(a['force']-b['force'].cpu().numpy());scale=max(np.linalg.norm(a['force']),1e-10);he=np.max(abs(a['trial_history']-b['trial_history'].cpu().numpy()));se=abs(a['stored_energy_j']-b['stored_energy_j'].item());pe=abs(a['incremental_potential_j']-b['incremental_potential_j'].item());pure=np.array_equal(g.state_dict()['history'],old)
 rows.append(dict(name=name,force_relative_or_floor_error=err/scale,history_max_error=he,stored_energy_error_J=se,potential_error_J=pe,trial_pure=pure,passed=bool(err<=1e-10+1e-9*scale and he<=1e-10 and se<=1e-12 and pe<=1e-12 and pure)))
 return b
all_e=np.ones(47,bool);none=np.zeros(47,bool)
for name,jump in [('zero',[0,0,0]),('opening_subonset',[.0005,0,0]),('onset',[.001,0,0]),('onset_minus',[.001-1e-10,0,0]),('onset_plus',[.001+1e-10,0,0]),('opening_softening',[.002,0,0]),('failure_minus',[.004-1e-10,0,0]),('complete_failure',[.004,0,0]),('over_failure',[.006,0,0]),('shear',[0,.002,0]),('mixed',[.0015,.001,-.0007]),('compression',[-.002,0,0])]:
 g.reset();q=x.copy();q[right]+=jump;compare(name,q,all_e);compare(name+'_ineligible',q,none)
# A rigid rotation also exercises moving frame derivatives.
a=.73;rot=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1.]])
g.reset();q=x.copy();q[right]+=[.002,.001,0];compare('rotated_mixed',q@rot.T+[.1,.04,-.03],all_e)
# Explicit history transaction, stale commits, unload/reload, state restore.
g.reset();q=x.copy();q[right]+=[.002,0,0];b=compare('loading',q,all_e);g.commit(b);saved=g.state_dict();b=compare('unload',x,none);g.commit(b);compare('reload_ineligible',q,none);q[right]+=[.001,0,0];compare('reload_eligible',q,all_e)
try:g.commit(b);stale=False
except ValueError:stale=True
old=g.state_dict()['history'];bad={'generation':g.generation,'trial_history':torch.zeros_like(g.history)}
try:g.commit(bad);healing=False
except ValueError:healing=True
q=x.copy();q[right]+=[.0025,0,0];before=g.state_dict();trial=gpu(q,all_e);trial2=gpu(x,none);rollback=np.array_equal(before['history'],g.state_dict()['history'])
g.load_state_dict(saved);restored=gpu(q,all_e);g.load_state_dict(saved);again=gpu(q,all_e);restart=torch.equal(restored['force'],again['force']) or torch.allclose(restored['force'],again['force'],atol=1e-12,rtol=1e-12)
g.reset();reset=np.all(g.state_dict()['history']==0)
# Fully released interface: no frame evaluation, even if all geometry collapses.
g.reset();q=x.copy();q[right]+=[.005,0,0];b=gpu(q,all_e);g.commit(b);released=gpu(np.zeros_like(x),all_e);release_zero=bool(torch.count_nonzero(released['force'])==0 and released['stored_energy_j']==0)
# Analytic group budget and constant jump controls (local energy metric).
g.reset();q=x.copy();q[right]+=[.002,0,0];b=gpu(q,all_e);expected=s.kn.numpy()*.001 # group force for bilinear opening at 2mm = kn*on*(fail-q)/(fail-on)
weights=np.bincount(s.group.numpy(),weights=s.weight.numpy(),minlength=47);budget=.5*s.kn.numpy()*s.on.numpy()*s.fail.numpy();budget_ok=np.isclose(budget.sum(),.11696391110288158,rtol=1e-12,atol=1e-14);weights_ok=np.max(abs(weights-1))<1e-12
# Independent energy derivative at fixed historical damage; eligibility false.
g.commit(b);direction=np.random.default_rng(7).normal(size=x.shape);direction/=np.linalg.norm(direction);eps=1e-8;f=gpu(q,none)['force'].cpu().numpy();plus=gpu(q+eps*direction,none)['stored_energy_j'].item();minus=gpu(q-eps*direction,none)['stored_energy_j'].item();derivative_error=abs((plus-minus)/(2*eps)+np.sum(f*direction));derivative_ok=derivative_error<1e-8
out=dict(scope='Constitutive and transactional controls only; no dynamic cut',rows=rows,stale_commit_rejected=stale,healing_rejected=healing,rejected_trial_preserves_history=rollback,checkpoint_restart_agrees=bool(restart),reset_zero=bool(reset),released_zero_even_collapsed=release_zero,weights_max_error=float(np.max(abs(weights-1))),group_budget_J=budget.tolist(),total_budget_J=float(budget.sum()),fixed_damage_energy_derivative_error_N=float(derivative_error),passed=bool(all(r['passed'] for r in rows) and stale and healing and rollback and restart and reset and release_zero and weights_ok and budget_ok and derivative_ok),wall_s=time.perf_counter()-start)
(W/'controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['rows','group_budget_J']},indent=2));print('failed cases',[r for r in rows if not r['passed']])
