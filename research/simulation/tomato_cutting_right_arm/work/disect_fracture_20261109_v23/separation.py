"""Material connectivity evaluator, independent of visible gaps and blade pose."""
import numpy as np
class SeparationEvaluator:
 def __init__(self,source):
  self.s=source;self.m=source.mesh;self.n=len(self.m['x']);self.mass=self.m['mass'];self.t=self.m['tets'];self.side_nodes=[np.unique(self.t[self.m['tet_side']==side]) for side in [-1,1]];self.expected_mass=np.array([self.mass[a].sum() for a in self.side_nodes]);self.group_nodes=[]
  group=source.group.cpu().numpy();li=source.li.cpu().numpy();ri=source.ri.cpu().numpy();ai=source.ai.cpu().numpy();bi=source.bi.cpu().numpy()
  for g in range(47):self.group_nodes.append(np.unique(np.r_[li[group==g].ravel(),ri[group==g].ravel(),ai[g].ravel(),bi[g].ravel()]))
 def evaluate(self,history,positions=None):
  h=np.asarray(history);on=self.s.on.cpu().numpy();fail=self.s.fail.cpu().numpy();canonical=np.where(h[:,0]<=on,0,np.where(h[:,0]>=fail,1,fail*(h[:,0]-on)/(np.maximum(h[:,0],1e-300)*(fail-on))))
  if h.shape!=(47,2) or not np.isfinite(h).all() or np.max(abs(canonical-h[:,1]))>1e-10:raise ValueError('Canonical finite history required')
  parent=np.arange(self.n)
  def find(a):
   while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
   return a
  def join(a,b):
   a=find(int(a));b=find(int(b))
   if a!=b:parent[b]=a
  for t in self.t:
   for b in t[1:]:join(t[0],b)
  live=np.flatnonzero(h[:,1]<1)
  for g in live:
   ids=self.group_nodes[g]
   for b in ids[1:]:join(ids[0],b)
  labels=np.array([find(a) for a in range(self.n)]);ids=np.unique(labels);masses=np.array([self.mass[labels==a].sum() for a in ids]);membership=[]
  for side in self.side_nodes:membership.append(np.unique(labels[side]))
  intended=bool(all(len(a)==1 for a in membership) and membership[0][0]!=membership[1][0]);mass_conserved=bool(np.isclose(masses.sum(),self.mass.sum(),atol=1e-14,rtol=1e-12));two=bool(len(ids)==2 and intended and np.allclose(np.sort(masses),np.sort(self.expected_mass),atol=1e-14,rtol=1e-12));substantial=bool(np.all(self.expected_mass>.01*self.mass.sum()));return dict(surviving_group_ids=live.tolist(),component_count=len(ids),component_masses_kg=masses.tolist(),expected_piece_masses_kg=self.expected_mass.tolist(),mass_conserved=mass_conserved,intended_piece_membership=intended,substantial_pieces=substantial,separation_passed=bool(len(live)==0 and two and substantial and mass_conserved))
