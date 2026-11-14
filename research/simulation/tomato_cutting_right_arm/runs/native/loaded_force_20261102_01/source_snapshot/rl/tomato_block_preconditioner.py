"""SPD 3x3 block-Jacobi linear preconditioner; never modifies the system matrix.

Normalized Cholesky avoids cofactor determinant overflow/cancellation. A fixed
relative diagonal shift is used only when required for a safe factorization.
The shift regularizes the preconditioner, not material or contact stiffness.
"""
import numpy as np
import warp as wp
from warp import sparse
from warp.optim.linear import LinearOperator,cg
from tomato_global_lbfgs import GlobalLBFGSCandidate

@wp.kernel(enable_backward=False)
def factor_blocks(diagonal:wp.array[wp.mat33d],factors:wp.array[wp.mat33d],scales:wp.array[wp.float64],shifts:wp.array[wp.float64],shifted_count:wp.array[int],invalid:wp.array[int]):
 i=wp.tid();h=wp.float64(.5)*(diagonal[i]+wp.transpose(diagonal[i]));scale=wp.max(wp.max(wp.abs(h[0,0]),wp.abs(h[1,1])),wp.abs(h[2,2]));valid=bool(False);L=wp.mat33d(0.);shift=wp.float64(0.)
 if scale>wp.float64(0.)and wp.isfinite(scale):
  a=h/scale
  for attempt in range(8):
   d0=a[0,0]+shift
   if d0>wp.float64(1.e-14):
    l00=wp.sqrt(d0);l10=a[1,0]/l00;l20=a[2,0]/l00;d1=a[1,1]+shift-l10*l10
    if d1>wp.float64(1.e-14):
     l11=wp.sqrt(d1);l21=(a[2,1]-l20*l10)/l11;d2=a[2,2]+shift-l20*l20-l21*l21
     if d2>wp.float64(1.e-14):L=wp.mat33d(l00,wp.float64(0.),wp.float64(0.),l10,l11,wp.float64(0.),l20,l21,wp.sqrt(d2));valid=True;break
   if shift==wp.float64(0.):shift=wp.float64(1.e-12)
   else:shift*=wp.float64(10.)
 if not valid:wp.atomic_add(invalid,0,1)
 factors[i]=L;scales[i]=scale;shifts[i]=shift
 if shift>wp.float64(0.):wp.atomic_add(shifted_count,0,1)

@wp.kernel(enable_backward=False)
def apply_blocks(factors:wp.array[wp.mat33d],scales:wp.array[wp.float64],x:wp.array[wp.vec3d],y:wp.array[wp.vec3d],z:wp.array[wp.vec3d],alpha:wp.float64,beta:wp.float64):
 i=wp.tid();L=factors[i];b=x[i]/scales[i];v0=b[0]/L[0,0];v1=(b[1]-L[1,0]*v0)/L[1,1];v2=(b[2]-L[2,0]*v0-L[2,1]*v1)/L[2,2];r2=v2/L[2,2];r1=(v1-L[2,1]*r2)/L[1,1];r0=(v0-L[1,0]*r1-L[2,0]*r2)/L[0,0];result=alpha*wp.vec3d(r0,r1,r2)
 if beta!=wp.float64(0.):result+=beta*y[i]
 z[i]=result

class BlockJacobi:
 def __init__(self,A):
  diagonal=sparse.bsr_get_diag(A);n=len(diagonal);self.factors=wp.empty(n,dtype=wp.mat33d);self.scales=wp.empty(n,dtype=wp.float64);self.shifts=wp.empty(n,dtype=wp.float64);self.shifted_count=wp.zeros(1,dtype=int);self.invalid=wp.zeros(1,dtype=int);wp.launch(factor_blocks,dim=n,inputs=[diagonal],outputs=[self.factors,self.scales,self.shifts,self.shifted_count,self.invalid],block_dim=64)
  if self.invalid.numpy()[0]:raise ValueError('Block preconditioner could not obtain a finite positive factor')
  def matvec(x,y,z,alpha,beta):wp.launch(apply_blocks,dim=n,inputs=[self.factors,self.scales,x,y,z,wp.float64(alpha),wp.float64(beta)],block_dim=64)
  self.operator=LinearOperator(shape=A.shape,dtype=A.dtype,device=A.device,matvec=matvec)

class BlockLBFGSCandidate(GlobalLBFGSCandidate):
 def _linear_direction(self,rhs):
  pre=BlockJacobi(self.assembly.matrix);self.direction.zero_();iterations,recursive,tolerance=cg(self.assembly.matrix,rhs,self.direction,tol=1e-9,atol=1e-13,maxiter=self.maximum_cg,M=pre.operator,check_every=10,use_cuda_graph=True);sparse.bsr_mv(self.assembly.matrix,self.direction,self.product);b=rhs.numpy();true=float(np.linalg.norm(self.product.numpy()-b));scale=float(np.linalg.norm(b));valid=bool(np.isfinite(true)and true<=max(5e-9*scale,1e-12));return dict(cg_iterations=int(iterations),cg_true_residual_n=true,cg_rhs_norm_n=scale,linear_valid=valid,preconditioner_shifted_blocks=int(pre.shifted_count.numpy()[0]),preconditioner_maximum_relative_shift=float(pre.shifts.numpy().max(initial=0.)))
