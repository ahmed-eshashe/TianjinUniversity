from cohesive_transfer import ROOT
import sys,numpy as np
sys.path.append('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages')
import warp as wp
from tomato_fast_mollified_contact import FastMollifiedEmbeddedSelfContact
class Closure:
 def __init__(self,source):
  s=source;m=s.mesh;x=m['x'];design=dict(nodes=[dict(position_m=p.tolist()) for p in x],cut_x_m=-.0225,pieces=[])
  for side in [-1,1]:
   owned=np.unique(m['tets'][m['tet_side']==side]);faces=m['boundary'][np.all(np.isin(m['boundary'],owned),axis=1)];design['pieces'].append(dict(side='left' if side<0 else 'right',surface_node_ids=np.unique(faces).tolist(),triangles=faces.tolist(),reference_interior_m=x[owned].mean(0).tolist()))
  wp.init();wp.set_device('cuda:0');self.engine=FastMollifiedEmbeddedSelfContact(dict(design=design,cells=m['tets'],x=x));self.physical=wp.array(x,dtype=wp.vec3)
 def force(self,q):
  e=self.engine;self.physical.assign(q);e.invalid.zero_();e.detect(self.physical);e.evaluate(self.physical,1/2400);wp.synchronize()
  if int(e.invalid.numpy()[0]):raise RuntimeError('Invalid cut-face contact geometry')
  return e.physical_force.numpy().copy()
