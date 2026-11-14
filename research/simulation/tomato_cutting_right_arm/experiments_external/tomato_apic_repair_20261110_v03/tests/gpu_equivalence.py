from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from apic_backend import APICBackend
from apic_reference import APICReference,momentum
from reference import block
X=block(6,.0015);rng=np.random.default_rng(892);results={};checks={};t=time.monotonic()
for name,fixed,codes in [('intact',None,np.zeros(len(X),int)),('partial',None,np.where(X[:,1]>0,np.where(X[:,0]<0,1,2),0)),('supported',np.isclose(X[:,1],X[:,1].min()),np.zeros(len(X),int))]:
 cpu=APICReference(X,fixed=fixed);gpu=APICBackend(X,fixed=fixed,margin=.012);state={'v':rng.normal(size=X.shape)*.001,'C':rng.normal(size=(len(X),3,3))*.01,'F':np.tile(np.diag([1,.999,1]),(len(X),1,1)),'x':X*[1,.999,1],'codes':codes}
 for k,v in state.items():setattr(cpu,k,v.copy())
 gpu.set_state(**state);f=rng.normal(size=X.shape)*.0001
 for j in range(5):cpu.step(1.25e-5,f);gpu.physical_step(1.25e-5,f)
 s=gpu.check();r={k:float(np.max(np.abs(s[k]-getattr(cpu,k)))) for k in ['x','v','C','F']};results[name]=r;checks[name]=r['x']<1e-10 and r['v']<1e-8 and r['C']<1e-6 and r['F']<1e-9
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'wall_s':time.monotonic()-t};(W/'gpu_equivalence.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
