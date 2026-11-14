import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu

def assemble(blocks,ids,n):
 shape=blocks.shape
 return coo_matrix((blocks.ravel(),(np.broadcast_to(ids[:,:,None],shape).ravel(),np.broadcast_to(ids[:,None,:],shape).ravel())),shape=(n,n)).tocsc()

class BlockPreconditioner:
 def __init__(self,b,material,graph,h,free):
  n=b.x.numel();t=b.t.cpu().numpy();ids=(t[:,:,None]*3+np.arange(3)).reshape(-1,12)
  g=b.g.cpu().numpy().reshape(-1,4,3);j=b.j.cpu().numpy().reshape(-1,12)
  weight=(b.kd/(6*__import__('torch').linalg.det(b.dm))).cpu().numpy()
  gg=np.einsum('eik,ejk->eij',g,g);C=(np.einsum('eij,ab->eiajb',gg,np.eye(3))).reshape(-1,12,12)+j[:,:,None]*j[:,None,:]
  blocks=material.h.cpu().numpy()+C*weight[:,None,None]/h
  matrix=assemble(blocks,ids,n)+diags(np.repeat(b.mass.cpu().numpy().reshape(-1),3)/h**2)
  # Assemble J^T H J for active contact stencils, retaining cross-node blocks.
  blocks=graph.blocks.cpu().numpy();active=np.max(abs(blocks),axis=(1,2))>0
  ends=graph.ends.cpu().numpy()[active];blocks=blocks[active]
  if len(ends):
   emb=graph.ids.cpu().numpy()[ends];w=graph.w.cpu().numpy()[ends]
   # 4 endpoints, each embedded in 4 physical nodes; duplicated ids coalesce.
   J=np.zeros((len(ends),12,48))
   for a in range(4):
    for k in range(4):
     for axis in range(3):J[:,3*a+axis,12*a+3*k+axis]=w[:,a,k]
   physical=np.einsum('eia,eij,ejb->eab',J,blocks,J,optimize=True)
   ci=(emb[:,:,:,None]*3+np.arange(3)).reshape(-1,48)
   matrix+=assemble(physical,ci,n)
  self.free=(np.asarray(free)[:,None]*3+np.arange(3)).ravel();self.factor=splu(matrix[self.free][:,self.free].tocsc());self.n=n
 def solve(self,r):
  out=np.zeros(self.n);out[self.free]=self.factor.solve(r[self.free]);return out
