"""Experimental nonfracturing fixed-packet interval with explicit coverage bound.

No eligibility/history commit and no cutting qualification. The packet comes
from the separately tested ten-micrometre padded material domain. Both target
and authored rigid vertices must remain within five micrometres of its
original geometry throughout the entire short diagnostic. Parent operators
continue to refuse stepping; this new class is isolated to that diagnostic.
"""
import numpy as np
from tomato_cad_pressure import CADPressureCandidate
from tomato_failed_safe_global import FailedSafeFractionCandidate

class BoundedCADInterval(CADPressureCandidate):
 def bind_domain(self,reference_x,vertices,rotation,translation):
  self.domain_x=np.asarray(reference_x,dtype=float).copy();self.domain_vertices=np.asarray(vertices,dtype=float).copy();self.domain_blade=self.domain_vertices@np.asarray(rotation).T+np.asarray(translation);self.domain_bound_m=5e-6;self.external_force=self.pressure.force
 def domain_motion(self,x):
  target=float(np.linalg.norm(x.numpy()-self.domain_x,axis=1).max());R=self.pressure.rotation.numpy()[0];t=self.pressure.translation.numpy()[0];blade=float(np.linalg.norm(self.domain_vertices@R.T+t-self.domain_blade,axis=1).max());return target,blade
 def force(self,x,dt):
  if max(self.domain_motion(x))>self.domain_bound_m:raise ValueError('Actual target/rigid motion exceeds preregistered fixed material coverage bound')
  return super().force(x,dt)
 def energy(self,x,dt,*,trial=False):
  if max(self.domain_motion(x))>self.domain_bound_m:
   if trial:return float('inf')
   raise ValueError('Accepted geometry exceeds fixed material coverage bound')
  return super().energy(x,dt,trial=trial)
 def step(self,state_in,state_out,control,contacts,dt):
  return FailedSafeFractionCandidate.step(self,state_in,state_out,control,contacts,dt)
