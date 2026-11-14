"""Block candidate with a tighter absolute linear-solve floor for tiny nodes.

The physical and nonlinear gates are unchanged. This addresses absolute PCG
stopping at 1e-13 N while a tiny-mass node still exceeds the velocity-defect
criterion. Only linear numerical tolerances are tightened.
"""
import numpy as np
import warp as wp
from warp import sparse
from warp.optim.linear import cg
from tomato_block_preconditioner import BlockJacobi,BlockLBFGSCandidate

class TightBlockCandidate(BlockLBFGSCandidate):
 def _linear_direction(self,rhs):
  pre=BlockJacobi(self.assembly.matrix);self.direction.zero_();iterations,recursive,tolerance=cg(self.assembly.matrix,rhs,self.direction,tol=1e-9,atol=1e-16,maxiter=self.maximum_cg,M=pre.operator,check_every=10,use_cuda_graph=True);sparse.bsr_mv(self.assembly.matrix,self.direction,self.product);b=rhs.numpy();true=float(np.linalg.norm(self.product.numpy()-b));scale=float(np.linalg.norm(b));valid=bool(np.isfinite(true)and true<=max(5e-9*scale,1e-15));return dict(cg_iterations=int(iterations),cg_true_residual_n=true,cg_rhs_norm_n=scale,linear_valid=valid,preconditioner_shifted_blocks=int(pre.shifted_count.numpy()[0]),preconditioner_maximum_relative_shift=float(pre.shifts.numpy().max(initial=0.)))
