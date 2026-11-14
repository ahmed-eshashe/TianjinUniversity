from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from consistent_backend import ConsistentBackend
from reference import block
R=W/'runs/checkpoint';R.mkdir(exist_ok=False);X=block(8,.0015);a=ConsistentBackend(X);a.initialize(F=np.diag([1,.99,1]));dt=3.90625e-7;a.step(dt,400);a.save(R/'loaded.npz');before=a.check();a.step(dt,400);expected=a.check();b=ConsistentBackend(X)
with np.load(R/'loaded.npz') as z:
 assert np.array_equal(z['X'],b.X) and np.array_equal(z['grid'],b.grid)
 b.initialize(q=z['q'],vg=z['vg']);b.time=float(z['sim_time']);b.steps=int(z['steps'])
b.step(dt,400);actual=b.check();errors={n:float(abs(expected[n]-actual[n]).max()) for n in ['x','v','F','q','vg']};checks={n:e<1e-9 for n,e in errors.items()};checks['same_clock']=abs(b.time-a.time)<1e-15 and b.steps==a.steps
reset=ConsistentBackend(X);reset_state=reset.check();checks['fresh_reset']=float(abs(reset_state['x']-X).max())<1e-14 and abs(reset_state['v']).max()==0 and float(abs(reset_state['F']-np.eye(3)).max())<1e-12
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'differences':errors,'scope':'Intact loaded state q,vg and reference basis, no contacts/cuts. Baseline compression survives checkpoint reconstruction; acceleration recomputed from q.'};(W/'checkpoint_controls.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()));print(json.dumps(out,indent=2,default=lambda x:x.item()))
