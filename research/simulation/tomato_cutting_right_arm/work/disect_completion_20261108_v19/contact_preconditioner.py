"""Axis-block contact coupling used only to accelerate the linear solve."""
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu
class CoupledAxes:
 def __init__(self,graph,mass,L,h,free):
  self.free=free;self.n=len(mass);blocks=graph.blocks.detach().cpu().numpy();ends=graph.ends.cpu().numpy();ids=graph.ids.cpu().numpy()[ends];w=graph.w.cpu().numpy()[ends];ci=ids.reshape(-1,16)
  active=np.max(abs(blocks),axis=(1,2))>0 if len(blocks) else np.zeros(0,bool)
  blocks=blocks[active];ci=ci[active];w=w[active];self.factors=[]
  for axis in range(3):
   matrix=diags(mass)+(h+1200*h*h)*L
   if len(blocks):
    block=blocks[:,axis::3,axis::3]
    physical=np.einsum('eij,eia,ejb->eiajb',block,w,w).reshape(-1,16,16)
    shape=physical.shape;C=coo_matrix((physical.ravel(),(np.broadcast_to(ci[:,:,None],shape).ravel(),np.broadcast_to(ci[:,None,:],shape).ravel())),shape=(self.n,self.n)).tocsc()
    matrix=matrix+h*h*C
   self.factors.append(splu(matrix[self.free][:,self.free].tocsc()))
 def solve(self,r,h):
  out=np.zeros_like(r)
  for a in range(3):out[self.free,a]=h*h*self.factors[a].solve(r[self.free,a])
  return out
