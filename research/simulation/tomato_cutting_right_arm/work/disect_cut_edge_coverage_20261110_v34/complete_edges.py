"""Candidate correction: include cut-to-cut physical tetrahedron edges.

Every cut vertex owns exactly one contact-sampling budget, distributed over all
of its incident physical edges. Shared edges are integrated once with summed
ownership weights. No cohesive/tie edge is added; no cross-bank attachment.
The existing CAD law, quadrature and full two-endpoint force pullback are reused.
"""
from pathlib import Path
import sys,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_adaptive_contact_20261109_v27'))
from adaptive_contact import AdaptiveContact
class CompleteCutEdges(AdaptiveContact):
 def __init__(self,mesh,force_atol=1e-10,rtol=1e-6,max_depth=40):
  raw=np.concatenate([mesh['tets'][:,[i,j]] for i in range(4) for j in range(i)])
  raw=np.unique(np.sort(raw,axis=1),axis=0);self.cut=np.unique(mesh['ties']);mask=np.zeros(len(mesh['x']),bool);mask[self.cut]=True
  self.edges=raw[np.any(mask[raw],axis=1)].copy();swap=mask[self.edges[:,0]]&~mask[self.edges[:,1]];self.edges[swap]=self.edges[swap,::-1]
  self.owner_degree=np.bincount(self.edges.ravel(),minlength=len(mask));self.owner_inverse_degree=np.zeros(len(mask));self.owner_inverse_degree[self.cut]=1/self.owner_degree[self.cut]
  self.edge_weights=self.owner_inverse_degree[self.edges].sum(1)
  self.outer=np.setdiff1d(np.unique(mesh['outer']),self.cut);self.force_atol=force_atol;self.rtol=rtol;self.max_depth=max_depth
