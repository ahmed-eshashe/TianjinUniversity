"""Positive tensile spring curvature added only to the search matrix.

For E=.5*k*(l-l0)^2 the exact spring Hessian has radial eigenvalue k
and tangential eigenvalue k*(1-l0/l). Retain its positive tangential
part in addition to the existing radial GN term. Compression remains the
existing positive GN approximation; exact forces and energy are unchanged.
"""
import warp as wp
from warp import sparse
from tomato_global_gn_assembly import GlobalGNAssembly,put_block
from tomato_tight_block import TightBlockCandidate

@wp.kernel(enable_backward=False)
def tensile_tangent_blocks(x:wp.array[wp.vec3d],pairs:wp.array[wp.vec2i],rest:wp.array[wp.float64],k:wp.array[wp.float64],free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 p,a,b=wp.tid();ids=pairs[p];v=x[ids[1]]-x[ids[0]];length=wp.length(v);h=wp.mat33d(0.)
 if length>rest[p] and length>wp.float64(1.e-8):
  normal=v/length;sgn=wp.float64(1.)
  if a!=b:sgn=wp.float64(-1.)
  h=sgn*k[p]*(wp.float64(1.)-rest[p]/length)*(wp.identity(n=3,dtype=wp.float64)-wp.outer(normal,normal))
 put_block(4*p+2*a+b,ids[a],ids[b],h,free,rows,cols,values)

class TangentGNAssembly(GlobalGNAssembly):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);ns=len(self.data['springs']);self.tangent_rows=wp.empty(4*ns,dtype=int);self.tangent_cols=wp.empty(4*ns,dtype=int);self.tangent_values=wp.empty(4*ns,dtype=wp.mat33d);self.tangent=sparse.bsr_zeros(self.n,self.n,block_type=wp.mat33d,device='cuda:0')
 def assemble(self,x,dt):
  counts=super().assemble(x,dt);ns=len(self.data['springs']);wp.launch(tensile_tangent_blocks,dim=(ns,2,2),inputs=[x,self.springs,self.s.relative_spring_rest,self.s.relative_spring_k,self.free],outputs=[self.tangent_rows,self.tangent_cols,self.tangent_values],block_dim=64);sparse.bsr_set_from_triplets(self.tangent,self.tangent_rows,self.tangent_cols,self.tangent_values);sparse.bsr_axpy(self.tangent,self.matrix,alpha=1.,beta=1.);return counts

class TangentCandidate(TightBlockCandidate):
 def __init__(self,holder,data,fixed,**kwargs):
  super().__init__(holder,data,fixed,**kwargs);self.assembly=TangentGNAssembly(holder,data,fixed)
