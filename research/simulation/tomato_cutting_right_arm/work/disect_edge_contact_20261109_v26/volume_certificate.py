"""Independent whole-tetrahedron CAD intrusion bound, not just vertex/edge tests.

Longest-edge bisection partitions current linear tetrahedra without changing
the simulation. For each child, phi(centroid)-max_vertex_radius is a rigorous
1-Lipschitz lower bound for its entire volume. Unresolved cells never pass.
"""
from pathlib import Path
import json,sys,time,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1]
sys.path.insert(0,str(R/'rl'))
from tomato_compiled_blade_query import query_mesh

def certify(q,tets,vertices,faces,limit=.0001,max_depth=20,wall_cap=180.):
 start=time.perf_counter();pending=q[tets].copy();owners=np.arange(len(tets))
 padding=max(0.,-limit)
 lo=vertices.min(0)-padding;hi=vertices.max(0)+padding;count=0;minimum_sample=0.;terminal_lower=padding
 for depth in range(max_depth+1):
  # A separating coordinate plane certifies no overlap with the CAD solid.
  overlap=np.all((pending.max(1)>=lo)&(pending.min(1)<=hi),axis=1)
  pending=pending[overlap];owners=owners[overlap]
  if not len(pending):
   return dict(passed=True,unresolved_cells=0,depth=depth,query_count=count,
               lower_bound_m=terminal_lower,minimum_sample_SDF_m=minimum_sample,wall_s=time.perf_counter()-start)
  centers=pending.mean(1);radius=np.linalg.norm(pending-centers[:,None],axis=2).max(1)
  phi=query_mesh(vertices,faces,centers)['phi'];count+=len(phi)
  minimum_sample=min(minimum_sample,float(phi.min()))
  if phi.min() < -limit:
   k=int(np.argmin(phi))
   return dict(passed=False,actual_violation=True,original_tet=int(owners[k]),
               violating_point=centers[k].tolist(),minimum_sample_SDF_m=minimum_sample,
               query_count=count,depth=depth,wall_s=time.perf_counter()-start)
  bound=phi-radius;done=bound>=-limit
  if done.any():terminal_lower=min(terminal_lower,float(bound[done].min()))
  pending=pending[~done];owners=owners[~done]
  if not len(pending):
   return dict(passed=True,unresolved_cells=0,depth=depth,query_count=count,
               lower_bound_m=terminal_lower,minimum_sample_SDF_m=minimum_sample,wall_s=time.perf_counter()-start)
  if depth==max_depth or time.perf_counter()-start>wall_cap:break
  pairs=np.array([[i,j] for i in range(4) for j in range(i)])
  lengths=np.linalg.norm(pending[:,pairs[:,0]]-pending[:,pairs[:,1]],axis=2)
  chosen=pairs[np.argmax(lengths,axis=1)];idx=np.arange(len(pending))
  mid=(pending[idx,chosen[:,0]]+pending[idx,chosen[:,1]])/2
  left=pending.copy();right=pending.copy()
  left[idx,chosen[:,0]]=mid;right[idx,chosen[:,1]]=mid
  pending=np.concatenate((left,right));owners=np.tile(owners,2)
 return dict(passed=False,actual_violation=False,unresolved_cells=len(pending),depth=depth,
             query_count=count,minimum_sample_SDF_m=minimum_sample,wall_s=time.perf_counter()-start)

if __name__=='__main__':
 d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
 ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
 rot=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation']
 T=np.array(json.loads((W/'probe_placement.json').read_text())['loaded_component_hold_translation_m'])
 vertices=np.array(d['vertices'])@rot.T+T;faces=np.array(d['triangles'])
 mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz')
 rows=[]
 cases=[('initial',W.parent/'disect_physical_20261109_v22/settle_contact_final.npz'),
        ('coarse',W/'corrected_probe_coarse_final.npz'),('fine',W/'corrected_probe_fine_final.npz')]
 for name,path in cases:
  if not path.exists():continue
  result=certify(np.load(path)['x'],mesh['tets'],vertices,faces)
  rows.append(dict(case=name,**result))
 out=dict(scope='Independent whole-volume geometric certificate; fixed current FEM cells, no force changes',
          required_penetration_limit_m=.0001,rows=rows,passed=bool(len(rows)==3 and all(r['passed'] for r in rows)))
 (W/'volume_certificate_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
