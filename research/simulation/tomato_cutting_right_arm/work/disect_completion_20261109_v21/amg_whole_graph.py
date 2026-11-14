"""Speculative graph of the unchanged IMEX solve; strict checks or original fallback.
Geometry is evaluated once outside capture. No state advance before acceptance.
"""
import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_precontact_20261108_v06'))
from amg_contact import AMGContact as ContactBulk
from numerics import torch
class WholeContactGraph(ContactBulk):
 def build_graph(self,h):
  self.enable_gather() if not hasattr(self,'csr') else None
  self.graph_mask=self.mask.clone()
  self.build_amg(h)
  self.h=h;self.root=self.mass.sqrt();self.scale=(self.free/self.root).expand_as(self.x).contiguous()
  self.out_v=torch.zeros_like(self.x);self.out_fric=torch.zeros_like(self.x)
  self.quality=torch.zeros(3,device='cuda',dtype=torch.float64)
  self.scalars=torch.zeros(4+(self.x.numel()+255)//256,device='cuda',dtype=torch.float64)
  self.ap=torch.zeros_like(self.x);self.zz=torch.zeros_like(self.x)
  self.zeros=torch.zeros_like(self.x);self.fg=torch.zeros_like(self.x)
  self.fallbacks=0;self.accepts=0;self.max_residual=0.
  def body():
   self.k.ground(self.x,self.zeros,self.graph_mask,self.fg)
   rhs=(self.root*self.v+h*((self.f+self.fg)/self.root+self.root*self.gravity))*self.free
   d0=1+h*self.diag/self.mass
   active=(self.x[:,1]<.001)*self.graph_mask;limit=.2*(.001-self.x[:,1]).clamp_min(0)*1000*self.graph_mask
   k=torch.zeros_like(self.x);k[:,0]=1000*active;k[:,2]=1000*active
   lim=torch.zeros_like(self.x);lim[:,0]=limit;lim[:,2]=limit
   def A(y):
    self.k.pcg_op(y,self.scale,self.t,self.j,self.weight,*self.csr,self.rate,self.ap,h)
    return self.ap.clone()
   def friction(y):return torch.clamp(k*self.scale*y,min=-lim,max=lim)
   def psi(y):
    av=(self.scale*y).abs();return torch.where(k*av<=lim,.5*k*av.square(),lim*av-.5*lim.square()/k.clamp_min(1)).sum()
   y=self.root*torch.sign(self.v)*torch.maximum(self.v.abs()/(1+h*k/self.mass),self.v.abs()-h*lim/self.mass)
   normalizer=rhs.norm().clamp_min(1e-14);bad=torch.zeros((),device='cuda',dtype=torch.bool);maxinner=torch.zeros((),device='cuda',dtype=torch.float64)
   for _ in range(1):
    ay=A(y);g=ay-rhs+h*self.scale*friction(y);needed=g.norm()>1e-9*normalizer
    slope=k*((k*self.scale*y).abs()<=lim);extra=h*self.scale.square()*slope;diag=d0+h*slope/self.mass
    r=-g;delta=torch.zeros_like(y);p=self.amg_cycle(r);self.scalars.zero_();self.scalars[0].copy_((r*p).sum())
    for __ in range(32):
     self.k.pcg_op(p,self.scale,self.t,self.j,self.weight,*self.csr,self.rate,self.ap,h)
     self.ap.add_(extra*p)
     alpha=self.scalars[0]/(p*self.ap).sum().clamp_min(1e-300)
     delta=delta+alpha*p;r=r-alpha*self.ap;zz=self.amg_cycle(r);new=(r*zz).sum()
     p=zz+(new/self.scalars[0].clamp_min(1e-300))*p;self.scalars[0].copy_(new)
    hd=A(delta)+extra*delta;inner=(-g-hd).norm()/g.norm().clamp_min(1e-30)
    maxinner=torch.maximum(maxinner,torch.where(needed,inner,0.))
    change=((ay-rhs)*delta).sum()+.5*(delta*A(delta)).sum()+h*(psi(y+delta)-psi(y))
    bad=bad|(needed&(change>1e-4*(g*delta).sum()+1e-24))
    y=torch.where(needed,y+delta,y)
   final=(A(y)-rhs+h*self.scale*friction(y)).norm()/normalizer
   self.quality[0].copy_(final);self.quality[1].copy_(maxinner);self.quality[2].copy_(bad.to(torch.float64))
   self.out_v.copy_(self.scale*y);self.out_fric.copy_(-friction(y))
  warm=torch.cuda.Stream();warm.wait_stream(torch.cuda.current_stream())
  with torch.cuda.stream(warm):body()
  torch.cuda.current_stream().wait_stream(warm);torch.cuda.synchronize()
  self.graph=torch.cuda.CUDAGraph()
  with torch.cuda.graph(self.graph):body()
 def implicit(self,h,**kwargs):
  start=time.perf_counter();self.geometry()
  if not hasattr(self,'graph') or self.h!=h:self.build_graph(h)
  self.graph_mask.copy_(self.mask);self.fg.zero_();self.graph.replay();quality=self.quality.cpu().numpy()
  if not ((quality[:2]<=1e-9).all() and quality[2]==0):
   self.fallbacks+=1
   if self.fallbacks<4:print('GRAPH_REJECT',quality,flush=True)
   return super().implicit(h,**kwargs)
  self.accepts+=1;self.max_residual=max(self.max_residual,float(quality[0]))
  self.last_friction=self.out_fric.clone();self.last_normal=self.fg.clone();self.last_force=self.f-self.damping(self.out_v)+self.fg+self.last_friction
  self.v.copy_(self.out_v);self.x.add_(h*self.v);self.guess.copy_(self.root*self.v)
  return dict(relative_residual=float(quality[0]),inner_max_residual=float(quality[1]),wall_s=time.perf_counter()-start)
