from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from blade_contact import CADBlade
from full_surface import FullSurface
s=FullSurface();cad=CADBlade();q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];vertices=cad.vertices@cad.rotation.T;cut=np.unique(s.li.numpy());p=json.loads((W.parent/'disect_physical_20261109_v22/indent_plan.json').read_text());T=np.array(p['initial_translation_m']);out=dict(CAD_local_bounds=[cad.minimum.tolist(),cad.maximum.tolist()],CAD_mapped_bounds=[vertices.min(0).tolist(),vertices.max(0).tolist()],cut_bounds=[q[cut].min(0).tolist(),q[cut].max(0).tolist()],tomato_bounds=[q.min(0).tolist(),q.max(0).tolist()],initial_T=T.tolist());print(json.dumps(out,indent=2));(W/'alignment_audit.json').write_text(json.dumps(out,indent=2))
