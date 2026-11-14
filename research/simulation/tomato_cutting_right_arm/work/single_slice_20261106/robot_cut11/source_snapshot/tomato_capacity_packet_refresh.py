"""Adaptive positive quadrature over the unchanged padded CAD/material domain.

Compare each leaf's three-point rule with its four children. Use the original
assembled-force/energy convergence test with a fourfold internal margin;
local absolute errors select where to refine.
No contact law, material area, geometry or old/new remap budget is changed.
"""
import numpy as np
from tomato_vectorized_material_coverage import padded_coverage
from tomato_capacity_packet_evaluator import PacketEvaluator

G=np.full((3,3),1/6);np.fill_diagonal(G,2/3)
GI=np.linalg.inv(G)
F=np.sqrt(2.)-1.
CHILD_AREA=np.array([F*(1-F)]*3+[1-3*F*(1-F)])

def split(c):
 a,b,d=c[:,0],c[:,1],c[:,2];ab=(1-F)*a+F*b;bd=(1-F)*b+F*d;da=(1-F)*d+F*a
 return np.stack([np.stack([a,ab,da],1),np.stack([ab,b,bd],1),np.stack([da,bd,d],1),np.stack([ab,bd,da],1)],1)

def packet(ids,cells,reference,areas):
 bary=(G@cells).reshape(-1,3);bary=np.maximum(bary,0);bary/=bary.sum(1)[:,None]
 return dict(indices=np.repeat(ids,3,axis=0),barycentric=bary,areas=np.repeat(areas/3,3)),areas

def evaluate_cells(evaluator,ids,cells,reference,areas):
 p,areas=packet(ids,cells,reference,areas);result=evaluator(p)
 sample=evaluator.packet.sample_force.numpy().reshape(-1,3,3);bary=p['barycentric'].reshape(-1,3,3)
 nodal=np.einsum('lqa,lqi->lai',bary,sample)
 energies=evaluator.packet.energy.numpy().reshape(-1,3).sum(1)
 return p,result,nodal,energies,areas

