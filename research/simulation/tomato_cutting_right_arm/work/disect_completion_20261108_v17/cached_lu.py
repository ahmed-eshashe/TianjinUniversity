import numpy as np,cupy as cp
from cupyx import cusparse as cs
from cupyx.scipy.sparse.linalg._solve import SuperLU
class Triangle:
 def __init__(self,a,lower):
  self.a=a;self.b=cp.zeros((a.shape[0],1),dtype=a.dtype,order='F');self.c=cp.zeros_like(self.b);self.alpha=np.array(1.,dtype=a.dtype);self.handle=cs._device.get_cusparse_handle();self.ma=cs.SpMatDescriptor.create(a);self.mb=cs.DnMatDescriptor.create(self.b);self.mc=cs.DnMatDescriptor.create(self.c);api=cs._cusparse
  self.ma.set_attribute(api.CUSPARSE_SPMAT_FILL_MODE,api.CUSPARSE_FILL_MODE_LOWER if lower else api.CUSPARSE_FILL_MODE_UPPER);self.ma.set_attribute(api.CUSPARSE_SPMAT_DIAG_TYPE,api.CUSPARSE_DIAG_TYPE_NON_UNIT)
  self.desc=api.spSM_createDescr();self.args=(self.handle,api.CUSPARSE_OPERATION_NON_TRANSPOSE,api.CUSPARSE_OPERATION_NON_TRANSPOSE,self.alpha.ctypes.data,self.ma.desc,self.mb.desc,self.mc.desc,cs._dtype.to_cuda_dtype(a.dtype),api.CUSPARSE_SPSM_ALG_DEFAULT,self.desc)
  self.buffer=cp.empty(api.spSM_bufferSize(*self.args),dtype=cp.int8);api.spSM_analysis(*self.args,self.buffer.data.ptr)
 def solve(self,rhs):
  self.b[:,0]=rhs;self.c.fill(0);cs._cusparse.spSM_solve(*self.args,self.buffer.data.ptr);return self.c[:,0]
 def __del__(self):
  try:cs._cusparse.spSM_destroyDescr(self.desc)
  except Exception:pass
class CachedLU(SuperLU):
 def __init__(self,f):
  super().__init__(f);self.lower=Triangle(self.L,True);self.upper=Triangle(self.U,False)
 def solve(self,rhs):
  y=self.lower.solve(rhs[self._perm_r_rev]);return self.upper.solve(y)[self.perm_c]
