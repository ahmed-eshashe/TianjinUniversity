from pathlib import Path
import json,numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
w=Path(__file__).resolve().parent;reports=[]
for p in sorted(w.glob('robo_*_result.json')):
 d=json.loads(p.read_text());z=np.load(p.with_name(p.name.replace('_result.json','_final.npz')));radii=[.0078125,.01171875,.015625];graphs=[]
 for radius in radii:
  row={'radius_m':radius}
  for label in ['initial','x']:
   x=z[label];pairs=cKDTree(x).query_pairs(radius,output_type='ndarray');g=coo_matrix((np.ones(len(pairs)),(pairs[:,0],pairs[:,1])),shape=(len(x),len(x))).tocsr();n,labels=connected_components(g,directed=False);sizes=np.bincount(labels);row[label]={'components':int(n),'largest_sizes':sorted(sizes.tolist(),reverse=True)[:8],'components_over_1_percent':int((sizes>=.01*len(x)).sum())}
  graphs.append(row)
 reports.append(dict(case=p.stem,particle_count=len(z['x']),finite=bool(np.isfinite(z['x']).all() and np.isfinite(z['v']).all()),proximity_connectivity=graphs,meaning='Geometric proximity diagnostic, NOT cohesive fracture or proof of disconnected continuum; MPM has no fixed bond graph.'))
(w/'robo_separation_assessment.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
