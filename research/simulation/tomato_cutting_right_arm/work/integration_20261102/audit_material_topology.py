from pathlib import Path
import json,numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
r=Path(__file__).resolve().parents[2];s=r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((s/'surface_design.json').read_text());assignments=json.loads((s/'mass_stiffness_assignments.json').read_text());x=np.array([n['position_m'] for n in design['nodes']]);spring=[];cells=[]
for a in assignments:spring.extend(design['bonds'][i]['nodes'] for i in a['bond_ids']);cells.extend(a['integration_cells_global_ids'])
spring=np.asarray(spring);cells=np.asarray(cells);side=(x[:,0]>design['cut_x_m']).astype(int)
# Duplicate zero-gap seam nodes require ownership from actual integration cells.
owner=np.full(len(x),-1,int)
for tet in cells:
 label=int(x[tet].mean(0)[0]>design['cut_x_m'])
 for node in tet:
  if owner[node] not in [-1,label]:raise ValueError('Shared mechanical node across material pieces')
  owner[node]=label
cross_spring=int(np.sum(owner[spring[:,0]]!=owner[spring[:,1]]));cross_cells=int(np.sum(np.any(owner[cells]!=owner[cells[:,0,None]],axis=1)));cross_surface=sum(len(set(owner[tri]))!=1 for p in design['pieces'] for tri in p['triangles']);edges=spring.tolist()
for tet in cells:
 for i in range(1,4):edges.append([int(tet[0]),int(tet[i])])
edges=np.array(edges);graph=coo_matrix((np.ones(2*len(edges)),(np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),shape=(len(x),len(x)));n,labels=connected_components(graph,directed=False);fixed=np.asarray(design['fixture']['node_ids']);fixture_side=np.unique(owner[fixed]);d=dict(nodes=len(x),springs=len(spring),cells=len(cells),cross_piece_bulk_springs=cross_spring,cross_piece_volume_cells=cross_cells,cross_piece_skin_triangles=int(cross_surface),bulk_material_components_after_all_cohesion_removed=int(n),component_sizes=np.bincount(labels).tolist(),fixture_nodes=len(fixed),fixture_material_side=fixture_side.tolist(),no_slice_node_pinned=bool(np.all(owner[fixed]==1)),scope='Topology audit only. Prescribed cohesion removal is not a performed cut; contact may still transmit compressive loads.')
assert cross_spring==cross_cells==cross_surface==0 and n==2 and d['no_slice_node_pinned'];(r/'work/integration_20261102/material_topology_audit.json').write_text(json.dumps(d,indent=2)+'\n');print(d)
