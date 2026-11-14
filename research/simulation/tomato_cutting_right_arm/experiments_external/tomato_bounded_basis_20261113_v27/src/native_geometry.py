from pathlib import Path
import ctypes as c
import numpy as np
LIB=c.CDLL(str(Path(__file__).resolve().parents[1]/'build/geometry.so'))
I=c.POINTER(c.c_longlong);D=c.POINTER(c.c_double);H=c.c_void_p
LIB.geometry_event.argtypes=[c.c_int,I,D,I,D,D,D,D,D,D,c.c_int,c.c_int];LIB.geometry_event.restype=H
LIB.geometry_error.restype=c.c_char_p;LIB.result_free.argtypes=[H]
for name in ['regions','vertices','changed']:
 f=getattr(LIB,'result_'+name);f.argtypes=[H];f.restype=c.c_int
for name in ['ptr','origin','codes','xyz','volume','centroid']:
 f=getattr(LIB,'result_'+name);f.argtypes=[H];f.restype=I if name in ['ptr','origin','codes'] else D
def event(polys,codes,vol,cent,cn,cd,fn,fd,cut_id):
 ptr=np.ascontiguousarray(np.r_[0,np.cumsum([len(p) for p in polys])],np.int64);v=np.ascontiguousarray(np.concatenate(polys),np.float64);codes=np.ascontiguousarray(codes,np.int64)
 data=[np.ascontiguousarray(x,np.float64) for x in [vol,cent,cn,cd]]
 front=fn is not None
 data += [np.ascontiguousarray(fn if front else np.zeros_like(cn),np.float64),np.ascontiguousarray(fd if front else np.zeros_like(cd),np.float64)]
 h=LIB.geometry_event(len(polys),ptr.ctypes.data_as(I),v.ctypes.data_as(D),codes.ctypes.data_as(I),*[x.ctypes.data_as(D) for x in data],cut_id,int(front))
 if not h:raise ValueError(LIB.geometry_error().decode())
 try:
  nr=LIB.result_regions(h);nv=LIB.result_vertices(h)
  def get(name,n):return np.ctypeslib.as_array(getattr(LIB,'result_'+name)(h),shape=(n,)).copy()
  p=get('ptr',nr+1);xyz=get('xyz',3*nv).reshape(-1,3)
  return {'polys':[xyz[a:b].copy() for a,b in zip(p[:-1],p[1:])],'origin':get('origin',nr),'codes':get('codes',nr),'V':get('volume',nr),'X':get('centroid',nr*3).reshape(-1,3),'changed':LIB.result_changed(h)}
 finally:LIB.result_free(h)
