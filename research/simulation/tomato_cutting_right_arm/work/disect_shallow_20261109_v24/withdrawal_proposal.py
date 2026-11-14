from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'));sys.path.insert(0,str(W.parent/'disect_fracture_20261109_v23'))
from full_surface import FullSurface
from blade_contact import CADBlade
from interface_contact import InterfaceSampling
s=FullSurface();sam=InterfaceSampling(s.mesh,s);cad=CADBlade();q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];p=json.loads((W/'correction_plan.json').read_text());T=np.array(p['selected']['translation_m'])+[p['front_lateral_path_m'][-1][1],-p['downward_stroke_m'],0];d=np.array(p['bodyward_direction_sim']);axis=cad.rotation[:,0].copy();axis[1]=0;axis/=np.linalg.norm(axis)
if axis@d<0:axis=-axis
rows=[]
for distance in [0,.02,.04,.06,.08,.10,.12,.16,.18]:
 tr=T+axis*distance;phi=cad.query(q[sam.ids],tr)['phi'];rows.append(dict(horizontal_slide_m=distance,minimum_static_clearance_m=float(phi.min())))
selected=next((r for r in rows if r['minimum_static_clearance_m']>=.001),None);out=dict(scope='Proposed change to withdrawal direction only; user decision needed before adoption',reason='Current bodyward vector is nearly normal to blade face and sweeps it sideways through tissue. Initial tangent slide would keep height fixed and have positive bodyward projection, followed by the originally requested bodyward direction.',axis_direction_sim=axis.tolist(),original_bodyward_direction_sim=d.tolist(),axis_bodyward_dot=float(axis@d),static_scan=rows,first_sample_with_1mm_clearance=selected,adopted=False);(W/'withdrawal_proposal.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
