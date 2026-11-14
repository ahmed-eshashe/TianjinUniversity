"""Explicit cohesive trials at force clock q_n; commit only after accepted IMEX step.
Exact same reference convention: damage fixed during spatial force derivative.
"""
from pathlib import Path
import sys,numpy as np,warp as wp
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_physical_20261109_v22'))
from assembly import s,z,m,closure
from blade_contact import CADBlade
from blade_numerics import BladeContactBulk
from numerics import Bulk,tensor,torch
sys.path.insert(0,str(W))
from progressive_gpu import ProgressiveGPU
from interface_contact import InterfaceSampling
class DamageBlade(BladeContactBulk):
 def __init__(self):
  super().__init__(z);self.enable_gather();self.fracture=ProgressiveGPU(s);self.sampling=InterfaceSampling(m,s);self.surface_ids=self.sampling.ids;self.cad=CADBlade();self.blade_enabled=False;self.blade_translation=np.zeros(3);self.blade_velocity=np.zeros(3);self.blade_sample=None;self.fracture_trial=None;self.eligibility=np.zeros(47,bool)
 def geometry(self):
  f=Bulk.geometry(self);self.blade_dashpot=None;self.eligibility=np.zeros(47,bool)
  if self.blade_enabled:
   q,v=self.arrays();ev=self.sampling.evaluate(self.cad,q,v,self.blade_translation,self.blade_velocity);self.blade_sample=ev;normal=ev['normal'];fd=-ev['kd'][:,None]*np.minimum(np.sum((v-self.blade_velocity)*normal,axis=1),0)[:,None]*normal
   self.eligibility=s.eligibility_from_contact(ev['force']+fd) if getattr(self,'eligibility_override',None) is None else self.eligibility_override.copy();f.add_(tensor(ev['force']));self.blade_dashpot={'normal':tensor(normal),'velocity':tensor(np.broadcast_to(self.blade_velocity,q.shape).copy()),'kd':tensor(ev['kd'])}
  self.fracture_trial=self.fracture.evaluate(self.x,self.eligibility)
  f.add_(self.fracture_trial['force'])
  with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):f.add_(closure.evaluate(self.x))
  return f
 def material(self):
  # Pure reporting: history fixed, no new eligibility, no overwriting pending trial.
  f=Bulk.geometry(self);trial=self.fracture.evaluate(self.x);f.add_(trial['force'])
  with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):f.add_(closure.evaluate(self.x))
  return f-self.damping(self.v)
 def reset(self):
  super().reset()
  if hasattr(self,'fracture'):self.fracture.reset()
  self.mask.copy_(tensor(self.z['contact_mask']));self.contact_trace=[]
  self.fracture_trial=None;self.blade_sample=None;self.blade_dashpot=None;self.blade_enabled=False;self.eligibility_override=None;self.eligibility=np.zeros(47,bool)
  if hasattr(self,'blade_translation'):self.blade_translation.fill(0);self.blade_velocity.fill(0)
 def accept_fracture(self):self.fracture.commit(self.fracture_trial);self.fracture_trial=None
