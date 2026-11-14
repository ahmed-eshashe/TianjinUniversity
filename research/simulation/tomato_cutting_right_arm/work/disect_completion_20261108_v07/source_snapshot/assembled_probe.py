"""Bounded assembled conditioning diagnostic, not a settling/fracture pass."""
from cohesive_transfer import W
from full_surface import FullSurface
from closure_runtime import Closure
import sys,time,json,numpy as np
from pathlib import Path
sys.path.insert(0,str(W));sys.path.insert(0,str(W/'backend'))
from numerics import load_arrays,tensor,torch
from contact_numerics import ContactBulk
torch.set_num_threads(1);s=FullSurface();closure=Closure(s);m=s.mesh;old=load_arrays();x=m['x'];t=m['tets'];parent=m['parent_tet'];fixed=m['fixed'];mass=m['mass'];inv=1/mass;inv[fixed]=0
z=dict(x=x,tet_indices=t,tet_poses=np.linalg.inv((x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1)),physical_mass=mass,particle_inv_mass=inv,gravity=old['gravity'],contact_mask=np.ones(len(x)),fixed=fixed)
for name in ['tet_mu','tet_lambda','tet_damping','tet_activations']:z[name]=old[name][parent]
class Assembled(ContactBulk):
 def geometry(self):
  f=super().geometry();r=s.evaluate(self.x.cpu().numpy());f.add_(tensor(r['force']+closure.force(self.x.cpu().numpy())));return f
b=Assembled(z);h=.0005/67;rows=[];start=time.perf_counter();stop='bounded_2ms_completed';initial=np.linalg.det(x[t[:,1:]]-x[t[:,0]][:,None])
try:
 for k in range(268):
  info=b.implicit(h);q,v=b.arrays();ratio=np.linalg.det(q[t[:,1:]]-q[t[:,0]][:,None])/initial
  row=dict(step=k+1,volume_ratio_min=float(ratio.min()),speed_max_m_s=float(np.linalg.norm(v,axis=1).max()),**info);rows.append(row)
  if not np.isfinite(q).all() or ratio.min()<=.1:stop='physical_stop';break
  if time.perf_counter()-start>120:stop='wall_cap';break
except Exception as e:stop=repr(e)
out=dict(scope='2-ms conditioning diagnostic with original objective elastic cohesion. Full-surface cohesion and existing cut-face closure active; damage disabled. Not a complete settling qualification.',stop=stop,dt_s=h,wall_s=time.perf_counter()-start,rows=rows)
Path(__file__).with_name('assembled_2ms_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
