from pathlib import Path
import json,numpy as np
from blade_contact import CADBlade
W=Path(__file__).resolve().parent;p=json.loads((W/'indent_plan.json').read_text());q=np.load(W/'settle_contact_final.npz')['x'];ids=np.unique(np.load(W.parent/'disect_mesh_validation_20261108_v02/tomato_fem_mesh.npz')['boundary']);c=CADBlade();t=np.array(p['initial_translation_m']);rows=[]
for s in [0,15e-6,50e-6,100e-6,200e-6,500e-6]:
 r=c.query(q[ids],t+[0,-s,0]);j=np.argmin(r['phi']);rows.append({'downstroke_m':s,'minimum_signed_distance_m':float(r['phi'][j]),'nearest_normal':r['normal'][j].tolist()})
(W/'probe_placement_diagnosis.json').write_text(json.dumps(rows,indent=2));print(rows)
