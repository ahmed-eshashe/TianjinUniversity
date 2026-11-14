from pathlib import Path
import sys,json,numpy as np
from scipy.spatial import cKDTree
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_mesh_validation_20261108_v02/audit_deps'))
from shapely import Polygon,LineString,union_all
from shapely.ops import polygonize
z=np.load(W/'conforming_split.npz');X=z['x'];x=z['source_x'];src=z['source_outer'];cand=z['outer'];p=x[src];norm=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None];tree=cKDTree(p.mean(1));groups={};unmatched=[];plane_error=0.;bary_error=0.
def match(tri,candidates):
    for idx in np.atleast_1d(candidates):
        a,b,c=p[idx];u=b-a;v=c-a;w=tri-a;uu=u@u;uv=u@v;vv=v@v;den=uu*vv-uv*uv;beta=(w@u*vv-w@v*uv)/den;gamma=(w@v*uu-w@u*uv)/den;dist=np.max(abs(w@norm[idx]));outside=max(float(np.max(-beta)),float(np.max(-gamma)),float(np.max(beta+gamma-1)),0.)
        if dist<1e-10 and outside<1e-8:return int(idx),float(dist),outside
    return None
for face in cand:
    tri=X[face];ids=tree.query(tri.mean(0),k=24)[1];result=match(tri,ids)
    if result is None:result=match(tri,np.arange(len(src)))
    if result is None:unmatched.append(face.tolist());continue
    idx,dist,outside=result;groups.setdefault(idx,[]).append(face);plane_error=max(plane_error,dist);bary_error=max(bary_error,outside)
uncovered=outside=overlap=0.
for idx,tri in enumerate(p):
    e0=(tri[1]-tri[0]);e0/=np.linalg.norm(e0);e1=np.cross(norm[idx],e0);basis=np.stack([e0,e1],axis=1);poly=Polygon((tri-tri[0])@basis);parts=[Polygon((X[f]-tri[0])@basis) for f in groups.get(idx,[])];u=union_all(parts);uncovered+=poly.difference(u).area;outside+=u.difference(poly).area;overlap+=sum(a.area for a in parts)-u.area
plane=-.0225;segments=[]
for tri in p:
    points=[]
    for a,b in zip(tri,np.roll(tri,-1,axis=0)):
        da=a[0]-plane;db=b[0]-plane
        if abs(da)<1e-12:points.append(a)
        if da*db<0:points.append(a+(plane-a[0])/(b[0]-a[0])*(b-a))
    points=np.unique(np.round(np.array(points).reshape(-1,3),12),axis=0)
    if len(points)==2:segments.append(LineString(points[:,1:]))
section=union_all(list(polygonize(union_all(segments))));sections={};dual=np.zeros(len(X))
for name in ['cut_minus','cut_plus']:
    faces=z[name];tri=X[faces];polys=[Polygon(t[:,1:]) for t in tri];u=union_all(polys);areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
    sections[name]={'triangles':len(faces),'minimum_area_m2':float(areas.min()),'union_area_m2':float(u.area),'expected_section_area_m2':float(section.area),'uncovered_area_m2':float(section.difference(u).area),'outside_area_m2':float(u.difference(section).area),'overlap_area_m2':float(sum(a.area for a in polys)-u.area),'duplicate_faces':len(faces)-len(np.unique(np.sort(faces,axis=1),axis=0))}
    if name=='cut_minus':np.add.at(dual,faces.ravel(),np.repeat(areas/3,3))
ties=z['ties'];weights=dual[ties[:,0]];np.savez_compressed(W/'interface_ties.npz',pairs=ties,reference_coordinates=X[ties[:,0]],area_weights_m2=weights,normal=np.tile([1.,0.,0.],(len(ties),1)))
cellpoints=X[z['tets']];crossing=int(((cellpoints[:,:,0].min(1)<plane-1e-12)&(cellpoints[:,:,0].max(1)>plane+1e-12)).sum());small=int((z['volume']<1e-13).sum())
out={'scope':'Independent static exterior/section/connection audit; not assembled dynamics','unmatched_exterior_faces':len(unmatched),'outer_uncovered_area_m2':float(uncovered),'outer_outside_area_m2':float(outside),'outer_overlap_area_m2':float(overlap),'max_outer_plane_error_m':plane_error,'max_outer_barycentric_error':bary_error,'sections':sections,'intact_tets_crossing_plane':crossing,'paired_ties':len(ties),'ties_position_error_m':float(np.max(abs(X[ties[:,0]]-X[ties[:,1]]))),'minimum_tie_area_weight_m2':float(weights.min()),'total_tie_area_m2':float(weights.sum()),'cells_smaller_than_1e_13_m3':small,'min_nodal_mass_kg':float(z['mass'][z['mass']>0].min()),'dynamic_limit':'Very small clipped cells remain; no time-step or prepared-assembly dynamics qualification follows. Do not delete them or raise their masses to force a pass.'}
(W/'geometry_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
