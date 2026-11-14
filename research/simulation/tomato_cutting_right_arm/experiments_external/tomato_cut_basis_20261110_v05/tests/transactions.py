from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from cut_reference import CutReference,RejectedEvent
from reference import block
X=block(8,.0015);b=CutReference(X);b.commit(b.propose([0,.006,-.006,.006]));b.q[b.base_ng:,0]=1e-6;b.update_state();b.vg[:,1]=np.r_[np.ones(b.base_ng)*.002,np.zeros(len(b.keys))];b.update_state();before=b.fingerprint();checks={};p=b.propose([-.006,.006,-.006,.006]);b.step(3.90625e-7)
try:b.commit(p);checks['stale_rejected']=False
except RejectedEvent:checks['stale_rejected']=len(b.keys)==24
old=b.fingerprint()
try:b.propose([-.006,.006,-.006,.006],plane=.003);checks['capacity_rejected']=False
except RejectedEvent:checks['capacity_rejected']=b.fingerprint()==old
b.commit(b.propose([-.006,.006,-.006,.006]));b.save(W/'runs/transaction_checkpoint.npz');base_q=b.q.copy();base_v=b.vg.copy();saved_time=b.time;saved_steps=b.steps
for i in range(80):b.step(3.90625e-7)
c=CutReference(X);c.commit(c.propose([-.006,.006,-.006,.006]))
with np.load(W/'runs/transaction_checkpoint.npz') as z:
 assert np.array_equal(c.X,z['X']) and np.array_equal(np.asarray(c.keys),z['keys']);c.q=z['q'].copy();c.vg=z['vg'].copy();c.time=float(z['time']);c.steps=int(z['steps']);c.update_state()
for i in range(80):c.step(3.90625e-7)
errors={n:float(abs(getattr(b,n)-getattr(c,n)).max()) for n in ['x','v','F']};checks['restart']=max(errors.values())<1e-10 and b.steps==c.steps;before=c.fingerprint();checks['reverse_no_heal']=c.propose([0,.006,-.006,.006])['noop'] and c.fingerprint()==before and len(c.keys)==72;fresh=CutReference(X);checks['fresh_reset_intact']=fresh.keys==[] and fresh.plane is None and abs(fresh.x-X).max()<1e-14
result={'status':'pass_restricted_unit_scope' if all(checks.values()) else 'fail','checks':checks,'restart_differences':errors,'scope':'Topology previews, rejection, loaded prescribed-cut checkpoint and fresh reset; no physical fracture ledger.'};(W/'transaction_controls.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item()));print(json.dumps(result,indent=2,default=lambda x:x.item()))
