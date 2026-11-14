"""Approved full-surface quadrature; original 47 constitutive laws and budgets.
New spatial integration layout, not equivalence to old nonuniform response.
"""
from cohesive_transfer import Transfer
from pathlib import Path
import numpy as np,torch
class FullSurface(Transfer):
 def __init__(self,device='cpu',quadrature='quadrature_proposal.npz'):
  super().__init__();self.device=device;self.quad=dict(np.load(Path(__file__).with_name(quadrature)))
  def T(a,dtype=torch.float64):return torch.as_tensor(np.array(a),dtype=dtype,device=device)
  self.T=T;q=self.quad;copies=dict(self.mesh['ties']);self.li=T(q['faces'],torch.long);self.ri=T([[copies[n] for n in face] for face in q['faces']],torch.long);self.bary=T(q['barycentric']);self.group=T(q['groups'],torch.long);self.weight=T(q['weights'])
  anchors=np.array([ids[list(p['anchors'])] for ids,p in self.patches]);a=self.mapping
  self.ai=T(a['left_indices'][anchors],torch.long);self.bi=T(a['right_indices'][anchors],torch.long);self.aw=T(a['barycentric_weights'][anchors]);self.sign=T([p['sign'] for ids,p in self.patches]);self.K=T([p['local_k'] for ids,p in self.patches]);self.on=T([p['onset'] for ids,p in self.patches]);self.fail=T([p['failure'] for ids,p in self.patches]);self.kn=T([p['kn'] for ids,p in self.patches]);self.Qt=T(self.Q);self.offsett=T(self.offset)
 def energies(self,x,active=None):
  # Transform back to source coordinates to reuse exact original local frames.
  y=(x-self.offsett)@self.Qt
  anchor=.5*((y[self.ai]+y[self.bi])*self.aw[:,:,:,None]).sum(2)
  u=anchor[:,1]-anchor[:,0];v=anchor[:,2]-anchor[:,0];cross=torch.linalg.cross(u,v);ul=torch.linalg.vector_norm(u,dim=1);cl=torch.linalg.vector_norm(cross,dim=1)
  if active is None:active=torch.ones(47,dtype=torch.bool,device=x.device)
  if torch.any(((ul<1e-12)|(cl<1e-12))&active):raise ValueError('Collapsed active material frame')
  t=u/ul.clamp_min(1e-12)[:,None];n=self.sign[:,None]*cross/cl.clamp_min(1e-12)[:,None];b=torch.linalg.cross(n,t);frame=torch.stack([n,t,b],dim=2)
  gap=((y[self.ri]-y[self.li])*self.bary[:,:,None]).sum(1);local=torch.einsum('ni,nij->nj',gap,frame[self.group]);e=torch.cat([local[:,:1].clamp_min(0),local[:,1:]],dim=1)
  values=.5*self.weight*torch.einsum('ni,nij,nj->n',e,self.K[self.group],e)
  return torch.zeros(47,dtype=x.dtype,device=x.device).index_add(0,self.group,values)*active
 def evaluate(self,x,eligible=None,history=None):
  if eligible is None:eligible=np.zeros(47,bool)
  eligible=np.asarray(eligible)
  if eligible.dtype!=bool or eligible.shape!=(47,):raise ValueError('Boolean eligibility required')
  h=self.history if history is None else np.asarray(history)
  if h.shape!=(47,2) or not np.isfinite(h).all() or np.any(h<0) or np.any(h[:,1]>1):raise ValueError('Invalid history')
  # Validate the canonical irreversible law, including reset and external loads.
  onset=self.on.cpu().numpy();failure=self.fail.cpu().numpy();expected=np.where(h[:,0]<=onset,0,np.where(h[:,0]>=failure,1,failure*(h[:,0]-onset)/(np.maximum(h[:,0],1e-300)*(failure-onset))))
  if np.max(abs(expected-h[:,1]))>1e-10:raise ValueError('Noncanonical damage history')
  with torch.enable_grad():
   y=self.T(x).detach().requires_grad_(True);U=self.energies(y,self.T(h[:,1]<1,torch.bool));q=(2*U/self.kn).clamp_min(1e-40).sqrt();old=self.T(h);maximum=torch.where(self.T(eligible,torch.bool),torch.maximum(old[:,0],q),old[:,0]);damage=torch.where(maximum<=self.on,torch.zeros_like(maximum),torch.where(maximum>=self.fail,torch.ones_like(maximum),self.fail*(maximum-self.on)/(maximum.clamp_min(1e-300)*(self.fail-self.on))))
   force=-torch.autograd.grad(((1-damage.detach())*U).sum(),y)[0]
   stored=((1-damage)*U).sum();diss=lambda z:.5*self.kn*self.on*self.fail/(self.fail-self.on)*(torch.minimum(self.fail,torch.maximum(self.on,z))-self.on)
   potential=stored+(diss(maximum)-diss(old[:,0])).sum()
  return dict(force=force.detach().cpu().numpy(),trial_history=torch.stack([maximum,damage],dim=1).detach().cpu().numpy(),stored_energy_j=stored.item(),incremental_potential_j=potential.item())
 def commit(self,trial):
  trial=np.asarray(trial)
  if trial.shape!=self.history.shape or np.any(trial<self.history-1e-12):raise ValueError('History cannot heal')
  self.evaluate(self.mesh['x'],history=trial);self.history=trial.copy()
 def tangent_action(self,*args,**kwargs):raise NotImplementedError('Old sparse-map tangent is not valid for the approved full-surface layout')

 def eligibility_from_contact(self,nodal_force):
  """Explicit adapter input must be actual applied blade nodal forces [N].
  Positive evidence on an incident interface face enables its assigned groups.
  No elapsed-time or commanded-depth failure rule is used.
  """
  f=np.asarray(nodal_force)
  if f.shape!=self.mesh['x'].shape or not np.isfinite(f).all():raise ValueError('Finite applied nodal blade forces required')
  active=np.linalg.norm(f,axis=1)>1e-9
  faces=self.quad['faces'];copies=dict(self.mesh['ties']);right=np.array([[copies[n] for n in face] for face in faces]);hit=np.any(active[faces]|active[right],axis=1);out=np.zeros(47,bool);out[np.unique(self.quad['groups'][hit])]=True
  return out
