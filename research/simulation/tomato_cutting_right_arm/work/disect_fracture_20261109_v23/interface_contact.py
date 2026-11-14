"""User-approved expanded node sampling, unchanged exact CAD law and coefficients.
Both physical banks are retained; repeated references to one physical node are unique.
No damage, force, eligibility or geometry is invented from commanded depth/time.
"""
import numpy as np
class InterfaceSampling:
 def __init__(self,mesh,source):
  outer=np.unique(mesh['outer']);cut=np.unique(np.r_[source.li.cpu().numpy().ravel(),source.ri.cpu().numpy().ravel()]);self.ids=np.union1d(outer,cut);self.outer=outer;self.cut=cut
 def evaluate(self,cad,q,v,translation,velocity):return cad.evaluate(q,v,self.ids,translation,velocity)
