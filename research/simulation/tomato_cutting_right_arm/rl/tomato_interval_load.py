"""Anchor held-load potential to the previous accepted interval state.

Changing the reference subtracts a constant only; the qualified external
force, Hessian, mechanical acceptance budgets and physical work ledger are
unchanged. The potential is fixed throughout each nonlinear step/retry.
"""
import warp as wp
from tomato_external_load import ExternalLoadCandidate

class IntervalLoadCandidate(ExternalLoadCandidate):
 def step(self,state_in,state_out,control,contacts,dt):
  wp.copy(self.load_reference,state_in.particle_q)
  return super().step(state_in,state_out,control,contacts,dt)
