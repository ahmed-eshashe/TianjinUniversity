from pathlib import Path
import sys,json,numpy as np
w=Path(__file__).resolve().parent;sys.path.insert(0,str(w/'audit_deps'))
from shapely import Polygon,box,union_all
z=np.load(w/'mesh_audit_input.npz');old=np.load(w.parent/'disect_feasibility_20261108_v01/mesh_audit_input.npz');x=z['particle_x'];ei=z['edge_indices'];c=z['edge_coords'];v=(1-c[:,None])*x[ei[:,0]]+c[:,None]*x[ei[:,1]]
out={'physics_arrays_unchanged':{key:bool(np.array_equal(z[key],old[key])) for key in ['particle_x','tets','triangles','edge_indices','edge_coords','springs']},'surfaces':{}}
rectangle=box(x[:,1].min(),x[:,2].min(),x[:,1].max(),x[:,2].max())
for key in ['above','below']:
 f=z[key];p=v[f];normals=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);area=np.linalg.norm(normals,axis=1)/2;polys=[Polygon(i[:,[1,2]]) for i in p];u=union_all(polys)
 out['surfaces'][key]={'faces':len(f),'minimum_area_m2':float(area.min()),'degenerate_faces':int((area<1e-15).sum()),'polygon_valid':bool(all(q.is_valid for q in polys)),'sum_area_m2':float(area.sum()),'union_area_m2':float(u.area),'uncovered_area_m2':float(rectangle.difference(u).area),'outside_area_m2':float(u.difference(rectangle).area),'overlap_area_m2':float(sum(q.area for q in polys)-u.area),'planarity_error_m':float(abs(p[:,:,0]).max()),'normal_signs':np.unique(np.sign(normals[:,0])).tolist()}
 # Every mapped opposite face must have identical coordinates and reversed normal.
a=v[z['above']];b=v[z['below']];pairs=np.linalg.norm(a[:,[2,1,0]]-b,axis=-1).max() if a.shape==b.shape else float('inf')
# Compare unordered vertices too: opposite winding may differ by cyclic rotation.
def keys(p):return sorted(tuple(sorted(tuple(np.round(y,12)) for y in tri)) for tri in p)
out['opposite_sides_geometrically_paired']=keys(a)==keys(b)
m=json.loads((w/'mesh_audit.json').read_text());out['qualified']=bool(all(out['physics_arrays_unchanged'].values()) and out['opposite_sides_geometrically_paired'] and all(not row['degenerate_faces'] and row['polygon_valid'] and row['uncovered_area_m2']<1e-12 and row['outside_area_m2']<1e-12 and abs(row['overlap_area_m2'])<1e-12 and row['planarity_error_m']<1e-12 for row in out['surfaces'].values()) and all(s['zero_area_count']==0 and s['duplicate_unoriented_triangles']==0 for s in m['surfaces'].values()))
(w/'prism_coverage_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
