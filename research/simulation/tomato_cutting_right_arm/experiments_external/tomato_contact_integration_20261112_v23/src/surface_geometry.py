"""Immutable native convex boundaries. Clones share immutable geometry only."""
from pathlib import Path
import ctypes as c
import numpy as np
from packed_polys import PackedPolys
L=c.CDLL(str(Path(__file__).resolve().parents[1]/'build/facets.so'))
I=c.POINTER(c.c_longlong);D=c.POINTER(c.c_double);H=c.c_void_p
L.surface_prepare.argtypes=[c.c_int,I,D];L.surface_prepare.restype=H
L.surface_event.argtypes=[H,I,D,D,D,D,D,D,c.c_int,c.c_int];L.surface_event.restype=H
L.geometry_error.restype=c.c_char_p
for k in ['count','vertex_count','changed']:
 f=getattr(L,'surface_'+k);f.argtypes=[H];f.restype=c.c_int
L.surface_data.argtypes=[H,I,D,I,I,D,D];L.surface_free.argtypes=[H]
class Surface:
 def __init__(self,polys=None,handle=None):
  self.h=handle
  if handle is None:
   ptr=np.ascontiguousarray(np.r_[0,np.cumsum([len(p) for p in polys])],np.int64);v=np.ascontiguousarray(np.concatenate(polys),np.float64)
   self.h=L.surface_prepare(len(polys),ptr.ctypes.data_as(I),v.ctypes.data_as(D))
  if not self.h:raise ValueError(L.geometry_error().decode())
 def __del__(self):
  if self.h:L.surface_free(self.h);self.h=None
 def event(self,codes,vol,cent,cn,cd,fn,fd,cut_id):
  codes=np.ascontiguousarray(codes,np.int64);front=fn is not None
  data=[np.ascontiguousarray(x,np.float64) for x in [vol,cent,cn,cd,fn if front else np.zeros_like(cn),fd if front else np.zeros_like(cd)]]
  h=L.surface_event(self.h,codes.ctypes.data_as(I),*[x.ctypes.data_as(D) for x in data],cut_id,int(front));s=Surface(handle=h) if h else None
  if s is None:raise ValueError(L.geometry_error().decode())
  n=L.surface_count(h);nv=L.surface_vertex_count(h);p=np.empty(n+1,np.int64);v=np.empty((nv,3));origin=np.empty(n,np.int64);codes=np.empty(n,np.int64);vol=np.empty(n);cent=np.empty((n,3))
  L.surface_data(h,p.ctypes.data_as(I),v.ctypes.data_as(D),origin.ctypes.data_as(I),codes.ctypes.data_as(I),vol.ctypes.data_as(D),cent.ctypes.data_as(D))
  return {'polys':PackedPolys(p,v),'origin':origin,'codes':codes,'V':vol,'X':cent,'changed':L.surface_changed(h),'surface':s}
