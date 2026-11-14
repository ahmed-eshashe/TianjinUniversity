from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from independent_cad_query import query_mesh
z=np.load(W/'assets/blade_partition.npz');cells=z['x'][z['tets']];eq=z['planes'];raw=json.loads((W/'assets/blade_export.json').read_text());v=np.array(raw['vertices']);v-=np.array([-.24,v[:,1].min(),.00125]);f=np.array(raw['triangles']);rng=np.random.default_rng(3917)
bary=rng.dirichlet(np.ones(4),size=(len(cells),16));inside=np.einsum('tni,tij->tnj',bary,cells).reshape(-1,3);random=rng.uniform(v.min(0)-.0001,v.max(0)+.0001,(2000,3));pts=np.r_[inside,random];hits=np.zeros(len(pts),int)
for planes in eq:hits+=np.all(pts@planes[:,:3].T+planes[:,3]<-1e-12,axis=1)
r=query_mesh(v,f,pts);checks={'interior_cell_points_inside_CAD':bool(np.all(r['phi'][:len(inside)]<0)),'cell_interior_single_ownership':bool(np.all(hits[:len(inside)]==1)),'CAD_and_partition_membership_agree':bool(np.array_equal(hits>0,r['phi']<0)),'no_sample_overlap':bool(np.all(hits<=1))};result={'checks':checks,'passed':all(checks.values()),'samples':len(pts),'purpose':'Independent signed-mesh query against unchanged positive-volume conforming CAD partition; randomized supplement to exact boundary/volume/manifold checks.'};(W/'reports/partition_membership.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
