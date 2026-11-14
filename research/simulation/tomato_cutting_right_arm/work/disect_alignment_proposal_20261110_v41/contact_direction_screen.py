"""Frozen-geometry screen only: penetrated fixtures are NOT physical episodes."""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1]
for name in ['disect_batched_contact_20261110_v39','disect_precision_sign_20261110_v38','disect_execution_strategy_20261110_v35']:sys.path.insert(0,str(W.parent/name))
from batched_contact import BatchedContact
from precision_query import precise_query
import tomato_compiled_blade_query as backend,numba
numba.set_num_threads(4);backend._query=precise_query
from scipy.interpolate import PchipInterpolator
m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];side=np.zeros(len(q),int);side[m['tets'].ravel()]=np.repeat(m['tet_side'],4);c=BatchedContact(m);p=json.loads((W/'pose_proposal.json').read_text());plan=json.loads((W.parent/'disect_batched_cutting_20261110_v40/correction_plan.json').read_text());curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T);ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rot=A.T@ref['rotation'];raw=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());v=np.array(raw['vertices']);f=np.array(raw['triangles']);rows=[]
for depth in [.001,.003,.005]:
 for label,Rc,T0 in [('original',rot,plan['selected']['translation_m']),('aligned',np.array(p['proposed_CAD_rotation']),p['proposed_translation_m'])]:
  T=np.array(T0)+[float(curve(depth)),-depth,0];ev=c.evaluate(q,np.zeros_like(q),v@Rc.T+T,f,np.zeros(3),T,ke=2e6,kd=0);load=2e6*ev['weights']*np.maximum(-ev['phi'],0);bank=side[ev['ids'][:,0]];lat=abs(ev['normal'][:,0])>.9;bb={}
  for s in [-1,1]:
   k=bank==s;outward=ev['normal'][:,0]*s>0;bb[str(s)]={'lateral_outward_normal_load_N':float(load[k&lat&outward].sum()),'lateral_inward_normal_load_N':float(load[k&lat&~outward].sum()),'normal_force_vector_N':(load[k,None]*ev['normal'][k]).sum(0).tolist()}
  rows.append({'depth_m':depth,'pose':label,'banks':bb,'max_sample_overlap_m':float(np.maximum(-ev['phi'],0).max()) if len(load) else 0})
out={'scope':'Read-only penetrated FROZEN initial-material fixtures for contact-direction screening. No history, dynamics, physical admissibility or causal/cutting pass. High static forces are not safe cutting loads.','rows':rows};(W/'direction_screen.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
