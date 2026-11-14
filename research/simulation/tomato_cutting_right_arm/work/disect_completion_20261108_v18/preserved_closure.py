from cohesive_transfer import ROOT
import sys,numpy as np
sys.path.append('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages')
import warp as wp
from tomato_fast_mollified_contact import FastMollifiedEmbeddedSelfContact
class Closure:
 def __init__(self,source):
  from pathlib import Path
  import tomato_embedded_self_contact as implementation
  W=Path(__file__).resolve().parent;m=dict(np.load(W.parent/'disect_precontact_20261108_v06/conforming_split.npz'));x=m['x']
  design=dict(nodes=[dict(position_m=p.tolist()) for p in x],cut_x_m=-.0225,pieces=[])
  for side in [-1,1]:
   owned=np.unique(m['tets'][m['tet_side']==side]);faces=m['boundary'][np.all(np.isin(m['boundary'],owned),axis=1)];design['pieces'].append(dict(side='left' if side<0 else 'right',surface_node_ids=np.unique(faces).tolist(),triangles=faces.tolist(),reference_interior_m=x[owned].mean(0).tolist()))
  embedding=dict(np.load(W/'preserved_contact_embedding.npz'));original=implementation.build_embedding
  wp.init();wp.set_device('cuda:0')
  try:
   implementation.build_embedding=lambda *args,**kwargs:embedding
   self.engine=FastMollifiedEmbeddedSelfContact(dict(design=design,cells=source.mesh['tets'],x=source.mesh['x']))
  finally:implementation.build_embedding=original
  self.physical=wp.array(source.mesh['x'],dtype=wp.vec3)

 def force(self,q):
  e=self.engine;self.physical.assign(q);e.invalid.zero_();e.detect(self.physical);e.evaluate(self.physical,1/2400);wp.synchronize()
  if int(e.invalid.numpy()[0]):raise RuntimeError('Invalid cut-face contact geometry')
  return e.physical_force.numpy().copy()

 def energy_force_precise(self,q):
  from tomato_fast_mollified_contact import current_contact_fast
  e=self.engine;self.physical.assign(q);e.invalid.zero_();e.detect(self.physical)
  embedding=e.embedding;precise=np.einsum('ni,nij->nj',embedding['weights'],q[embedding['indices']]);e.precise_position.assign(precise)
  e.force.zero_();e.hessian.zero_();e.physical_force.zero_();e.physical_hessian.zero_();e.contact_energy.zero_()
  wp.launch(current_contact_fast,dim=e.stencil_capacity,inputs=[e.precise_position,e.physical_ids,e.endpoint_weight,e.endpoint,e.kind,e.mollifier_threshold,e.stencil_count,e.stencil_capacity,wp.float64(e.margin),wp.float64(e.model.soft_contact_ke)],outputs=[e.physical_force,e.physical_hessian,e.force,e.hessian,e.contact_energy,e.invalid]);wp.synchronize()
  if int(e.invalid.numpy()[0]):raise RuntimeError('Invalid precise closure geometry')
  return float(e.contact_energy.numpy()[0]),e.physical_force.numpy().copy()
