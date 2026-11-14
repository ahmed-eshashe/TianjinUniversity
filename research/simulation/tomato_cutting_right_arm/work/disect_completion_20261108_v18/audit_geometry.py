from pathlib import Path
import sys,json,numpy as np
from scipy.spatial import cKDTree
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_mesh_validation_20261108_v02/audit_deps'))
from shapely import Polygon,union_all
z=np.load(W/'conforming_split.npz');X=z['x'];sx=z['source_x'];sf=z['source_outer']
def groups(x,f):
 t=x[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];n*=np.where(n[np.arange(len(n)),abs(n).argmax(1)]<0,-1,1)[:,None];plane=np.column_stack([n,-np.einsum('ij,ij->i',n,t[:,0])]); out={}
 for i,key in enumerate(map(tuple,np.round(plane,8))):out.setdefault(key,[]).append(i)
 return t,out
st,sg=groups(sx,sf);ct,cg=groups(X,z['outer']);missing=set(cg)-set(sg);uncovered=outside=overlap=planeerr=0.
for key,ids in sg.items():
 t=st[ids];origin=t[0,0];u=t[0,1]-origin;u/=np.linalg.norm(u);n=np.array(key[:3]);v=np.cross(n,u);basis=np.stack([u,v],axis=1)
 src=union_all([Polygon((p-origin)@basis) for p in t]);parts=[Polygon((p-origin)@basis) for p in ct[cg.get(key,[])]];cand=union_all(parts)
 uncovered+=src.difference(cand).area;outside+=cand.difference(src).area;overlap+=sum(p.area for p in parts)-cand.area
 if parts:planeerr=max(planeerr,float(abs((ct[cg[key]]-origin)@n).max()))
cut=[]
for name in ['cut_minus','cut_plus']:
 polys=[Polygon(t[:,1:]) for t in X[z[name]]];u=union_all(polys);cut.append(u)
original=np.load(W.parent/'disect_precontact_20261108_v06/conforming_split.npz');expected=union_all([Polygon(t[:,1:]) for t in original['x'][original['cut_minus']]])
out=dict(unmatched_plane_groups=len(missing),outer_uncovered_area_m2=uncovered,outer_outside_area_m2=outside,outer_overlap_area_m2=overlap,max_plane_error_m=planeerr,cut_symmetric_difference_m2=[p.symmetric_difference(expected).area for p in cut],mass_error_kg=float(z['mass'].sum()-original['mass'].sum()),support_error_m=float(abs(X[z['fixed']]-original['x'][original['fixed']]).max()),volume_relative_error=float(z['volume'].sum()/original['volume'].sum()-1))
out['passed']=bool(not missing and uncovered<1e-12 and outside<1e-12 and abs(overlap)<1e-12 and planeerr<1e-10 and max(out['cut_symmetric_difference_m2'])<1e-12 and abs(out['mass_error_kg'])<1e-12 and out['support_error_m']<1e-12 and abs(out['volume_relative_error'])<1e-10)
(W/'geometry_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
assert out['passed']
