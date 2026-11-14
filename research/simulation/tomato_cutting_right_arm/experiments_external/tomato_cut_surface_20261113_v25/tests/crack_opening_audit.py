"""Check mechanical opening modes, separately from geometric crack area."""
from pathlib import Path
import os,sys,json,numpy as np
from scipy.spatial import ConvexHull
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from fast_aggregation import Aggregate
from poly_surface import Surface

def audit(b):
 a=Aggregate(b);s=Surface(a);positive=np.flatnonzero(b.codes%3==1);negative=np.flatnonzero(b.codes%3==2);jumps=[];paired_area=0.;checked=0
 # Same parent affine map: select only the genuinely new interior faces,
 # and evaluate both lips at precisely the same reference material point.
 for face,owner in enumerate(s.tri_owner):
  if owner not in positive:continue
  x=s.triangles[face].mean(0);n=np.r_[1.,x]@b.inv[owner]
  matches=[j for j in negative if np.array_equal(b.inv[j],b.inv[owner]) and np.max(ConvexHull(b.polys[j]).equations[:,:3]@x+ConvexHull(b.polys[j]).equations[:,3])<1e-12]
  if not matches:continue
  j=matches[0];left=np.asarray(n@a.E[b.ids[owner]].toarray());right=np.asarray(n@a.E[b.ids[j]].toarray());jump=left-right;jumps.append(jump);paired_area+=s.tri_area[face];checked+=1
 matrix=np.asarray(jumps);rank=int(np.linalg.matrix_rank(matrix,tol=1e-11)) if len(matrix) else 0
 return dict(original_coordinate_nodes=len(np.unique(b.grid,axis=0)),mechanical_nodes=len(a.q),paired_crack_triangles=checked,paired_reference_area_m2=float(paired_area),opening_operator_rank=rank,maximum_opening_row_norm=float(np.linalg.norm(matrix,axis=1).max()) if len(matrix) else None,components=len(np.unique(b.components()[0])),geometry_history_only=all(h.get('geometry_only',True) for h in b.history))

actual=Body.restore(W/'runs/paid_onset_inclined_r3/event_candidate.npz');measured=audit(actual);reference=Body(n=2,h=.003);reference.split([1,0,0],.00013);full=audit(reference);cases=[]
# Straight-front inclination matching the physical trial. These are static
# diagnostic geometries, never passed off as physically achieved cuts.
normal=np.array([1.,0,0]);direction=np.array([0.,-np.cos(np.pi/6),-np.sin(np.pi/6)]);start=float(np.min(Body(n=2,h=.003).grid@direction))
for depth in [1e-5,5e-5,1e-4,5e-4,1e-3,3e-3]:
 b=Body(n=2,h=.003);b.split(normal,.00013,front=(direction,start+depth));entry=audit(b);entry['front_advance_m']=depth;cases.append(entry)
out=dict(observed_event=measured,full_plane_control=full,partial_geometry_cases=cases,scope='Mechanical opening rank, independent of fracture-area payment and rendering. Geometry-only controls explicitly labelled.',partial_crack_has_opening_mode=measured['opening_operator_rank']>0,full_plane_control_opens=full['opening_operator_rank']>0)
(W/'reports/crack_opening_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
