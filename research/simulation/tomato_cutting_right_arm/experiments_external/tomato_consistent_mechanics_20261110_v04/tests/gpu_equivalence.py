from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from consistent_reference import ConsistentReference
from consistent_backend import ConsistentBackend
from reference import block
X=block(8,.0015);rng=np.random.default_rng(42);a=ConsistentReference(X);a.initialize(F=np.diag([1,.99,1]));a.vg=rng.normal(size=a.q.shape)*.001;a.update_state();f=rng.normal(size=X.shape)*1e-5;b=ConsistentBackend(X);b.initialize(q=a.q,vg=a.vg,external=f)
for i in range(10):a.step(12.5e-6,f)
b.step(12.5e-6,10);z=b.check();diff={name:float(abs(getattr(a,name)-z[name]).max()) for name in ['x','v','F','q','vg']};checks={name:err<2e-8 for name,err in diff.items()};out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'differences':diff,'scope':'GPU tensor-product full mass solve against independent CPU sparse full mass solve'};(W/'gpu_equivalence.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
