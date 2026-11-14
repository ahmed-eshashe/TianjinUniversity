"""Progressive forward adapter. Same moving-frame forces; pure trials and explicit commits."""
import warp as wp
import numpy as np
@wp.func
def source_vector(v:wp.vec3d):return wp.vec3d(v[0],-v[2],v[1])
@wp.func
def world_vector(v:wp.vec3d):return wp.vec3d(v[0],v[2],-v[1])
@wp.func
def anchor_position(q:wp.array[wp.vec3d],ai:wp.array[wp.vec3i],bi:wp.array[wp.vec3i],aw:wp.array[wp.vec3d],i:int):
 p=wp.vec3d(0.)
 for j in range(3):p+=wp.float64(.5)*aw[i][j]*(q[ai[i][j]]+q[bi[i][j]])
 return source_vector(p)
@wp.kernel(enable_backward=False)
def frames(q:wp.array[wp.vec3d],ai:wp.array[wp.vec3i],bi:wp.array[wp.vec3i],aw:wp.array[wp.vec3d],sign:wp.array[wp.float64],frame:wp.array[wp.mat33d],invalid:wp.array[int],active:wp.array[int]):
 i=wp.tid()
 if active[i]==0:return
 a=anchor_position(q,ai,bi,aw,3*i);u=anchor_position(q,ai,bi,aw,3*i+1)-a;v=anchor_position(q,ai,bi,aw,3*i+2)-a;c=wp.cross(u,v)
 if wp.length(u)<wp.float64(1.e-12) or wp.length(c)<wp.float64(1.e-12):wp.atomic_add(invalid,0,1)
 else:
  t=u/wp.length(u);n=sign[i]*c/wp.length(c);b=wp.cross(n,t);frame[i]=wp.mat33d(n[0],t[0],b[0],n[1],t[1],b[1],n[2],t[2],b[2])
@wp.kernel(enable_backward=False)
def quadrature(q:wp.array[wp.vec3d],li:wp.array[wp.vec3i],ri:wp.array[wp.vec3i],bary:wp.array[wp.vec3d],group:wp.array[int],weight:wp.array[wp.float64],K:wp.array[wp.mat33d],frame:wp.array[wp.mat33d],force:wp.array[wp.vec3d],frame_gradient:wp.array[wp.mat33d],energy:wp.array[wp.float64],factor:wp.array[wp.float64]):
 i=wp.tid();g=group[i]
 if factor[g]==wp.float64(0.):return
 gap=wp.vec3d(0.)
 for j in range(3):gap+=bary[i][j]*source_vector(q[ri[i][j]]-q[li[i][j]])
 local=wp.transpose(frame[g])*gap;e=wp.vec3d(wp.max(local[0],wp.float64(0.)),local[1],local[2]);gl=factor[g]*(K[g]*e)
 wp.atomic_add(energy,g,wp.float64(.5)*weight[i]*wp.dot(e,gl))
 if local[0]<wp.float64(0.):gl[0]=wp.float64(0.)
 gl=weight[i]*gl;f=world_vector(frame[g]*gl)
 for j in range(3):
  wp.atomic_add(force,li[i][j],bary[i][j]*f);wp.atomic_add(force,ri[i][j],-bary[i][j]*f)
 wp.atomic_add(frame_gradient,g,wp.outer(gap,gl))
@wp.kernel(enable_backward=False)
def anchor_force(q:wp.array[wp.vec3d],ai:wp.array[wp.vec3i],bi:wp.array[wp.vec3i],aw:wp.array[wp.vec3d],sign:wp.array[wp.float64],frame:wp.array[wp.mat33d],frame_gradient:wp.array[wp.mat33d],force:wp.array[wp.vec3d],active:wp.array[int]):
 i=wp.tid()
 if active[i]==0:return
 a=anchor_position(q,ai,bi,aw,3*i);u=anchor_position(q,ai,bi,aw,3*i+1)-a;v=anchor_position(q,ai,bi,aw,3*i+2)-a;F=frame[i];G=frame_gradient[i]
 n=wp.vec3d(F[0,0],F[1,0],F[2,0]);t=wp.vec3d(F[0,1],F[1,1],F[2,1]);gn=wp.vec3d(G[0,0],G[1,0],G[2,0]);gt=wp.vec3d(G[0,1],G[1,1],G[2,1]);gb=wp.vec3d(G[0,2],G[1,2],G[2,2]);gn+=wp.cross(t,gb);gt+=wp.cross(gb,n)
 gc=sign[i]*(gn-n*wp.dot(n,gn))/wp.length(wp.cross(u,v));gu=(gt-t*wp.dot(t,gt))/wp.length(u)+wp.cross(v,gc);gv=wp.cross(gc,u)
 for aidx in range(3):
  grad=-gu-gv
  if aidx==1:grad=gu
  elif aidx==2:grad=gv
  f=-wp.float64(.5)*world_vector(grad)
  for j in range(3):
   wp.atomic_add(force,ai[3*i+aidx][j],aw[3*i+aidx][j]*f);wp.atomic_add(force,bi[3*i+aidx][j],aw[3*i+aidx][j]*f)
