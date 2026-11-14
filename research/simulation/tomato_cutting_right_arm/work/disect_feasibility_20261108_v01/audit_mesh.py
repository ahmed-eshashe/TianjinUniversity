from pathlib import Path
import numpy as np,json
w=Path(__file__).resolve().parent;d=np.load(w/'mesh_audit_input.npz');x=d['particle_x'];t=d['tets'];ei=d['edge_indices'];c=d['edge_coords'];v=(1-c[:,None])*x[ei[:,0]]+c[:,None]*x[ei[:,1]];aug=np.vstack([x,v]);q=x[t];vol=np.linalg.det(q[:,1:]-q[:,0,None,:])/6
out={'native_status':json.loads((w/'mesh_status.json').read_text()),'nodes':len(x),'tets':len(t),'finite_coordinates':bool(np.isfinite(x).all()),'tet_indices_valid':bool(t.min()>=0 and t.max()<len(x)),'minimum_absolute_tet_volume':float(abs(vol).min()),'negative_tet_volumes':int((vol<0).sum()),'zero_tet_volumes':int((vol==0).sum()),'edge_coordinates_finite_in_0_1':bool(np.isfinite(c).all() and (c>=0).all() and (c<=1).all()),'surfaces':{}}
for key,coords in [('triangles',x),('cut_triangles',aug),('virtual_triangles',v),('above',v),('below',v)]:
 f=d[key];p=coords[f];area=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)/2
 out['surfaces'][key]={'count':len(f),'indices_valid':bool(f.min()>=0 and f.max()<len(coords)),'zero_area_count':int((area<1e-15).sum()),'duplicate_unoriented_triangles':len(f)-len(np.unique(np.sort(f,axis=1),axis=0)),'minimum_area':float(area.min())}
out['paired_cut_faces']=len(d['above'])==len(d['below'])
(w/'mesh_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
