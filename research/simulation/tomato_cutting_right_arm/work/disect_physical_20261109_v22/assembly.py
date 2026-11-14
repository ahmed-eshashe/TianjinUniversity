"""Bounded assembled conditioning diagnostic, not a settling/fracture pass."""
from pathlib import Path
import sys
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
sys.path.insert(0,str(W.parent/'disect_completion_20261108_v20'))
from full_surface import FullSurface
from closure_gpu import ClosureGPU
from cohesion_gpu import CohesionGPU
import warp as wp
import sys,time,json,numpy as np
from pathlib import Path
sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06/backend'))
from numerics import load_arrays,tensor,torch
sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'))
from contact_numerics import ContactBulk
torch.set_num_threads(1);s=FullSurface(device="cuda");closure=ClosureGPU(s);cohesion=CohesionGPU(s);m=s.mesh;old=load_arrays();x=m['x'];t=m['tets'];fixed=m['fixed'];mass=m['mass'];inv=1/mass;inv[fixed]=0
z=dict(x=x,tet_indices=t,tet_poses=np.linalg.inv((x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1)),physical_mass=mass,particle_inv_mass=inv,gravity=old['gravity'],contact_mask=np.ones(len(x)),fixed=fixed)
for name in ['tet_mu','tet_lambda','tet_damping','tet_activations']:
 assert np.all(old[name]==old[name][0])
 z[name]=np.full(len(t),old[name][0])
class Assembled(ContactBulk):
 def geometry(self):
  f=super().geometry()
  with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):
   f.add_(cohesion.evaluate(self.x));f.add_(closure.evaluate(self.x))
  return f
