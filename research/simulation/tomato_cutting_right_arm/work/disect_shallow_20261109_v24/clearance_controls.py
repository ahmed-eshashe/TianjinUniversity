from pathlib import Path
import numpy as np,json
W=Path(__file__).resolve().parent
def box_sdf(q):
 a=np.abs(q)-.5;return np.linalg.norm(np.maximum(a,0),axis=1)+np.minimum(a.max(1),0)
def bound(q):
 D=max(np.linalg.norm(a-b) for a in q for b in q);return float(box_sdf(q).min()-np.sqrt(3/8)*D)
far=np.array([[2,2,2],[2.01,2,2],[2,2.01,2],[2,2,2.01]]);enclose=np.array([[2,2,2],[2,-2,-2],[-2,2,-2],[-2,-2,2]],float);rng=np.random.default_rng(42);worst=1e9
for k in range(30):
 q=rng.uniform(-2,2,(4,3));weights=rng.dirichlet(np.ones(4),2000);worst=min(worst,float((box_sdf(weights@q)-bound(q)).min()))
o=dict(scope='Independent analytic cube SDF fixtures for conservative tetrahedron clearance bound only',far_tetra_pass=bound(far)>.001,nodal_only_false_clearance_fixture_has_positive_vertices=bool((box_sdf(enclose)>0).all()),enclosing_tetra_rejected=bound(enclose)<0,known_interior_point_SDF=float(box_sdf(np.zeros((1,3)))[0]),sampled_inequality_min_margin_m=worst,passed=bool(bound(far)>.001 and (box_sdf(enclose)>0).all() and bound(enclose)<0 and worst>=-1e-12));(W/'clearance_controls_result.json').write_text(json.dumps(o,indent=2));print(json.dumps(o,indent=2))