import torch
class ProgressiveGPU:
 def __init__(self,s):
  self.source=s;self.device='cuda:0';self.n=len(s.mesh['x']);self.ng=len(s.patches)
  def A(t,dtype,shape=None):
   a=t.detach().cpu().numpy()
   if shape is not None:a=a.reshape(shape)
   return wp.array(a,dtype=dtype,device=self.device)
  self.ai=A(s.ai,wp.vec3i,(-1,3));self.bi=A(s.bi,wp.vec3i,(-1,3));self.aw=A(s.aw,wp.vec3d,(-1,3));self.sign=A(s.sign,wp.float64);self.li=A(s.li,wp.vec3i);self.ri=A(s.ri,wp.vec3i);self.bary=A(s.bary,wp.vec3d);self.group=A(s.group,wp.int32);self.weight=A(s.weight,wp.float64);self.K=A(s.K,wp.mat33d)
  self.frame=wp.zeros(self.ng,dtype=wp.mat33d,device=self.device);self.fg=wp.zeros_like(self.frame);self.force=wp.zeros(self.n,dtype=wp.vec3d,device=self.device);self.energy=wp.zeros(self.ng,dtype=wp.float64,device=self.device);self.invalid=wp.zeros(1,dtype=int,device=self.device)
  self.history=torch.zeros((self.ng,2),dtype=torch.float64,device=self.device);self.generation=0
  self.on=s.on.to(self.device);self.fail=s.fail.to(self.device);self.kn=s.kn.to(self.device)
 def canonical(self,maximum):
  return torch.where(maximum<=self.on,0.,torch.where(maximum>=self.fail,1.,self.fail*(maximum-self.on)/(maximum.clamp_min(1e-300)*(self.fail-self.on))))
 def validate(self,h):
  if h.shape!=(self.ng,2) or not torch.isfinite(h).all() or (h<0).any() or (h[:,1]>1).any() or torch.max(torch.abs(self.canonical(h[:,0])-h[:,1]))>1e-10:raise ValueError('Invalid canonical history')
 def dissipation(self,maximum):
  return .5*self.kn*self.on*self.fail/(self.fail-self.on)*(torch.minimum(self.fail,torch.maximum(self.on,maximum))-self.on)
 def _force(self,q,factor,active):
  q=wp.from_torch(q,dtype=wp.vec3d);factor=wp.from_torch(factor.contiguous());active=wp.from_torch(active.contiguous());self.force.zero_();self.fg.zero_();self.energy.zero_();self.invalid.zero_()
  wp.launch(frames,self.ng,inputs=[q,self.ai,self.bi,self.aw,self.sign],outputs=[self.frame,self.invalid,active])
  wp.launch(quadrature,len(self.group),inputs=[q,self.li,self.ri,self.bary,self.group,self.weight,self.K,self.frame],outputs=[self.force,self.fg,self.energy,factor])
  wp.launch(anchor_force,self.ng,inputs=[q,self.ai,self.bi,self.aw,self.sign,self.frame,self.fg],outputs=[self.force,active])
  return wp.to_torch(self.force),wp.to_torch(self.energy)
 def evaluate(self,q,eligible=None):
  if eligible is None:eligible=torch.zeros(self.ng,dtype=torch.bool,device=self.device)
  eligible=torch.as_tensor(eligible,device=self.device)
  if eligible.shape!=(self.ng,) or eligible.dtype!=torch.bool:raise ValueError('Boolean group eligibility required')
  active=(self.history[:,1]<1).to(torch.int32)
  with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):
   _,U=self._force(q,active.to(torch.float64),active);U=U.clone()
   if int(self.invalid.numpy()[0]):raise ValueError('Collapsed active material frame')
   maximum=torch.where(eligible,torch.maximum(self.history[:,0],(2*U/self.kn).clamp_min(1e-40).sqrt()),self.history[:,0]);damage=self.canonical(maximum)
   trial=torch.stack([maximum,damage],dim=1);force,stored=self._force(q,1-damage,active)
   return dict(force=force.clone(),trial_history=trial.clone(),stored_energy_j=stored.sum().clone(),incremental_potential_j=(stored.sum()+(self.dissipation(maximum)-self.dissipation(self.history[:,0])).sum()).clone(),dissipation_j=self.dissipation(maximum).sum().clone(),generation=self.generation)
 def commit(self,result):
  if result['generation']!=self.generation:raise ValueError('Stale or repeated trial commit')
  trial=result['trial_history'];self.validate(trial)
  if (trial<self.history-1e-12).any():raise ValueError('History cannot heal')
  self.history.copy_(trial);self.generation+=1
 def reset(self):self.history.zero_();self.generation+=1
 def state_dict(self):return {'history':self.history.detach().cpu().numpy().copy(),'generation':self.generation}
 def load_state_dict(self,state):
  h=torch.as_tensor(state['history'],dtype=torch.float64,device=self.device);self.validate(h);self.history.copy_(h);self.generation+=1
