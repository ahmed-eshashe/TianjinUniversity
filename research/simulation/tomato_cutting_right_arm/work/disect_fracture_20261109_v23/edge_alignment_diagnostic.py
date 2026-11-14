from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from blade_contact import CADBlade
from full_surface import FullSurface
s=FullSurface();cad=CADBlade();q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];pairs=s.mesh['ties'];mid=.5*(q[pairs[:,0]]+q[pairs[:,1]]);p=mid[np.argmax(mid[:,1])];old=json.loads((W/'shallow_plan.json').read_text());T=np.array(old['selected']['translation_m']);v=cad.vertices@cad.rotation.T;z0=p[2]-T[2];cross=[]
for tri in cad.triangles:
 for i,j in [(0,1),(1,2),(2,0)]:
  a=v[tri[i]];b=v[tri[j]]
  if (a[2]-z0)*(b[2]-z0)<0:cross.append(a+(z0-a[2])/(b[2]-a[2])*(b-a))
cross=np.unique(np.round(cross,14),axis=0);minimum=cross[:,1].min();edge=cross[abs(cross[:,1]-minimum)<1e-7];edge_x=float(edge[:,0].mean());new=T.copy();new[0]=p[0]-edge_x;new[1]=p[1]-minimum+5e-6;out=dict(scope='Read-only cutting-edge cross-section alignment diagnostic; no new run adopted',target_top_interface_midpoint_m=p.tolist(),CAD_cross_section_z_m=float(z0),CAD_lowest_edge_points_m=edge.tolist(),old_translation_m=T.tolist(),edge_aligned_translation_m=new.tolist(),lateral_correction_m=float(new[0]-T[0]),edge_points_count=len(edge),edge_width_x_m=float(np.ptp(edge[:,0])),current_initial_outer_min_phi_m=float(cad.query(q[np.unique(s.mesh['outer'])],new)['phi'].min()));(W/'edge_alignment_diagnostic.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
