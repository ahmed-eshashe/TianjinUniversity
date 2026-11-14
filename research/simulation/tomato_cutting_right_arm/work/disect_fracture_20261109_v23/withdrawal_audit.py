from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from blade_contact import CADBlade
from full_surface import FullSurface
from interface_contact import InterfaceSampling
s=FullSurface();cad=CADBlade();sam=InterfaceSampling(s.mesh,s);q=np.load(W/'shallow_checkpoint.npz')['x'];p=json.loads((W/'shallow_plan.json').read_text());base=np.array(p['selected']['translation_m'])-[0,p['downward_stroke_m'],0];d=np.array(p['bodyward_direction_sim']);axis=cad.rotation[:,0].copy();axis[1]=0;axis/=np.linalg.norm(axis)
if axis@d<0:axis=-axis
normal=cad.rotation[:,2];rows=[]
for f in [0,.006,.01,.02,.04,.06,.08]:
 tr=base+f*d;ev=sam.evaluate(cad,q,np.zeros_like(q),tr,np.zeros(3));rows.append(dict(displacement_m=f,static_active_nodes=ev['active_nodes'],static_penetration_m=ev['maximum_penetration_m']))
out=dict(scope='Read-only frozen-shape withdrawal geometry audit; not a dynamic result',bodyward_direction=d.tolist(),horizontal_blade_length_direction_toward_body=axis.tolist(),bodyward_dot_blade_length=float(d@axis),bodyward_dot_blade_face_normal=float(abs(d@normal)),samples=rows,interpretation='Bodyward is predominantly across blade thickness, not along its length. Static intersections along the route are diagnostics, not proof of dynamic outcome.');(W/'withdrawal_audit_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
