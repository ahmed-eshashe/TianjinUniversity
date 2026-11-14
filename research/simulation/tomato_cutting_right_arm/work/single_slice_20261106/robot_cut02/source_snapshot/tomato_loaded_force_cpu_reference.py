"""CPU autograd of the full intact loaded potential; independent force formulas.

Contact closest features come from independent CPU geometric minimization.
Differentiation uses raw positive embedding weights, not native cached force
scatter coefficients. Envelope derivatives hold the minimizing barycentrics.
"""
import argparse,json
from pathlib import Path
import numpy as np
import torch
from tomato_global_gn_cpu_reference import closest_point_triangle,closest_edges

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=np.load(a.input);torch.set_num_threads(1);x=torch.tensor(d['x'],dtype=torch.float64,requires_grad=True)
 def T(v):return torch.tensor(v,dtype=torch.float64)
 if np.any(d['history'])or np.any(d['eligible']):raise ValueError('This loaded gradient diagnostic is intact only')
 ids=d['spring_pairs'];length=torch.linalg.vector_norm(x[ids[:,1]]-x[ids[:,0]],dim=1);spring=.5*torch.sum(T(d['spring_k'])*(length-T(d['spring_rest']))**2);q=x[d['cells']];aa=q[:,1]-q[:,0];bb=q[:,2]-q[:,0];cc=q[:,3]-q[:,0];J=torch.sum(aa*torch.linalg.cross(bb,cc),dim=1)/(6*T(d['volumes']));active=J.detach().numpy()<.5;r=(J[active]-.1)/.4;volume=torch.sum(10000*T(d['volumes'][active])*(r-1-torch.log(r)));bulk=spring+volume;cohesion=x.sum()*0
 for i,count in enumerate(d['cohesive_counts']):
  pairs=d['cohesive_pairs'][i,:count];paired=x[pairs];mid=paired.mean(1);a0,b0,c0=d['anchors'][i];u=mid[b0]-mid[a0];v=mid[c0]-mid[a0];t=u/torch.linalg.vector_norm(u);n=d['sign'][i]*torch.linalg.cross(u,v);n=n/torch.linalg.vector_norm(n);frame=torch.stack([n,t,torch.linalg.cross(n,t)],dim=1);gap=(paired[:,1]-paired[:,0])@frame;gap=torch.cat([torch.clamp(gap[:,:1],min=0),gap[:,1:]],dim=1);cohesion+=.5*torch.sum(T(d['weights'][i,:count,None])*gap*(gap@T(d['local_k'][i])))
 proxy=torch.sum(x[d['embedding_ids']]*T(d['embedding_weights'])[:,:,None],dim=1);px=proxy.detach().numpy();selected=[];coeffs=[];minimum_distance=float('inf');minimum_record=-1;radius=float(d['radius'][0]);stiffness=float(d['contact_k'][0])
 for i,end in enumerate(d['endpoint']):
  p0,p1,p2,p3=px[end]
  if d['kind'][i]==0:c=np.r_[1.,-closest_point_triangle(p0,p1,p2,p3)]
  else:s,t=closest_edges(p0,p1,p2,p3);c=np.array([1-s,s,-1+t,-t])
  distance_np=float(np.linalg.norm(c@px[end]))
  if distance_np<minimum_distance:minimum_distance=distance_np;minimum_record=i
  if distance_np<radius:selected.append(i);coeffs.append(c)
 contact=x.sum()*0
 if selected:
  selected=np.array(selected,dtype=int);p0=proxy[d['endpoint'][selected]];delta=torch.sum(p0*T(np.array(coeffs))[:,:,None],dim=1);distance=torch.linalg.vector_norm(delta,dim=1);tau=radius/2;minimum=1e-5;k2=tau*tau*stiffness;quadratic=.5*stiffness*(radius-distance)**2;logarithmic=.5*k2-k2*torch.log(distance/tau);gap=distance-minimum;continued=.5*k2-k2*np.log(minimum/tau)-k2/minimum*gap+.5*k2/minimum**2*gap**2;value=torch.where(distance>=tau,quadratic,torch.where(distance>minimum,logarithmic,continued));m=torch.ones_like(distance);edge=d['kind'][selected]!=0
  if edge.any():
   u=p0[edge,1]-p0[edge,0];v=p0[edge,3]-p0[edge,2];cross=torch.linalg.cross(u,v);squared=torch.sum(cross*cross,dim=1);eps=T(d['threshold'][selected[edge]]);ratio=squared/eps;m[edge]=torch.where(squared<eps,ratio*(2-ratio),torch.ones_like(ratio))
  contact=torch.sum(m*value)
 gravity=-torch.sum(T(d['mass'])[:,None]*T(d['gravity'])[None,:]*(x-T(d['source_sim'])));board=.5*torch.sum(T(d['board_k'])*torch.clamp(float(d['board_height'][0])-x[:,2],min=0)**2);energies={'bulk':bulk,'cohesion':cohesion,'contact':contact,'gravity_board':gravity+board};forces={name:-torch.autograd.grad(value,x,retain_graph=True)[0].detach().numpy()for name,value in energies.items()};total=sum(forces.values());free=d['free'].astype(bool);total[~free]=0;actuals={'bulk':d['native_bulk_force'],'cohesion':d['native_cohesive_force'],'contact':d['native_contact_force'],'total_free':d['native_rhs']};forces['total_free']=total;errors={}
 for key,actual in actuals.items():
  ref=forces[key];absolute=float(abs(ref-actual).max());relative=float(np.linalg.norm(ref-actual)/max(np.linalg.norm(ref),1e-12));errors[key]=dict(maximum_absolute_error_n=absolute,relative_error=relative,within_budget=bool(absolute<=1e-8 or relative<=1e-6))
 energy_total=sum(float(e.detach())for e in energies.values());energy_error=abs(energy_total-float(d['native_energy'][0]));passed=all(e['within_budget']for e in errors.values())and(energy_error<=1e-10 or energy_error/max(abs(energy_total),1e-12)<=1e-9);a.output.write_text(json.dumps(dict(passed=bool(passed),errors=errors,cpu_active_contacts=len(selected),minimum_query_distance_m=minimum_distance,minimum_query_kind=int(d['kind'][minimum_record]),energy_error_j=energy_error,cpu_force_l1_n=float(np.linalg.norm(total,axis=1).sum()),cpu_maximum_force_acceleration_m_s2=float((np.linalg.norm(total,axis=1)/d['mass']).max()),scope='Independent full loaded CPU-autograd energy gradient and raw-embedding contact scatter versus native forces. Intact posed operators only, no equilibrium, dynamics or cutting pass.'),indent=2)+'\n');return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
