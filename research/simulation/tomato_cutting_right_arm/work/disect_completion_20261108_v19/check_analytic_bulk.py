from pathlib import Path
import sys,json,time
import numpy as np
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06/backend'))
from numerics import Bulk,load_arrays,tensor,torch
sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from bulk_cache import BulkCache as AD
from analytic_bulk import BulkCache
m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');x=m['x'];t=m['tets'];old=load_arrays();mass=m['mass'];inv=1/mass;inv[m['fixed']]=0
z=dict(x=x,tet_indices=t,tet_poses=np.linalg.inv((x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1)),physical_mass=mass,particle_inv_mass=inv,gravity=old['gravity'],contact_mask=np.ones(len(x)),fixed=m['fixed'])
for key in ['tet_mu','tet_lambda','tet_damping','tet_activations']:z[key]=np.full(len(t),old[key][0])
b=Bulk(z);V=1/(6*torch.linalg.det(b.dm));alpha=1+.75*b.mu/b.la;rows=[]
for name,q in [('rest',tensor(x)),('deformed',tensor(np.load(W/'failure_iterate_00.npz')['q']))]:
 a=AD(b,q,V,alpha);c=BulkCache(b,q,V,alpha);err=(a.h-c.h).norm()/a.h.norm();rows.append(dict(state=name,relative_error=float(err),max_error=float((a.h-c.h).abs().max())))
assert max(r['relative_error'] for r in rows)<1e-10
out=dict(rows=rows,passed=True);(W/'analytic_bulk_control.json').write_text(json.dumps(out,indent=2));print(out)
