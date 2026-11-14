from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from local_continuity import Aggregate
from fast_aggregation import vertex_fields
from scipy.spatial import ConvexHull
parent=W.parent/'tomato_local_continuity_20261113_v26';rows=[]
for p in sorted((parent/'runs/continue_paid_r6').glob('accepted_event_*.npz')):
 b=Body.restore(p);before=b.metrics();a=Aggregate(b);after=a.metrics();x,v=vertex_fields(b);xx,vv=vertex_fields(a.body);dv=np.linalg.norm(v-vv,axis=1);reg=np.maximum.reduceat(dv,b.poly_ptr[:-1]);weighted=float(np.sqrt(b.V@reg**2/b.V.sum()));energy=abs(after['U']+after['T']-before['U']-before['T'])/max(before['U']+before['T'],1e-10);audit=a.audit();jumps=[]
 for r in np.flatnonzero(a.body.codes%3==1):
  for q in np.flatnonzero(a.body.codes%3==2):
   if not np.array_equal(a.body.inv[r],a.body.inv[q]):continue
   poly=a.body.polys[r];hull=ConvexHull(a.body.polys[q]);inside=np.max(poly@hull.equations[:,:3].T+hull.equations[:,3],axis=1)<1e-12
   for X in poly[inside]:
    N=np.r_[1.,X]@a.body.inv[r];jumps.append(N@a.E[a.body.ids[r]].toarray()-N@a.E[a.body.ids[q]].toarray())
 opening=int(np.linalg.matrix_rank(np.array(jumps),tol=1e-10)) if jumps else 0;checks=dict(positive_opening=opening>0,mass=a.report['mass_relative_error']<1e-6,position=a.transfer['position_m']<.0001,weighted_velocity=weighted<.005,energy=energy<.05,elastic_rank=audit['rank']==audit['expected_rank']);row=dict(file=p.name,nodes_before=b._valid_basis.shape[1],nodes_after=len(a.q),opening_rank=opening,transfer=a.transfer,weighted_velocity_bound_m_s=weighted,projection_energy_relative=energy,checks={k:bool(v) for k,v in checks.items()},mechanics=audit);rows.append(row);print(json.dumps(row),flush=True)
out=dict(passed=all(all(r['checks'].values()) for r in rows),cases=rows,scope='Projection-only candidate, not dynamic accuracy or RL qualification. Same-parent same-history face-connected affine coalescence, exact reduced inertia, no geometry deletion.');(W/'reports/bounded_basis_projection.json').write_text(json.dumps(out,indent=2));assert out['passed']
