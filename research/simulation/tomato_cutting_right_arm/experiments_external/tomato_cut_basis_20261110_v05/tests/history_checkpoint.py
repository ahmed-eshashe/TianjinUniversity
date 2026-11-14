"""Complete state round trip for the restricted cut representation, not a fracture ledger."""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from cut_reference import CutReference
from reference import block
R=W/'runs/history_checkpoint';R.mkdir(exist_ok=False)
X=block(8,.0015);fixed=X[:,1]==X[:,1].min();dt=3.90625e-7
b=CutReference(X,fixed=fixed);force=np.zeros_like(X);force[~fixed,0]=.01/(~fixed).sum()
checks={};records={}
for name,rectangle in [('intact',None),('partial',[0,.006,-.006,.006]),('full',[-.006,.006,-.006,.006])]:
 if rectangle is not None:b.commit(b.propose(rectangle))
 for _ in range(80):b.step(dt,force)
 checkpoint=R/(name+'.npz');b.save(checkpoint);c=CutReference.restore(checkpoint)
 checks[name+'_history']=b.keys==c.keys and b.history==c.history and b.epoch==c.epoch and b.plane==c.plane
 checks[name+'_clock']=b.time==c.time and b.steps==c.steps
 checks[name+'_constraints']=np.array_equal(b.fixed,c.fixed)
 pre={key:float(abs(getattr(b,key)-getattr(c,key)).max()) for key in ['q','vg','x','v','F','support_impulse','support_moment']}
 for _ in range(80):b.step(dt,force);c.step(dt,force)
 post={key:float(abs(getattr(b,key)-getattr(c,key)).max()) for key in pre}
 checks[name+'_continuation']=max(post.values())<1e-10
 records[name]={'before':pre,'after':post,'history_events':len(c.history),'epoch':c.epoch,'support_impulse_norm':float(np.linalg.norm(c.support_impulse))}
checks['nonzero_reaction_restored']=records['full']['support_impulse_norm']>1e-12
with np.load(R/'full.npz',allow_pickle=False) as saved:data={k:saved[k].copy() for k in saved.files}
metadata=json.loads(str(data['metadata']));metadata['history']=metadata['history'][1:];data['metadata']=np.array(json.dumps(metadata));np.savez_compressed(R/'inconsistent_history.npz',**data)
try:CutReference.restore(R/'inconsistent_history.npz');checks['inconsistent_history_rejected']=False
except ValueError:checks['inconsistent_history_rejected']=True
try:CutReference.restore(W/'runs/transaction_checkpoint.npz');checks['legacy_incomplete_rejected']=False
except ValueError:checks['legacy_incomplete_rejected']=True
out={'status':'pass_restricted_unit_scope' if all(checks.values()) else 'fail','checks':checks,'results':records,'scope':'Intact/partial/full single-plane prescribed topology, mechanics, support reactions and event history only. No damage/contact cache or paid fracture exists in this candidate.'}
(W/'history_checkpoint_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2,allow_nan=False))
