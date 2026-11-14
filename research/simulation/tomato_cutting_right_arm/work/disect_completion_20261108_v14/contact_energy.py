"""Differentiable original contact potential with frozen broad-phase stencils.
Closest features remain differentiable; stencil discovery is refreshed per iterate.
"""
import torch

def dot(a,b):return (a*b).sum(-1)
def segment(p,a,b):
 v=b-a;t=(dot(p-a,v)/dot(v,v).clamp_min(1e-30)).clamp(0,1)
 return a+t[:,None]*v

def potential(p,kind,eps,radius,stiffness):
 a,b,c,d=p.unbind(1);result=torch.zeros(len(p),device=p.device,dtype=p.dtype)
 vt=kind==0
 if vt.any():
  pt,aa,bb,cc=a[vt],b[vt],c[vt],d[vt];u=bb-aa;v=cc-aa;w=pt-aa
  uu=dot(u,u);uv=dot(u,v);vv=dot(v,v);wu=dot(w,u);wv=dot(w,v);den=(uu*vv-uv*uv).clamp_min(1e-30)
  s=(vv*wu-uv*wv)/den;t=(uu*wv-uv*wu)/den
  inside=(s>=0)&(t>=0)&(s+t<=1)
  ds=[dot(pt-segment(pt,aa,bb),pt-segment(pt,aa,bb)),dot(pt-segment(pt,bb,cc),pt-segment(pt,bb,cc)),dot(pt-segment(pt,cc,aa),pt-segment(pt,cc,aa))]
  delta=pt-aa-s[:,None]*u-t[:,None]*v;ds.append(torch.where(inside,dot(delta,delta),torch.full_like(s,float('inf'))))
  result[vt]=torch.stack(ds).min(0).values
 ee=~vt;m=torch.ones_like(result)
 if ee.any():
  aa,bb,cc,dd=a[ee],b[ee],c[ee],d[ee];u=bb-aa;v=dd-cc;w=aa-cc
  uu=dot(u,u);uv=dot(u,v);vv=dot(v,v);uw=dot(u,w);vw=dot(v,w);den=uu*vv-uv*uv
  safe=torch.where(den>1e-14*uu*vv,den,torch.ones_like(den))
  s=(uv*vw-vv*uw)/safe;t=(uu*vw-uv*uw)/safe;inside=(den>1e-14*uu*vv)&(s>=0)&(s<=1)&(t>=0)&(t<=1)
  ds=[]
  for point,e0,e1 in [(aa,cc,dd),(bb,cc,dd),(cc,aa,bb),(dd,aa,bb)]:
   delta=point-segment(point,e0,e1);ds.append(dot(delta,delta))
  delta=aa+s[:,None]*u-cc-t[:,None]*v;ds.append(torch.where(inside,dot(delta,delta),torch.full_like(s,float('inf'))))
  result[ee]=torch.stack(ds).min(0).values
  cross=torch.linalg.cross(u,v);ratio=dot(cross,cross)/eps[ee];m[ee]=torch.where(ratio<1,ratio*(2-ratio),torch.ones_like(ratio))
 distance=torch.sqrt(result.clamp_min(1e-30));tau=radius*.5;minimum=1e-5;k2=tau*tau*stiffness
 low=.5*k2-k2*torch.log(distance.new_tensor(minimum/tau))-k2/minimum*(distance-minimum)+.5*k2/minimum**2*(distance-minimum)**2
 value=torch.where(distance<=minimum,low,torch.where(distance<tau,.5*k2-k2*torch.log(distance/tau),.5*stiffness*(radius-distance)**2))
 return (m*torch.where(distance<radius,value,torch.zeros_like(value))).sum()

class ContactGraph:
 def __init__(self,closure,q):
  import numpy as np
  closure.energy_force_precise(q.detach().cpu().numpy());e=closure.engine;n=int(e.stencil_count.numpy()[0]);assert n<=e.stencil_capacity
  self.ends=torch.as_tensor(e.endpoint.numpy()[:n].copy(),device=q.device,dtype=torch.long)
  self.kind=torch.as_tensor(e.kind.numpy()[:n].copy(),device=q.device,dtype=torch.long)
  self.eps=torch.as_tensor(e.mollifier_threshold.numpy()[:n].copy(),device=q.device,dtype=q.dtype)
  self.ids=torch.as_tensor(e.embedding['indices'],device=q.device,dtype=torch.long);self.w=torch.as_tensor(e.embedding['weights'],device=q.device,dtype=q.dtype)
  self.radius=e.margin;self.stiffness=e.model.soft_contact_ke
 def energy(self,q):
  proxy=(q[self.ids]*self.w[:,:,None]).sum(1)
  return potential(proxy[self.ends],self.kind,self.eps,self.radius,self.stiffness)
 def cache_hessian(self,q):
  # Each stencil has 12 local coordinates. Different stencils are independent
  # before assembly, so 12 reverse passes construct every local block.
  with torch.enable_grad():
   proxy=(q.detach()[self.ids]*self.w[:,:,None]).sum(1)
   local=proxy[self.ends].detach().requires_grad_(True)
   value=potential(local,self.kind,self.eps,self.radius,self.stiffness)
   grad=torch.autograd.grad(value,local,create_graph=True)[0].reshape(-1,12)
   columns=[]
   for j in range(12):
    columns.append(torch.autograd.grad(grad[:,j].sum(),local,retain_graph=True)[0].reshape(-1,12).detach())
   self.blocks=torch.stack(columns,dim=1)
  if not torch.isfinite(self.blocks).all():raise RuntimeError('Nonfinite contact Hessian')
 def action(self,u):
  proxy=(u[self.ids]*self.w[:,:,None]).sum(1)
  local=proxy[self.ends].reshape(-1,12)
  out=torch.einsum('nij,nj->ni',self.blocks,local).reshape(-1,4,3)
  accumulated=torch.zeros_like(proxy);accumulated.index_add_(0,self.ends.reshape(-1),out.reshape(-1,3))
  result=torch.zeros_like(u);result.index_add_(0,self.ids.reshape(-1),(accumulated[:,None,:]*self.w[:,:,None]).reshape(-1,3))
  return result
