from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_precontact_20261108_v06';sys.path.insert(0,str(V));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from blade_contact import CADBlade
from full_surface import FullSurface
s=FullSurface();m=s.mesh;q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];p=json.loads((W.parent/'disect_physical_20261109_v22/indent_plan.json').read_text());cad=CADBlade();T=np.array(p['initial_translation_m']);outer=np.unique(m['outer']);cut=np.unique(np.r_[s.li.numpy().ravel(),s.ri.numpy().ravel()]);excluded=np.setdiff1d(cut,outer);rows=[]
for depth in [0,.00006,.001,.003,.005,.01,.02,.03,.04]:
 t=T-[0,depth,0];ph=cad.query(q[cut],t)['phi'];inside=cut[ph<0];rows.append(dict(downward_stroke_m=depth,inside_CAD_cut_nodes=int(len(inside)),inside_nodes_ignored_by_outer_only=int(np.isin(inside,excluded).sum())))
# Eligibility from actual incident force, including threshold boundary and no unrelated group activation.
eligibility=[]
for node in [int(cut[0]),int(excluded[len(excluded)//2])]:
 for force in [0.,1e-9,1.0001e-9]:
  f=np.zeros_like(q);f[node,0]=force;actual=s.eligibility_from_contact(f);faces=s.quad['faces'];copies=dict(m['ties']);rf=np.array([[copies[int(n)] for n in face] for face in faces]);incident=np.any(faces==node,axis=1)|np.any(rf==node,axis=1);expected=np.zeros(47,bool)
  if force>1e-9:expected[np.unique(s.quad['groups'][incident])]=True
  eligibility.append(dict(node=node,force_N=force,passed=bool(np.array_equal(actual,expected)),enabled_groups=int(actual.sum())))
out=dict(scope='Static geometric coverage only; no new contact force law or simulation adopted',outer_node_count=len(outer),cut_node_count=len(cut),cut_nodes_excluded_from_blade_contact=len(excluded),samples=rows,eligibility_controls=eligibility,eligibility_controls_passed=all(r['passed'] for r in eligibility),deep_contact_coverage_complete=len(excluded)==0)
(W/'contact_coverage_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
