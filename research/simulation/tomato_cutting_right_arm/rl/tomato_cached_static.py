"""Cached sparse factor preconditioner; exact current-system residual is required.

Only the search solve changes. Old factors precondition the current sparse
system; bounded CG or stale-factor correction can never qualify a solution
without the independent actual GPU BSR residual. A fresh factor is the
fallback. Original force, energy, state and all acceptance gates are retained.
"""
import numpy as np
import warp as wp
from warp import sparse
from tomato_static_safeguarded import SafeguardedStaticCandidate

class CachedDirectSolve:
 def __init__(self):self.factor=None;self.shape=None
 def solve(self,A,rhs,solution,product):
  from scipy.sparse import bsr_matrix
  from scipy.sparse.linalg import splu,LinearOperator,cg
  import time
  start=time.monotonic();offsets=A.offsets.numpy();nn=int(offsets[-1]);n=len(offsets)-1;values=A.values.numpy()[:nn];columns=A.columns.numpy()[:nn]
  if not np.isfinite(values).all():raise ValueError('Nonfinite actual search matrix')
  cpu=bsr_matrix((values,columns,offsets),shape=(3*n,3*n)).tocsc();b=rhs.numpy().reshape(-1);scale=float(np.linalg.norm(b));threshold=max(5e-9*scale,1e-15);iterations=0;fresh=0;info=None;refinements=0
  def count(_):
   nonlocal iterations
   iterations+=1
  if self.factor is not None and self.shape==cpu.shape:
   M=LinearOperator(cpu.shape,matvec=self.factor.solve,dtype=np.float64);x,info=cg(cpu,b,M=M,rtol=1e-10,atol=1e-16,maxiter=128,callback=count)
  else:x=np.zeros_like(b)
  solution.assign(x.reshape(n,3));sparse.bsr_mv(A,solution,product);residual=b-product.numpy().reshape(-1);true=float(np.linalg.norm(residual))
  if not np.isfinite(true)or true>threshold:
   self.factor=splu(cpu);self.shape=cpu.shape;fresh=1;x=self.factor.solve(b)
   for refinements in range(4):
    solution.assign(x.reshape(n,3));sparse.bsr_mv(A,solution,product);residual=b-product.numpy().reshape(-1);true=float(np.linalg.norm(residual))
    if np.isfinite(true)and true<=threshold:break
    if refinements<3:x+=self.factor.solve(residual)
  return dict(cg_iterations=iterations,cpu_cg_status=None if info is None else int(info),linear_backend='CPU cached-LU-preconditioned CG with fresh LU fallback; actual GPU residual',direct_factorizations=fresh,direct_refinement_steps=refinements,cg_true_residual_n=true,cg_rhs_norm_n=scale,linear_true_residual_n=true,linear_valid=bool(np.isfinite(true)and true<=threshold),linear_wall_s=time.monotonic()-start)

class CachedStaticCandidate(SafeguardedStaticCandidate):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.linear_cache=CachedDirectSolve()
 def _linear_direction(self,rhs):return self.linear_cache.solve(self.assembly.matrix,rhs,self.direction,self.product)
