from pathlib import Path
import sys,json,numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent
sys.path[:0]=[str(r/'rl'),str(r/'work/scripted_slicing_20261106')]
from tomato_native_full_model import registry
from separation import assess_separation
d=registry();labels=np.array([0 if n['side']=='slice' else 1 for n in d['design']['nodes']]);bulk=np.concatenate([d['springs']]+[d['cells'][:,[0,j]] for j in [1,2,3]])
# Each active objective patch couples all pair nodes and its material frame anchors.
# A spanning star is sufficient for the connectivity graph, without changing mechanics.
active=[]
for p in d['cohesion'].patches:
 ids=np.unique(d['pairs'][p['indices']]);active.extend((int(ids[0]),int(j)) for j in ids[1:])
intact=assess_separation(d['mass'],np.concatenate([bulk,np.array(active)]),labels)
failed=assess_separation(d['mass'],bulk,labels)
result=dict(intact_components=intact['component_count'],all_failed_components=failed['component_count'],all_failed_topological_separation=failed['topological_separation'],piece_masses_kg=[c['mass_kg'] for c in failed['components']],fixture_piece_labels=np.unique(labels[d['design']['fixture']['node_ids']]).tolist(),scope='Topology audit only. All-failed graph is hypothetical; no history altered, no performed slice.')
assert intact['component_count']==1 and failed['topological_separation']
(w/'connectivity.json').write_text(json.dumps(result,indent=2));print(result)
