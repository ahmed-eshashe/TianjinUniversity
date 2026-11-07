"""Accepted-interval remapping using the existing verified double CAD operator.

Same positive packet construction and force/energy convergence budgets as
host refresh. Independent host parity is checked separately; this is not a
new material model or a claim of cutting qualification.
"""
import numpy as np
import warp as wp
from tomato_cached_cad_pressure import CachedCADPressurePacket as CADPressurePacket
from tomato_host_fixed_pressure import packet_from_samples
from tomato_vectorized_material_coverage import padded_coverage

class PacketEvaluator:
 def __init__(self,blade,x,rotation,translation,com):
  self.blade=blade;self.x=wp.array(x,dtype=wp.vec3d);self.packet=CADPressurePacket(len(x));self.rotation=rotation;self.translation=translation;self.com=com
 def __call__(self,packet):
  p=self.packet;p.set_cad(vertices=self.blade['vertices'],triangles=self.blade['triangles'],**packet,rotation=self.rotation,translation=self.translation,com_local=self.com,source_scope='Accepted-state remap quadrature check')
  energy=p.evaluate(self.x)
  return dict(energy_j=float(energy),force_n=p.force.numpy(),body_wrench=p.reaction())

def refresh_packet(blade,cells,x,triangles,reference,rotation,translation,com,previous_packet,*,padding_m=1e-5):
 evaluate=PacketEvaluator(blade,x,rotation,translation,com);old=evaluate(previous_packet);vertices=np.asarray(blade['vertices'])@rotation.T+translation;last=None;history=[]
 for level in [2,3,4,5,6]:
  domain=padded_coverage(vertices,cells,x,triangles,reference,padding_m=padding_m,level=level,capacity=524288);packet=packet_from_samples(domain['samples']);value=evaluate(packet);scale=max(np.linalg.norm(value['force_n']),np.linalg.norm(old['force_n']),1e-12);energy_scale=max(abs(old['energy_j']),abs(value['energy_j']));force_old=float(np.linalg.norm(value['force_n']-old['force_n']));energy_old=float(value['energy_j']-old['energy_j']);force_step=None if last is None else float(np.linalg.norm(value['force_n']-last['force_n']));energy_step=None if last is None else float(abs(value['energy_j']-last['energy_j']));force_budget=.01*scale+1e-5;energy_budget=.01*energy_scale+1e-11;row=dict(level=level,samples=len(packet['areas']),force_difference_from_old_n=force_old,energy_jump_from_old_j=energy_old,successive_force_difference_n=force_step,successive_energy_difference_j=energy_step,force_budget_n=float(force_budget),energy_budget_j=float(energy_budget));history.append(row)
  if level>=4 and force_step<=force_budget and energy_step<=energy_budget and force_old<=force_budget and abs(energy_old)<=energy_budget:
   return packet,value,dict(passed=True,quadrature=history,energy_jump_j=energy_old,padding_m=padding_m,scope='Existing CAD operator remap; independently parity-tested. No work or cutting qualification.')
  last=value
 raise ValueError(('Material packet refresh lacks unchanged force/energy convergence',history))
