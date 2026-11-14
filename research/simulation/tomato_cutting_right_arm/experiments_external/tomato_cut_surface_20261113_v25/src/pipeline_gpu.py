"""Asynchronous independent environments, with owned pinned observations.

Every environment advances using its latest completed state. Geometry changes
are forbidden during an unfinished step. Failure restores its own prior state.
"""
import ctypes as c
import warp as wp
from active_gpu import GPU as ActiveGPU,CapacityError,L
L.dispatch_stream_create.restype=c.c_void_p
L.dispatch_stream_free.argtypes=[c.c_void_p]
class GPU(ActiveGPU):
 def __init__(self,*args,**kwargs):
  self.pending=None;self.host_bad=wp.empty(1,dtype=int,device='cpu',pinned=True);self.bad_view=self.host_bad.numpy()
  self.stream_handle=L.dispatch_stream_create()
  if not self.stream_handle:raise ValueError(L.dispatch_error().decode())
  self.stream=wp.Stream('cuda:0',cuda_stream=self.stream_handle)
  with wp.ScopedStream(self.stream):
   super().__init__(*args,**kwargs)
   self.host_q=wp.empty(self.ncap,dtype=wp.vec3,device='cpu',pinned=True);self.host_v=wp.empty(self.ncap,dtype=wp.vec3,device='cpu',pinned=True)
   self.q_view=self.host_q.numpy();self.v_view=self.host_v.numpy();self.graph(64)
 def __del__(self):
  # Warp owns the registration, this wrapper owns the external CUDA stream.
  if hasattr(self,'stream_handle') and self.stream_handle:
   wp.synchronize_stream(self.stream);self.stream=None;L.dispatch_stream_free(self.stream_handle);self.stream_handle=None
 def check(self):
  wp.copy(self.host_bad,self.bad,stream=self.stream);wp.synchronize_stream(self.stream)
  if self.bad_view[0]:raise ValueError(('pipeline mechanics rejected',int(self.bad_view[0])))
 def replace(self,*args,**kwargs):
  if self.pending is not None:raise ValueError('cannot replace an unfinished environment')
  with wp.ScopedStream(self.stream):return super().replace(*args,**kwargs)
 def step_async(self,n,block=64):
  if self.pending is not None:raise ValueError('previous step is unfinished')
  if n<=0:raise ValueError('positive step count required')
  with wp.ScopedStream(self.stream):
   full,rem=divmod(n,block);graphs=[self.graph(block)]*full
   if rem:graphs.append(self.graph(rem))
   wp.copy(self.backup[0],self.q);wp.copy(self.backup[1],self.vh);self.bad.zero_()
   for g in graphs:wp.capture_launch(g)
   self.stress();wp.copy(self.vfull,self.vh);self.advance(self.vfull,.5*self.dt,0.)
   wp.copy(self.host_q,self.q,count=self.n);wp.copy(self.host_v,self.vfull,count=self.n);wp.copy(self.host_bad,self.bad)
  self.pending=n
 def finish(self):
  if self.pending is None:raise ValueError('no pending step')
  wp.synchronize_stream(self.stream);n=self.pending;self.pending=None
  if self.bad_view[0]:
   with wp.ScopedStream(self.stream):
    wp.copy(self.q,self.backup[0]);wp.copy(self.vh,self.backup[1]);self.bad.zero_()
   wp.synchronize_stream(self.stream)
   raise ValueError(('pipeline mechanics rejected; state rolled back',int(self.bad_view[0])))
  self.steps+=n
  return self._bodies(self.q_view[:self.n].astype(float),self.v_view[:self.n].astype(float))
 def _bodies(self,q,v):
  out=[]
  for j,a in enumerate(self.aggregates):
   lo,hi=self.bounds[j:j+2];a.q=q[lo:hi];a.v=v[lo:hi];a.sync();a.body.time=self.base[j][0]+self.steps*self.dt;a.body.steps=self.base[j][1]+self.steps;out.append(a.body)
  return out
 def step(self,n,block=64):self.step_async(n,block);return self.finish()
 def state(self):
  if self.pending is not None:raise ValueError('cannot read unfinished state')
  with wp.ScopedStream(self.stream):
   self.stress();wp.copy(self.vfull,self.vh);self.advance(self.vfull,.5*self.dt,0.)
   wp.copy(self.host_q,self.q,count=self.n);wp.copy(self.host_v,self.vfull,count=self.n)
   self.check()
  return self.q_view[:self.n].astype(float),self.v_view[:self.n].astype(float)
