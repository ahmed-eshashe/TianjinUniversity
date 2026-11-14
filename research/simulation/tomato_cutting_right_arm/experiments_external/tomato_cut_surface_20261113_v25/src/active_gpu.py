"""Resize execution grids, not storage, when current cut topology changes.

No future topology is assumed. The same graph nodes, kernels and arguments are
retained; only grids covering active rows/regions change through CUDA's API.
"""
from pathlib import Path
import ctypes as c
import warp as wp
from cached_gpu import GPU as StorageGPU,CapacityError
from persistent_gpu import stress,gather,advance
L=c.CDLL(str(Path(__file__).resolve().parents[1]/'build/dispatch.so'))
L.dispatch_prepare.argtypes=[c.c_void_p,c.c_void_p];L.dispatch_prepare.restype=c.c_void_p
L.dispatch_update.argtypes=[c.c_void_p,c.c_int,c.c_int];L.dispatch_update.restype=c.c_int
L.dispatch_free.argtypes=[c.c_void_p];L.dispatch_error.restype=c.c_char_p
L.dispatch_executable.argtypes=[c.c_void_p];L.dispatch_executable.restype=c.c_void_p
class Dispatch:
 def __init__(self,g):
  self.h=L.dispatch_prepare(g.graph,g.graph_exec)
  if not self.h:raise ValueError(L.dispatch_error().decode())
  if g.graph_exec is None:g.graph_exec=L.dispatch_executable(self.h)
 def update(self,n,p):
  if L.dispatch_update(self.h,n,p):raise ValueError(L.dispatch_error().decode())
 def __del__(self):
  if self.h:L.dispatch_free(self.h)
class GPU(StorageGPU):
 def __init__(self,*args,**kwargs):self.dispatch={};super().__init__(*args,**kwargs)
 def _upload(self,d,aggregates):
  super()._upload(d,aggregates)
  for h in self.dispatch.values():h.update(self.n,self.p)
 def replace(self,*args,**kwargs):
  n,p=self.n,self.p
  try:super().replace(*args,**kwargs)
  except Exception:
   for h in self.dispatch.values():h.update(n,p)
   raise
 def graph(self,n):
  g=super().graph(n)
  if n not in self.dispatch:self.dispatch[n]=Dispatch(g);self.dispatch[n].update(self.n,self.p)
  return g
