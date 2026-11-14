"""Original CAD nodal contact on approved split exterior; damage disabled."""
from assembly import z,m,cohesion,closure
from blade_contact import CADBlade
from blade_numerics import BladeContactBulk
from numerics import Bulk,tensor,torch
import numpy as np,warp as wp
class AssembledBlade(BladeContactBulk):
 def __init__(self):
  super().__init__(z);self.enable_gather();self.surface_ids=np.unique(m['outer']);self.cad=CADBlade();self.blade_enabled=False;self.blade_translation=np.zeros(3);self.blade_velocity=np.zeros(3);self.blade_sample=None
 def internal_geometry(self):
  f=Bulk.geometry(self)
  with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):
   f.add_(cohesion.evaluate(self.x));f.add_(closure.evaluate(self.x))
  return f
 def geometry(self):
  self.internal_geometry()
  if self.blade_enabled:
   q,v=self.arrays();ev=self.cad.evaluate(q,v,self.surface_ids,self.blade_translation,self.blade_velocity);self.blade_sample=ev;self.f.add_(tensor(ev['force']));self.blade_dashpot={'normal':tensor(ev['normal']),'velocity':tensor(np.broadcast_to(self.blade_velocity,q.shape).copy()),'kd':tensor(ev['kd'])}
  return self.f
 def material(self):return self.internal_geometry()-self.damping(self.v)
 def reset(self):
  super().reset();self.blade_sample=None;self.blade_dashpot=None;self.blade_enabled=False;self.blade_translation[:]=0;self.blade_velocity[:]=0
