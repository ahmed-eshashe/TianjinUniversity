from pathlib import Path
import sys,json,numpy as np
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;R=W.parents[1];sys.path.insert(0,str(W.parent/'disect_adaptive_contact_20261109_v27'))
from adaptive_contact import AdaptiveContact,intersections
from tomato_compiled_blade_query import query_mesh
base=json.loads((W/'initial_entry_geometry_audit.json').read_text());front=np.array(base['front_point_m']);plan=json.loads((W/'correction_plan.json').read_text());T=np.array(plan['selected']['translation_m']);curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T);d=base['initial_vertical_apex_clearance_m']+.001;T+=np.array([float(curve(d)),-d,0])
raw=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rotation=A.T@ref['rotation'];local=np.array(raw['vertices']);faces=np.array(raw['triangles']);vertices=local@rotation.T+T
start=np.array([vertices[:,0].min()-.01,front[1],front[2]]);end=np.array([vertices[:,0].max()+.01,front[1],front[2]]);times=intersections(start,end,vertices,faces);times=times[np.r_[True,np.diff(times)>1e-12]];mid=(times[1:]+times[:-1])/2;phi=query_mesh(vertices,faces,start+mid[:,None]*(end-start))['phi'];inside=[(a,b) for a,b,p in zip(times[:-1],times[1:],phi) if p<0];assert len(inside)==1
left,right=[start[0]+t*(end[0]-start[0]) for t in inside[0]];correction=front[0]-(left+right)/2
q=np.tile(front,(4,1));q[0,0]-=.003;q[2,0]+=.003
c=AdaptiveContact.__new__(AdaptiveContact);c.edges=np.array([[0,1],[2,3]]);c.edge_weights=np.ones(2);c.force_atol=1e-10;c.rtol=1e-6;c.max_depth=40
rows=[]
for name,offset in [('current_reference',0.),('geometric_center_reference',correction)]:
 shifted=vertices+np.array([offset,0,0]);ev=c.evaluate(q,np.zeros_like(q),shifted,faces,np.zeros(3),T+np.array([offset,0,0]),ke=2e6,kd=0.)
 rows.append(dict(name=name,translation_correction_x_m=float(offset),negative_cut_node_force_N=ev['force'][1].tolist(),positive_cut_node_force_N=ev['force'][3].tolist(),negative_bank_force_N=ev['force'][:2].sum(0).tolist(),positive_bank_force_N=ev['force'][2:].sum(0).tolist(),cut_node_forces_open_interface=bool(ev['force'][1,0]<0 and ev['force'][3,0]>0),energy_J=ev['energy_J']))
out=dict(scope='Static 4-node/two-material-edge force-direction diagnostic on the exact CAD; intentionally penetrating fixture, not an admissible tomato episode or cutting qualification. Offset is derived from geometry, not chosen by damage outcomes.',material_reference_m=front.tolist(),knife_interval_at_1mm_depth_m=[float(left),float(right)],geometric_center_offset_x_m=float(correction),rows=rows)
(W/'knife_reference_direction_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