def refresh_packet(blade,cells,x,triangles,reference,rotation,translation,com,previous_packet,*,padding_m=1e-5,maximum_samples=4194304,lookahead=None):
 evaluate=PacketEvaluator(blade,x,rotation,translation,com);old=evaluate(previous_packet)
 feature_ids=set(evaluate.packet.face.numpy().tolist()) if evaluate.packet.count else set()
 future=None if lookahead is None else PacketEvaluator(blade,lookahead[0],rotation if len(lookahead)==2 else lookahead[2],lookahead[1],com)
 domain=padded_coverage(np.asarray(blade['vertices'])@rotation.T+translation,cells,x,triangles,reference,padding_m=padding_m,level=0)
 samples=domain['samples']
 if not samples:
  p=dict(indices=np.empty((0,3),np.int32),barycentric=np.empty((0,3)),areas=np.empty(0));value=evaluate(p)
  if np.linalg.norm(old['force_n'])>1e-5 or abs(old['energy_j'])>1e-11:raise ValueError('Empty remap disagrees with previous contact')
  return p,value,dict(passed=True,samples=0,energy_jump_j=-old['energy_j'])
 ids=np.array([q['corners'] for q in samples],np.int32)[::3];b=np.array([q['barycentric'] for q in samples]).reshape(-1,3,3);leaves=GI@b
 if leaves.min()<-1e-12:raise ValueError('Invalid reconstructed material leaf')
 leaves=np.maximum(leaves,0);leaves/=leaves.sum(2)[:,:,None];depth=np.zeros(len(leaves),int);history=[];leaf_areas=np.array([q['area_m2'] for q in samples]).reshape(-1,3).sum(1)
 # Add observed exact CAD features at the new domain before partitioning.
 _,_,_,_,_=evaluate_cells(evaluate,ids,leaves,reference,leaf_areas)
 feature_ids.update(evaluate.packet.face.numpy().tolist())
 if future is not None:
  evaluate_cells(future,ids,leaves,reference,leaf_areas);feature_ids.update(future.packet.face.numpy().tolist())
 from tomato_compiled_plane_partition import partition
 ids,leaves,leaf_areas,partition_report=partition(blade,ids,leaves,leaf_areas,x,rotation,translation,sorted(feature_ids))
 if lookahead is not None:
  ids,leaves,leaf_areas,future_partition=partition(blade,ids,leaves,leaf_areas,lookahead[0],rotation if len(lookahead)==2 else lookahead[2],lookahead[1],sorted(feature_ids));partition_report['lookahead']=future_partition
 depth=np.zeros(len(leaves),int)
 for iteration in range(12):
  if 12*len(leaves)>maximum_samples:raise ValueError(('Adaptive quadrature capacity',len(leaves),maximum_samples))
  low,lv,lf,le,area=evaluate_cells(evaluate,ids,leaves,reference,leaf_areas)
  children=split(leaves).reshape(-1,3,3);child_ids=np.repeat(ids,4,axis=0)
  high,hv,hf,he,_=evaluate_cells(evaluate,child_ids,children,reference,(leaf_areas[:,None]*CHILD_AREA).ravel())
  ferr=np.linalg.norm((hf.reshape(-1,4,3,3).sum(1)-lf).reshape(-1,9),axis=1);eerr=abs(he.reshape(-1,4).sum(1)-le)
  fbudget=.01*max(np.linalg.norm(hv['force_n']),np.linalg.norm(old['force_n']),1e-12)+1e-5;ebudget=.01*max(abs(hv['energy_j']),abs(old['energy_j']))+1e-11
  global_fe=float(np.linalg.norm(hv['force_n']-lv['force_n']));global_ee=float(abs(hv['energy_j']-lv['energy_j']))
  if future is not None:
   _,flv,flf,fle,_=evaluate_cells(future,ids,leaves,reference,leaf_areas)
   _,fhv,fhf,fhe,_=evaluate_cells(future,child_ids,children,reference,(leaf_areas[:,None]*CHILD_AREA).ravel())
   future_fb=.01*max(np.linalg.norm(fhv['force_n']),1e-12)+1e-5;future_eb=.01*abs(fhv['energy_j'])+1e-11
   future_fe=np.linalg.norm((fhf.reshape(-1,4,3,3).sum(1)-flf).reshape(-1,9),axis=1);future_ee=abs(fhe.reshape(-1,4).sum(1)-fle)
   global_fe=max(global_fe,float(np.linalg.norm(fhv['force_n']-flv['force_n']))*fbudget/future_fb);global_ee=max(global_ee,float(abs(fhv['energy_j']-flv['energy_j']))*ebudget/future_eb)
   ferr=np.maximum(ferr,future_fe*fbudget/future_fb);eerr=np.maximum(eerr,future_ee*ebudget/future_eb)
  old_f=float(np.linalg.norm(hv['force_n']-old['force_n']));old_e=float(hv['energy_j']-old['energy_j'])
  row=dict(iteration=iteration,leaves=len(leaves),samples=len(high['areas']),maximum_depth=int(depth.max()),global_force_error_n=global_fe,global_energy_error_j=global_ee,summed_force_error_n=float(ferr.sum()),summed_energy_error_j=float(eerr.sum()),force_budget_n=float(fbudget),energy_budget_j=float(ebudget),force_difference_from_old_n=old_f,energy_jump_from_old_j=old_e);history.append(row)
  if ferr.sum()<=.25*fbudget and eerr.sum()<=.25*ebudget:
   if old_f>fbudget or abs(old_e)>ebudget:raise ValueError(('Converged adaptive remap differs from old packet',history))
   return high,hv,dict(passed=True,quadrature=history,partition=partition_report,energy_jump_j=old_e,padding_m=padding_m,scope='Adaptive positive material quadrature; unchanged conservative remap error budgets')
  share=area/area.sum();refine=(ferr>.25*fbudget*share)|(eerr>.25*ebudget*share)
  if not refine.any():raise ValueError('Adaptive estimator failed to select refinement')
  if np.any(depth[refine]>=10):raise ValueError(('Adaptive depth limit',history))
  leaf_areas=np.concatenate([leaf_areas[~refine],(leaf_areas[refine,None]*CHILD_AREA).ravel()])
  leaves=np.concatenate([leaves[~refine],split(leaves[refine]).reshape(-1,3,3)])
  ids=np.concatenate([ids[~refine],np.repeat(ids[refine],4,axis=0)]);depth=np.concatenate([depth[~refine],np.repeat(depth[refine]+1,4)])
 raise ValueError(('Adaptive quadrature failed unchanged convergence budgets',history))
