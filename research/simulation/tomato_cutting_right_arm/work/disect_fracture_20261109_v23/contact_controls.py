from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from blade_contact import CADBlade,law
from full_surface import FullSurface
from interface_contact import InterfaceSampling
s=FullSurface();a=InterfaceSampling(s.mesh,s);cad=CADBlade();q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];v=np.zeros_like(q);p=json.loads((W.parent/'disect_physical_20261109_v22/indent_plan.json').read_text());T=np.array(p['initial_translation_m']);pairs=s.mesh['ties'];rows=[]
for depth in [0.,.00006,.003,.01,.02,.03,.04]:
 t=T-[0,depth,0];b=a.evaluate(cad,q,v,t,np.zeros(3));query=cad.query(q[a.ids],t);ind=np.zeros_like(q);ind[a.ids]=law(query['phi'],query['normal'],v[a.ids],np.zeros(3),kd=0.)
 balance=float(np.linalg.norm(b['reaction']+b['force'].sum(0)));error=float(np.max(abs(ind-b['force'])));outer=cad.evaluate(q,v,a.outer,t,np.zeros(3));retained=float(np.max(abs(b['force'][a.outer]-outer['force'][a.outer])));coverage=int(np.count_nonzero(np.linalg.norm(b['force'][a.cut],axis=1)));e=s.eligibility_from_contact(b['force']);rows.append(dict(depth_m=depth,force_reference_error_N=error,reaction_balance_error_N=balance,old_outer_force_error_N=retained,contacted_interface_nodes=coverage,eligible_groups=int(e.sum()),passed=bool(error<1e-12 and balance<1e-12 and retained<1e-12)))
# No duplicated evaluation for a physical node; twins are distinct DOFs.
unique=len(a.ids)==len(np.unique(a.ids));coverage=np.isin(a.cut,a.ids).all();zero=rows[0]['contacted_interface_nodes']==0
# Nonfracturing saved probes keep original results when expanded nodes remain clear.
old=np.load(W.parent/'disect_physical_20261109_v22/indent_trajectory.npz');probe_equal=[]
for k in [0,12,30,50,70,90]:
 t=float(old['t'][k]);ramp=lambda u:10*u**3-15*u**4+6*u**5
 if t<=.015:tr=T+[0,-60e-6*ramp(t/.015),0]
 elif t<=.035:tr=T+[0,-60e-6,0]+np.array(p['bodyward_direction_sim'])*p['horizontal_withdrawal_m']*ramp((t-.015)/.020)
 else:tr=T+[0,-60e-6,0]+np.array(p['bodyward_direction_sim'])*p['horizontal_withdrawal_m']
 aa=a.evaluate(cad,old['x'][k],old['v'][k],tr,np.zeros(3));bb=cad.evaluate(old['x'][k],old['v'][k],a.outer,tr,np.zeros(3));probe_equal.append(float(np.max(abs(aa['force']-bb['force']))))
# SDF work gradient at a smooth active cut node with zero velocity/friction.
t=T-[0,.04,0];query=cad.query(q[a.cut],t);candidates=np.where(query['phi']< -1e-6)[0];i=int(candidates[np.argmax(-query['phi'][candidates])]);point=q[a.cut[i]];n=query['normal'][i];eps=1e-8
phi=cad.query(np.array([point+eps*n,point-eps*n]),t)['phi'];energy=.5*2000*np.minimum(phi,0)**2;deriv=(energy[0]-energy[1])/(2*eps);f=law(np.array([query['phi'][i]]),n[None],np.zeros((1,3)),np.zeros(3),kd=0.)[0];derivative_error=abs(deriv+f@n)
# Opposing bank diagnostics on the current settled shape; do not manufacture normals.
f=a.evaluate(cad,q,v,t,np.zeros(3))['force'];both=(np.linalg.norm(f[pairs[:,0]],axis=1)>0)&(np.linalg.norm(f[pairs[:,1]],axis=1)>0);dots=np.sum(f[pairs[both,0]]*f[pairs[both,1]],axis=1)
out=dict(scope='Expanded exact CAD nodal sampling controls; static fixtures, no dynamic cutting qualification',user_authorized=True,unique_physical_nodes=unique,all_interface_nodes_covered=bool(coverage),no_false_initial_interface_contact=zero,old_probe_max_force_difference_N=max(probe_equal),energy_gradient_error_N=float(derivative_error),rows=rows,coincident_bank_note={'both_banks_contacted':int(both.sum()),'opposite_force_pairs':int((dots<0).sum()),'same_force_pairs':int((dots>0).sum()),'meaning':'Exact CAD normals retained; initial plane/CAD alignment must be checked before shallow trajectory.'},passed=bool(unique and coverage and zero and all(r['passed'] for r in rows) and max(probe_equal)<1e-12 and derivative_error<1e-6))
(W/'contact_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
