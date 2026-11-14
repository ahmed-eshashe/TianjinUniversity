from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from full_surface import FullSurface
from scipy.spatial.transform import Rotation
import torch,warp as wp
from cohesion_gpu import CohesionGPU
wp.init();wp.set_device('cuda:0');torch.set_num_threads(1);s=FullSurface(device='cuda');c=CohesionGPU(s);x=s.mesh['x'];plus=np.unique(s.mesh['tets'][s.mesh['tet_side']>0]);q=x.copy();q[plus]+=[.0002,.00005,.00003];rng=np.random.default_rng(12);q+=rng.normal(size=q.shape)*1e-7;rot=Rotation.from_rotvec([.2,-.3,.1]).as_matrix();rows=[]
for name,p in [('rest',x),('nonuniform',q),('rotated',q@rot.T+[.2,-.3,.1])]:
 ref=s.evaluate(p);f=c.evaluate(torch.tensor(p,device='cuda',dtype=torch.float64)).cpu().numpy().copy();e=c.energy.numpy().sum();err=np.linalg.norm(f-ref['force'])/max(np.linalg.norm(ref['force']),1e-12);rows.append(dict(state=name,force_relative_error=float(err),energy_error_j=float(abs(e-ref['stored_energy_j'])),invalid=int(c.invalid.numpy()[0])))
out=dict(rows=rows,passed=all(r['force_relative_error']<1e-8 and r['energy_error_j']<1e-10 and r['invalid']==0 for r in rows));(W/'cohesion_control.json').write_text(json.dumps(out,indent=2));print(out);assert out['passed']
