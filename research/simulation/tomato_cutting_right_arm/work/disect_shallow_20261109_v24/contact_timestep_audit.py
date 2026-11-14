from pathlib import Path
import sys,json,math,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_fracture_20261109_v23';sys.path.insert(0,str(V));sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from full_surface import FullSurface
from blade_contact import CADBlade
from interface_contact import InterfaceSampling
from scipy.interpolate import PchipInterpolator
s=FullSurface();cad=CADBlade();sam=InterfaceSampling(s.mesh,s);q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];p=json.loads((W/'correction_plan.json').read_text());a=np.array(p['front_lateral_path_m']);c=PchipInterpolator(a[:,0],a[:,1]);T=np.array(p['selected']['translation_m']);depth=p['downward_stroke_m'];direction=np.array(p['bodyward_direction_sim']);poses=[T+[c(d),-d,0] for d in np.linspace(0,depth,65)]+[T+[c(depth),-depth,0]+direction*f for f in np.linspace(0,p['horizontal_withdrawal_m'],65)];hit=np.zeros(len(sam.ids),bool)
for tr in poses:
 local=(q[sam.ids]-tr)@cad.rotation;hit|=np.all((local>=cad.minimum-.0001)&(local<=cad.maximum+.0001),axis=1)
ids=np.setdiff1d(sam.ids[hit],s.mesh['fixed']);minimum=float(s.mesh['mass'][ids].min());bound=.5*np.sqrt(minimum/2000.);h=min(3.125e-6,bound);sub=math.ceil(.0005/h);h=.0005/sub;out=dict(scope='Conservative sampled swept CAD AABB plus0.1mm inflation on settled geometry; not a deformation-independent proof',potential_nodes=len(ids),minimum_mass_kg=minimum,elastic_contact_dt_scale_s=float(bound),selected_dt_s=h,refined_dt_s=h/2,substeps_per_sample=sub)
(W/'contact_timestep_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
