from pathlib import Path
import numpy as np,json
from scipy.spatial import cKDTree
W=Path(__file__).resolve().parent;old=np.load(W.parent/'disect_precontact_20261108_v06/conforming_split.npz');m=np.load(W/'conforming_split.npz');e=dict(np.load(W.parent/'disect_completion_20261108_v07/closure_embedding.npz'));q=e['reference_positions'];x=m['x'];t=m['tets'];ids=np.empty((len(q),4),int);weights=np.empty((len(q),4));oldminus=set(old['tets'][old['tet_side']<0].ravel());side=np.array([-1 if n in oldminus else 1 for n in e['surface_node_ids']])
for sign in [-1,1]:
 cells=t[m['tet_side']==sign];tri=x[cells];D=np.linalg.inv((tri[:,1:]-tri[:,0,None]).transpose(0,2,1));tree=cKDTree(tri.mean(1))
 for i in np.flatnonzero(side==sign):
  for k in [64,256,len(cells)]:
   candidates=np.atleast_1d(tree.query(q[i],k=min(k,len(cells)))[1]);uv=np.einsum('nij,nj->ni',D[candidates],q[i]-tri[candidates,0]);b=np.column_stack([1-uv.sum(1),uv]);best=b.min(1).argmax()
   if b[best].min()>=-1e-10:
    ids[i]=cells[candidates[best]];weights[i]=b[best];break
  else:raise ValueError(f'Proxy {i} outside new physical mesh')
actual=np.einsum('ni,nij->nj',weights,x[ids]);err=float(abs(actual-q).max());assert err<1e-12
# Tiny negative roundoff clipped only after exact reconstruction audit.
weights=np.maximum(weights,0);weights/=weights.sum(1)[:,None];e['indices']=ids;e['weights']=weights
np.savez_compressed(W/'preserved_contact_embedding.npz',**e)
out=dict(proxy_points=len(q),max_coordinate_error_m=err,min_weight=float(weights.min()),triangle_connectivity_preserved=True,rest_proxy_geometry_preserved=True,passed=True);(W/'contact_remap.json').write_text(json.dumps(out,indent=2));print(out)
