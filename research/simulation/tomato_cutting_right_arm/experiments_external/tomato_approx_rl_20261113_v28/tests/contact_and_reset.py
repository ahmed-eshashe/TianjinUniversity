from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
from solver import Solver
from model import lattice
# Separate fixture: without recontact, disconnected pieces cannot transmit forces.
z=np.load(W/'runs/task_full_cycle/state.npz');labels=z['labels'];results=[]
for impulse in [0.,-.01]:
 g=Solver(lattice('tomato'),recontact=False)
 for key in g.initial:
  if key in z:getattr(g,key).assign(z[key])
 g.fixed.zero_();g.bad.zero_();v=g.v.numpy();v[labels==0,0]+=impulse;g.v.assign(v);g.step([0,0,0],200);results.append((g.x.numpy(),g.bad.numpy()))
other=labels!=0;own=~other;other_error=float(np.max(np.linalg.norm(results[0][0][other]-results[1][0][other],axis=1)));own_error=float(np.mean(np.linalg.norm(results[0][0][own]-results[1][0][own],axis=1)))
E=CuttingEnv(2,shape='cube',max_steps=3);g=E.g
E.step([[0,-.001,.01,0,.1,0],[0,-.001,-.01,0,-.1,0]])
second_before={k:v.numpy()[len(v)//2:].copy() for k,v in [(k,getattr(g,k)) for k in g.initial]};E.reset([0]);reset_exact=all(np.array_equal(getattr(g,k).numpy()[:len(v)//2],v.numpy()[:len(v)//2]) for k,v in g.initial.items());other_preserved=all(np.array_equal(getattr(g,k).numpy()[len(getattr(g,k))//2:],v) for k,v in second_before.items());E.reset();allfinite=True
for k in range(3):obs,r,t,tr,info=E.step([0,0,0,0,0,0]);allfinite&=bool(np.isfinite(obs).all() and np.isfinite(r).all())
timeout=bool(tr.all());E.reset();obs,r,t,tr,info=E.step([np.nan,0,0,0,0,0]);invalid=bool(t.all() and not info['success'].any());E.reset()
# Deliberate overlap of fixed material must stop; not an allowed rollout.
tool=g.tool.numpy();tool[:,1]=g.model['x'][:,1].min();tool[:,0]=g.offset[:,0];g.tool.assign(tool);obs,r,t,tr,info=E.step([0,0,0,0,0,0]);penetration_stop=bool(np.all(info['bad']!=0) and not info['success'].any())
E.reset();tool=g.tool.numpy();tool[:,1]=.00001;tool[:,2]=.2;g.tool.assign(tool);obs,r,t,tr,info=E.step([0,-.01,0,0,0,0]);board_stop=bool(np.all(info['bad']==6) and not info['success'].any())
result={'no_recontact_component_independence':{'other_max_change_m':other_error,'own_mean_change_m':own_error,'bad':[x[1].tolist() for x in results],'pass':bool(other_error<2e-6 and own_error>1e-5 and not any(x[1].any() for x in results))},'blade_board_stop':board_stop,'selective_reset_exact':reset_exact,'other_environment_preserved':other_preserved,'timeout':timeout,'invalid_action_rejected':invalid,'penetration_rejected':penetration_stop,'finite_observations_rewards':allfinite,'note':'Physical recontact can transmit forces between disconnected pieces; that is intentional. The independence fixture disables contact only to isolate cohesive coupling. Production task keeps recontact enabled.'};result['pass']=result['no_recontact_component_independence']['pass'] and all(result[k] for k in ['blade_board_stop','selective_reset_exact','other_environment_preserved','timeout','invalid_action_rejected','penetration_rejected','finite_observations_rewards']);(W/'reports/contact_and_reset.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
