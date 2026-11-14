"""Direct sparse numerical search solve with independent GPU residual checks.

Only the static optimizer's search system is solved here. Physical forces,
potential and acceptance criteria are inherited unchanged. Matrix capacity
padding is excluded from CPU storage; accepted solutions are checked against
the actual GPU BSR operator, with bounded iterative refinement if needed.
"""
import numpy as np
import warp as wp
from warp import sparse
from tomato_static_safeguarded import SafeguardedStaticCandidate

def direct_direction(A,rhs,solution,product,*,maximum_refinements=3):
 from scipy.sparse import bsr_matrix
 from scipy.sparse.linalg import splu
 offsets=A.offsets.numpy();nn=int(offsets[-1]);n=len(offsets)-1;values=A.values.numpy()[:nn];columns=A.columns.numpy()[:nn]
 if not np.isfinite(values).all():raise ValueError('Nonfinite actual search matrix')
 cpu=bsr_matrix((values,columns,offsets),shape=(3*n,3*n)).tocsc();factor=splu(cpu);b=rhs.numpy().reshape(-1);x=factor.solve(b);scale=float(np.linalg.norm(b));threshold=max(5e-9*scale,1e-15)
 for refinement in range(maximum_refinements+1):
  solution.assign(x.reshape(n,3));sparse.bsr_mv(A,solution,product);residual=b-product.numpy().reshape(-1);true=float(np.linalg.norm(residual))
  if np.isfinite(true)and true<=threshold:break
  if refinement<maximum_refinements:x+=factor.solve(residual)
 return dict(cg_iterations=0,linear_backend='CPU sparse LU, GPU BSR true residual',direct_factorizations=1,direct_refinement_steps=refinement,cg_true_residual_n=true,cg_rhs_norm_n=scale,linear_true_residual_n=true,linear_valid=bool(np.isfinite(true)and true<=threshold))

class DirectStaticCandidate(SafeguardedStaticCandidate):
 def _linear_direction(self,rhs):return direct_direction(self.assembly.matrix,rhs,self.direction,self.product)
