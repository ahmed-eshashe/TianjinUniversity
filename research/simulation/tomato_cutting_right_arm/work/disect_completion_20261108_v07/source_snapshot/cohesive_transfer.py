"""Exact barycentric pullback of existing objective reference. Qualification adapter.
No contact eligibility is invented; history commits are explicit after acceptance.
No closure, damping, or dynamics qualification is implied by this component.
"""
from pathlib import Path
import sys,json,numpy as np
ROOT=Path(__file__).resolve().parents[2]
W=ROOT/'work/disect_precontact_20261108_v06'
sys.path.insert(0,str(ROOT/'rl'))
from tomato_objective_cohesion_reference import make_patch
from tomato_failed_cohesion_reference import released_safe_response as response
from tomato_bonds import CohesiveLaw
import torch
class Transfer:
 def __init__(self):
  self.mesh=dict(np.load(W/'conforming_split.npz')); self.mapping=dict(np.load(W/'cohesive_mapping_proposal.npz'))
  self.registry=json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/native_surface_patch_registry_2047fix.json').read_text())
  self.Q=np.array([[1,0,0],[0,0,1],[0,-1,0]],float);self.offset=np.array([0,.002,0]);self.patches=[]
  ref=np.array(self.registry['positions_m'])[np.array(self.registry['pairs'])]
  for p in self.registry['patches']:
   law=CohesiveLaw(**p['law']);ids=np.array(p['pair_indices'])
   self.patches.append((ids,make_patch(ref[ids],p['weights'],p['stiffness_n_m'],[law.onset_m,law.failure_m,law.stiffness_n_m])))
  self.history=np.zeros((len(self.patches),2))
 def evaluate(self,x,eligible=None,history=None):
  if eligible is None:eligible=np.zeros(len(self.patches),bool)
  eligible=np.asarray(eligible)
  if eligible.dtype!=bool or eligible.shape!=(len(self.patches),):raise ValueError('Explicit boolean eligibility per original patch required')
  h=self.history if history is None else np.asarray(history)
  if h.shape!=self.history.shape:raise ValueError('Invalid history dimensions')
  m=self.mapping;w=m['barycentric_weights'];left=m['left_indices'];right=m['right_indices']
  pair=np.stack([np.einsum('ni,nij->nj',w,x[left]),np.einsum('ni,nij->nj',w,x[right])],axis=1)
  original=(pair-self.offset)@self.Q
  force=np.zeros_like(x);trial=h.copy();stored=potential=0.
  with torch.enable_grad():
   for i,(ids,p) in enumerate(self.patches):
    r=response(original[ids],p,history=tuple(h[i]),eligible=bool(eligible[i]));f=r['force_n']@self.Q.T
    for side,nodeids in enumerate([left,right]):
     np.add.at(force,nodeids[ids].ravel(),(w[ids,:,None]*f[:,side,None,:]).reshape(-1,3))
    trial[i]=r['trial_history'];stored+=r['stored_energy_j'];potential+=r['incremental_potential_j']
  return dict(force=force,trial_history=trial,stored_energy_j=stored,incremental_potential_j=potential)
 def commit(self,trial):
  trial=np.asarray(trial)
  if trial.shape!=self.history.shape or not np.isfinite(trial).all() or np.any(trial<self.history-1e-12):raise ValueError('History cannot heal')
  # Reuse reference validation before changing committed state.
  self.evaluate(self.mesh['x'],history=trial)
  self.history=trial.copy()

 def reset(self):
  self.history.fill(0.)
 def tangent_action(self,x,direction,eligible=None):
  if eligible is None:eligible=np.zeros(len(self.patches),bool)
  m=self.mapping;w=m['barycentric_weights'];indices=[m['left_indices'],m['right_indices']]
  pair=np.stack([np.einsum('ni,nij->nj',w,x[ids]) for ids in indices],axis=1)
  dpair=np.stack([np.einsum('ni,nij->nj',w,direction[ids]) for ids in indices],axis=1)@self.Q
  original=(pair-self.offset)@self.Q;out=np.zeros_like(x)
  with torch.enable_grad():
   for i,(ids,p) in enumerate(self.patches):
    r=response(original[ids],p,history=tuple(self.history[i]),eligible=bool(eligible[i]),tangent=True)
    df=(r['force_jacobian_n_m']@dpair[ids].ravel()).reshape(-1,2,3)@self.Q.T
    for side,nodeids in enumerate(indices):
     np.add.at(out,nodeids[ids].ravel(),(w[ids,:,None]*df[:,side,None,:]).reshape(-1,3))
  return out
