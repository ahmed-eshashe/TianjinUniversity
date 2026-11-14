from pathlib import Path
import numpy as np,json,hashlib
w=Path(__file__).resolve().parent;r=w.parents[1];src=r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';d=json.loads((src/'surface_design.json').read_text());a=json.loads((src/'mass_stiffness_assignments.json').read_text());x=np.array([n['position_m'] for n in d['nodes']]);t=np.array([t for p in a for t in p['integration_cells_global_ids']]);v=np.linalg.det(x[t[:,1:]]-x[t[:,0,None]])/6;m=np.zeros(len(x))
for p in a:m[p['global_node_ids']]=p['node_mass_kg']
print('dims',d['dimensions_m'],'bounds',x.min(0),x.max(0),'mass',m.sum(),'tetvol',v.sum(),'minvol',v.min(),'role',[p['integration_cells_role'] for p in a]);print('gap',d['numerical_rest_gap_m']);print('patch',str(d['interface_patches'][0])[:1200])
# Export without importing production solver or changing any source assets.
np.savez(w/'source_tomato.npz',x=x,tets=t,mass=m,fixed=d['fixture']['node_ids'],surface=np.array([f for p in d['pieces'] for f in p['triangles']]))
report={'source_hashes':{n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in ['surface_design.json','mass_stiffness_assignments.json']},'source_dimensions':d['dimensions_m'],'bounds_m':[x.min(0).tolist(),x.max(0).tolist()],'mass_kg':m.sum(),'nodes':len(x),'volume_cells':len(t),'sum_cell_volume_m3':v.sum(),'cell_role':[p['integration_cells_role'] for p in a],'cut_x_m':d['cut_x_m'],'rest_gap_m':d['numerical_rest_gap_m'],'fixture_nodes':d['fixture']['node_ids']}
(w/'tomato_source_audit.json').write_text(json.dumps(report,indent=2))
