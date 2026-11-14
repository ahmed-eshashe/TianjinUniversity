from pathlib import Path
import json,numpy as np
W=Path(__file__).resolve().parent
m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');pairs=m['ties'];tt=m['tets'];sides=m['tet_side'];node_side=np.zeros(len(m['x']),int);node_side[tt.ravel()]=np.repeat(sides,4)
assert np.all(node_side[pairs[:,0]]!=node_side[pairs[:,1]])
neg=np.where(node_side[pairs[:,0]]<0,pairs[:,0],pairs[:,1]);pos=np.where(node_side[pairs[:,0]]>0,pairs[:,0],pairs[:,1]);mapping=np.full(len(m['x']),-1,int);mapping[neg]=np.arange(len(pairs));mapping[pos]=np.arange(len(pairs));on=mapping[tt]>=0
tri=np.array([mapping[tet[mask]] for tet,mask,side in zip(tt,on,sides) if side>0 and mask.sum()==3]);assert len(tri)>0
base=json.loads((W/'initial_entry_geometry_audit.json').read_text());plan=json.loads((W/'correction_plan.json').read_text());edge0=np.array(base['initial_apex_at_same_z_m']);T0=np.array(plan['selected']['translation_m'])
def surface_x(points,yz):
 p=points[tri][:,:,[1,2]];A=np.transpose(p[:,1:]-p[:,0,None],(0,2,1));rhs=yz-p[:,0];det=np.linalg.det(A);valid=abs(det)>1e-18;ids=np.flatnonzero(valid);uv=np.linalg.solve(A[valid],rhs[valid]);weights=np.column_stack((1-uv.sum(1),uv));keep=np.all(weights>=-1e-9,axis=1)&np.all(weights<=1+1e-9,axis=1)
 if not keep.any():return None
 choices=ids[keep];ww=weights[keep];xs=np.einsum('ij,ij->i',points[tri[choices],0],ww)
 return {'x_m':float(xs[0]),'containing_faces':len(xs),'consistency_span_m':float(np.ptp(xs)),'triangle_pair_indices':tri[choices[0]].tolist(),'weights':ww[0].tolist()}
rows=[]
for file in ['prefix0038_checkpoint.npz','loading0080_checkpoint.npz']:
 z=np.load(W/file);q=z['x'];time=float(z['step'])*float(z['dt']);edge=edge0+z['blade_translation']-T0;mid=(q[neg]+q[pos])/2
 surfaces={name:surface_x(points,edge[[1,2]]) for name,points in [('negative',q[neg]),('mid',mid),('positive',q[pos])]}
 row={'checkpoint':file,'sim_s':time,'knife_apex_m':edge.tolist(),'surface_intersections_at_same_yz':surfaces,'group_history_max_m':float(z['history'][:,0].max()),'damage_max':float(z['history'][:,1].max())}
 if surfaces['mid']:row['apex_x_minus_current_interface_m']=edge[0]-surfaces['mid']['x_m']
 rows.append(row)
out={'scope':'Read-only exact current interface-facet projections at the CAD apex Y/Z. Uses the actual conforming cut-face triangulation, not an undeformed plane, group averaging or rendered appearance. This diagnoses path alignment; it is not separation or damage qualification.','interface_faces':len(tri),'rows':rows}
(W/'loaded_interface_alignment_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
