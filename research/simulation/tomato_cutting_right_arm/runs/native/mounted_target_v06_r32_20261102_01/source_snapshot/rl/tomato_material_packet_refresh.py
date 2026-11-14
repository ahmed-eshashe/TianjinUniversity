"""Host positive material-packet refresh with explicit quadrature jump gates.

Call ONLY between accepted physical intervals. Coordinates/areas remain
fixed throughout each nonlinear solve. No material or contact law is changed.
Refresh is refused if either the old packet or successive new refinements
disagree beyond the original host force/energy quadrature budgets.
"""
import numpy as np
from tomato_padded_material_coverage import padded_coverage
from tomato_host_fixed_pressure import packet_from_samples,evaluate_fixed

def refresh_packet(blade,cells,x,triangles,reference,rotation,translation,com,previous_packet):
 old=evaluate_fixed(blade,x,previous_packet,rotation,translation,com);vertices=np.asarray(blade['vertices'])@rotation.T+translation;last=None;history=[]
 for level in [2,3,4,5]:
  domain=padded_coverage(vertices,cells,x,triangles,reference,padding_m=1e-5,level=level);packet=packet_from_samples(domain['samples']);value=evaluate_fixed(blade,x,packet,rotation,translation,com);scale=max(np.linalg.norm(value['force_n']),np.linalg.norm(old['force_n']),1e-12);energy_scale=max(abs(old['energy_j']),abs(value['energy_j']));force_old=float(np.linalg.norm(value['force_n']-old['force_n']));energy_old=float(value['energy_j']-old['energy_j']);force_step=None if last is None else float(np.linalg.norm(value['force_n']-last['force_n']));energy_step=None if last is None else float(abs(value['energy_j']-last['energy_j']));force_budget=.01*scale+1e-5;energy_budget=.01*energy_scale+1e-11;row=dict(level=level,samples=len(packet['areas']),force_difference_from_old_n=force_old,energy_jump_from_old_j=energy_old,successive_force_difference_n=force_step,successive_energy_difference_j=energy_step,force_budget_n=float(force_budget),energy_budget_j=float(energy_budget));history.append(row)
  if level>=4 and force_step<=force_budget and energy_step<=energy_budget and force_old<=force_budget and abs(energy_old)<=energy_budget:
   return packet,value,dict(passed=True,quadrature=history,energy_jump_j=energy_old,padding_m=1e-5,scope='Accepted-interval host packet refresh only; no work/physics/CCD qualification. Original force/energy quadrature gates retained.')
  last=value
 raise ValueError(('Material packet refresh lacks unchanged force/energy convergence',history))
