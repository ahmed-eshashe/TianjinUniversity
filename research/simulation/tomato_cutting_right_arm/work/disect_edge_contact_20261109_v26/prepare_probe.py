"""Read-only whole-material clearance and bounded contact fixture placement."""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1]
sys.path.insert(0,str(R/'rl'))
from tomato_compiled_blade_query import query_mesh
old=W.parent/'disect_shallow_20261109_v25'
p=json.loads((old/'correction_plan.json').read_text())
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
rotation=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation']
verts=np.array(d['vertices']);faces=np.array(d['triangles'])
mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz')
q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];cells=mesh['tets']
raw=np.concatenate([cells[:,[i,j]] for i in range(4) for j in range(i)])
edges=np.unique(np.sort(raw,axis=1),axis=0)
T0=np.array(p['selected']['translation_m'])
def query(points,T):return query_mesh(verts,faces,(points-T)@rotation)['phi']
def edge_bound(T,order=513):
 local=(q-T)@rotation;a,b=edges.T
 keep=np.all((np.maximum(local[a],local[b])>=verts.min(0))&
             (np.minimum(local[a],local[b])<=verts.max(0)),axis=1)
 e=edges[keep]
 if not len(e):return 0.,0,0.
 u=np.linspace(0,1,order)[None,:,None]
 points=q[e[:,0],None]*(1-u)+q[e[:,1],None]*u
 phi=query(points.reshape(-1,3),T).reshape(len(e),order)
 depth=np.maximum(-phi.min(1),0)
 uncertainty=np.linalg.norm(q[e[:,1]]-q[e[:,0]],axis=1)/(2*(order-1))
 return float(np.max(depth+uncertainty)),len(e),float(depth.max())
rows=[]
for up in [0.,.001,.002,.004,.01]:
 bound,n,depth=edge_bound(T0+[0,up,0]);rows.append(dict(up_m=up,conservative_edge_penetration_bound_m=bound,sampled_depth_m=depth,screened_edges=n))
lo=0.;hi=.01
for _ in range(14):
 up=(lo+hi)/2;bound,n,depth=edge_bound(T0+[0,up,0],257)
 if bound>20e-6:lo=up
 else:hi=up
hold=T0+[0,hi,0];bound,n,depth=edge_bound(hold,1025)
clear=T0+[0,.01,0];phi=query(q,clear)
diameter=np.zeros(len(cells))
for i in range(4):
 for j in range(i):diameter=np.maximum(diameter,np.linalg.norm(q[cells[:,i]]-q[cells[:,j]],axis=1))
lower=phi[cells].min(1)-np.sqrt(3/8)*diameter-1e-9
out=dict(scope='Placement only; immutable settled mesh; no motion, fracture or material changes',
 original_initial_edge_audit=rows,whole_tetrahedron_clear_translation_m=clear.tolist(),
 whole_tetrahedron_clearance_lower_bound_m=float(lower.min()),
 clear_start_passed=bool(lower.min()>=.001),
 loaded_component_hold_translation_m=hold.tolist(),hold_upward_correction_m=hi,
 hold_conservative_all_edge_penetration_bound_m=bound,hold_sampled_penetration_m=depth,
 hold_placement_passed=bool(bound<.0001),
 note='The hold fixture deliberately begins in small contact. It is not a zero-load approach trajectory or Gate B pass.')
(W/'probe_placement.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
