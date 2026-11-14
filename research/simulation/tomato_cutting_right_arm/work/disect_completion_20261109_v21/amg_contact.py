"""GPU multigrid preconditioner only; physical operator/residuals unchanged."""
from pathlib import Path
import sys,numpy as np
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'deps'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from factored_contact import FactoredContactBulk
import torch
class AMGContact(FactoredContactBulk):
 def precondition(self,r,h):
  if not hasattr(self,'amg_h') or self.amg_h!=h:self.build_amg(h)
  self.amg_input.copy_(r);self.amg_graph.replay();return self.amg_output.clone()
 def build_amg(self,h):
  from scipy.sparse import coo_matrix,diags,eye
  import pyamg
  from pyamg.util.linalg import approximate_spectral_radius
  z=self.z;t=z['tet_indices'];dm=z['tet_poses'];G=np.concatenate([-dm.sum(1)[:,None],dm],axis=1);weight=z['tet_damping']/(6*np.linalg.det(dm));local=weight[:,None,None]*(G@G.transpose(0,2,1));N=len(self.x)
  L=coo_matrix((local.ravel(),(np.broadcast_to(t[:,:,None],local.shape).ravel(),np.broadcast_to(t[:,None,:],local.shape).ravel())),shape=(N,N)).tocsr()
  scale=(z['particle_inv_mass']>0)/np.sqrt(z['physical_mass']);D=diags(scale);A=(eye(N)+h*D@L@D).tocsr()
  np.random.seed(3)
  ml=pyamg.smoothed_aggregation_solver(A,B=np.sqrt(z['physical_mass'])[:,None],symmetry='hermitian',max_coarse=40)
  def sparse(a):
   a=a.tocsr();return torch.sparse_csr_tensor(torch.tensor(a.indptr,device='cuda'),torch.tensor(a.indices,device='cuda'),torch.tensor(a.data,device='cuda'),size=a.shape)
  self.levels=[]
  for lev in ml.levels[:-1]:
   rho=approximate_spectral_radius(diags(1/lev.A.diagonal())@lev.A)
   self.levels.append((sparse(lev.A),sparse(lev.P),sparse(lev.R),torch.tensor((1.2/rho)/lev.A.diagonal(),device='cuda')[:,None]))
  self.coarse=torch.tensor(np.linalg.inv(ml.levels[-1].A.toarray()),device='cuda');self.amg_input=torch.zeros_like(self.x);self.amg_output=torch.zeros_like(self.x)
  def cycle(i,b):
   if i==len(self.levels):return self.coarse@b
   a,p,rt,d=self.levels[i];v=d*b
   v=v+d*(b-torch.sparse.mm(a,v))
   v=v+torch.sparse.mm(p,cycle(i+1,torch.sparse.mm(rt,b-torch.sparse.mm(a,v))))
   for _ in range(2):v=v+d*(b-torch.sparse.mm(a,v))
   return v
  self.amg_cycle=lambda b:cycle(0,b)
  def body():self.amg_output.copy_(self.amg_cycle(self.amg_input))
  stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
  with torch.cuda.stream(stream):body()
  torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize();self.amg_graph=torch.cuda.CUDAGraph()
  with torch.cuda.graph(self.amg_graph):body()
  self.amg_h=h
  print('AMG_LEVELS',[(a.shape[0],a._nnz()) for a,_,_,_ in self.levels],self.coarse.shape,flush=True)
