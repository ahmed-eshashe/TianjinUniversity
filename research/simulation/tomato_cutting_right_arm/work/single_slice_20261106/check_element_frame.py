from pathlib import Path
import sys,json
import numpy as np
import torch,warp as wp
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_native_full_model import registry
from tomato_element_frame_live import frame_support
from tomato_element_frame_objective import objective_force,incremental_objective_energy,commit_objective_history
wp.init();wp.set_device('cuda:0');d=registry();pairs,counts,coef,weights,models,supports=frame_support(d);patches=d['cohesion'].patches
sign=np.array([m['sign'] for m in models]);stiff=np.array([m['local_k'] for m in models]);law=np.array([[p['law'].stiffness_n_m,p['law'].onset_m,p['law'].failure_m] for p in patches])
args=[wp.array(pairs,dtype=wp.vec2i),wp.array(counts,dtype=int),wp.array(coef,dtype=wp.float64),wp.array(sign,dtype=wp.float64),wp.array(weights,dtype=wp.float64),wp.array(stiff,dtype=wp.mat33d),wp.array(law,dtype=wp.vec3d)]
def native(x,h,mask):
 xx=wp.array(x,dtype=wp.vec3d);hh=wp.array(h,dtype=wp.vec2d);ee=wp.array(mask,dtype=int);force=wp.zeros(len(x),dtype=wp.vec3d);energy=wp.zeros(47,dtype=wp.float64);mirror=wp.zeros(47,dtype=wp.vec2)
 wp.launch(objective_force,47,inputs=[xx,*args,hh,ee],outputs=[force]);wp.launch(incremental_objective_energy,47,inputs=[xx,*args,hh,ee],outputs=[energy]);wp.launch(commit_objective_history,47,inputs=[xx,*args,ee],outputs=[hh,mirror])
 return force.numpy(),energy.numpy().sum(),hh.numpy()
def reference(x,h,mask):
 xx=torch.tensor(x,dtype=torch.float64,requires_grad=True);total=xx.sum()*0
 for i in range(47):
  if h[i,1]>=1:continue
  pp=xx[pairs[i]];mid=pp.mean(1);uv=torch.tensor(coef[i].T)@mid;u,v=uv;t=u/torch.linalg.vector_norm(u);n=sign[i]*torch.linalg.cross(u,v);n=n/torch.linalg.vector_norm(n);b=torch.linalg.cross(n,t);gap=(pp[:,1]-pp[:,0])@torch.stack([n,t,b],1);gap=torch.cat([torch.clamp(gap[:,:1],min=0),gap[:,1:]],1);energy=.5*torch.sum(torch.tensor(weights[i])[:,None]*gap*(gap@torch.tensor(stiff[i])));kn,onset,failure=law[i];q=torch.sqrt(torch.clamp(2*energy/kn,min=1e-40));value=(1-h[i,1])*energy
  if mask[i] and q.item()>=h[i,0]:
   oldd=.5*kn*onset*failure/(failure-onset)*(min(failure,max(onset,h[i,0]))-onset)
   if q.item()>=failure:value=energy*0+.5*kn*onset*failure-oldd
   elif q.item()>onset:value=.5*kn*onset**2+kn*onset/(failure-onset)*(failure*(q-onset)-.5*(q*q-onset**2))-oldd
   else:value=energy-oldd
  total=total+value
 return -torch.autograd.grad(total,xx)[0].numpy(),float(total.detach())
z=np.load(w/'softening_replay03/stalled_solver.npz');cases=[('reference',d['x'],np.zeros((47,2)),np.ones(47,np.int32)),('captured_deformation',z['x'],z['history'],z['eligible'])];rows=[]
for name,x,h,mask in cases:
 f,e,hh=native(x,h,mask);fr,er=reference(x,h,mask);Q=Rotation.from_rotvec([.4,-.6,.2]).as_matrix();xr=x@Q.T+[.05,-.03,.02];ff,ee,hhh=native(xr,h,mask)
 row=dict(case=name,force_reference_error=float(abs(f-fr).max()),energy_reference_error=abs(e-er),net_force=float(np.linalg.norm(f.sum(0))),net_moment=float(np.linalg.norm(np.cross(x,f).sum(0))),rotation_force_error=float(abs(ff-f@Q.T).max()),rotation_energy_error=abs(ee-e),history_rotation_error=float(abs(hhh-hh).max()),ineligible_unchanged=bool(np.array_equal(hh[mask==0],h[mask==0])),irreversible=bool(np.all(hh>=h-1e-14)))
 row['passed']=all(row[k]<1e-8 for k in ['force_reference_error','net_force','net_moment','rotation_force_error']) and all(row[k]<1e-11 for k in ['energy_reference_error','rotation_energy_error','history_rotation_error']) and row['ineligible_unchanged'] and row['irreversible'];rows.append(row)
mid=z['x'][pairs[24]].mean(1);u,v=coef[24].T@mid;conditioning=float(np.linalg.norm(np.cross(u,v)));result=dict(passed=all(x['passed'] for x in rows),cases=rows,captured_patch24_frame_area_ratio=conditioning,scope='Volume-backed face frame: independent CPU gradients and rigid-motion invariance; not a completed slice or experimental validation')
(w/'element_frame_operator_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert result['passed']
