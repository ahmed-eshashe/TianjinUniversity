"""Host analytic ownership, positive quadrature and neighbourhood coverage controls."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.spatial import ConvexHull
from tomato_padded_material_coverage import padded_coverage,subtract_convex,signed_uv_area
from tomato_host_blade_geometry import query_mesh
R=Path(__file__).resolve().parents[2];out=R/'runs/offline/padded_material_coverage_20261102_01';out.mkdir(exist_ok=False);(out/'input_manifest.json').write_text(json.dumps(dict(scope='Host material-domain geometry only. No native CAD force, collision/CCD, time integration or robot qualification.',area_absolute_budget_m2=1e-14,uv_area_budget=1e-12,conservation_budget=1e-10,neighbourhood_grid_resolution=160,padding_m=.0005,split_fraction=float(np.sqrt(2)-1)),indent=2)+'\n');records=[]
def bary(uv):
 uv=np.array(uv);return np.c_[1-uv.sum(1),uv]
P=bary([[0,0],[1,0],[0,1]])
for label,Q,expected in [('identical',P,0.),('internal',bary([[.25,.25],[.5,.25],[.25,.5]]),.46875),('partial',bary([[.5,0],[1.5,0],[.5,1]]),.375),('disjoint',bary([[2,0],[3,0],[2,1]]),.5)]:
 pieces=subtract_convex(list(P),list(Q));area=sum(abs(signed_uv_area(p))for p in pieces);error=abs(area-expected)
 if error>1e-12:raise ValueError((label,area,expected))
 records.append(dict(case='convex_difference_'+label,uv_area_error=error))
v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],dtype=float)*.01;soft=np.array([[.001,.001,.001],[.006,.001,.001],[.001,.006,.001]]);tri=np.array([[0,1,2]]);cells=np.array([[0,1,2,3],[0,1,2,3]]);expected=.5*.005*.005
for level in [0,1,2]:
 result=padded_coverage(v,cells,soft,tri,soft,padding_m=.0005,level=level);weights=np.array([s['area_m2']for s in result['samples']]);points=np.array([s['point_m']for s in result['samples']]);b=np.array([s['barycentric']for s in result['samples']]);ids=np.array([s['corners']for s in result['samples']]);actual=weights.sum();error=abs(actual-expected);centroid=np.sum(weights[:,None]*points,axis=0)/expected;centroid_error=float(abs(centroid-soft.mean(0)).max());exact_x2=expected*(np.sum(soft[:,0]**2)+sum(soft[i,0]*soft[j,0]for i,j in [(0,1),(0,2),(1,2)]))/6;quadratic_error=float(abs(np.sum(weights*points[:,0]**2)-exact_x2));rng=np.random.default_rng(12);f=rng.normal(size=points.shape);nodal=np.zeros_like(soft)
 for corner in range(3):np.add.at(nodal,ids[:,corner],b[:,corner,None]*f)
 delta=rng.normal(size=soft.shape)*1e-5;force_error=float(abs(nodal.sum(0)-f.sum(0)).max());moment_error=float(np.linalg.norm(np.cross(soft,nodal).sum(0)-np.cross(points,f).sum(0)));work_error=float(abs(np.sum(nodal*delta)-np.sum(f*np.einsum('ni,nij->nj',b,delta[ids]))))
 if error>1e-14 or centroid_error>1e-12 or quadratic_error>1e-14 or min(weights)<=0 or b.min()<-1e-12 or max(force_error,moment_error,work_error)>1e-10:raise ValueError((level,error,centroid_error,quadratic_error,force_error,moment_error,work_error))
 records.append(dict(case='duplicate_cell_positive_quad_level_'+str(level),reference_area_m2=actual,removed_duplicate_reference_area_m2=result['raw_duplicated_reference_area_m2']-result['reference_area_m2'],area_error_m2=error,centroid_error_m=centroid_error,quadratic_integral_error=quadratic_error,force_error_n=force_error,moment_error_nm=moment_error,virtual_work_error_j=work_error))
v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,1]],dtype=float)*.01;cells=np.array([[0,1,2,3],[4,1,3,2]]);soft=np.array([[-.003,-.003,.003],[.022,-.003,.003],[-.003,.022,.003]]);h=.0005;result=padded_coverage(v,cells,soft,tri,soft,padding_m=h,level=1);faces=ConvexHull(v).simplices.copy()
for f in faces:
 t=v[f]
 if np.cross(t[1]-t[0],t[2]-t[0])@(t.mean(0)-v.mean(0))<0:f[1],f[2]=f[2],f[1]
b=bary([[i/160,j/160]for i in range(161)for j in range(161-i)]);points=b@soft;q=query_mesh(v,faces,points);needed=q['phi']<=h-1e-8;owners=np.zeros(len(points),dtype=int);boundary=np.zeros(len(points),dtype=bool)
for polygon in result['polygons_by_triangle'][0]:
 p=np.array(polygon)
 if signed_uv_area(p)<0:p=p[::-1]
 inside=np.ones(len(points),dtype=bool);near=np.zeros(len(points),dtype=bool)
 for index,first in enumerate(p):
  edge=p[(index+1)%len(p),1:]-first[1:];normal=np.array([edge[1],-edge[0]]);value=(b[:,1:]-first[1:])@normal;inside&=value<=1e-12;near|=abs(value)<=1e-12
 owners+=inside;boundary|=inside&near
missing=int(np.sum(needed&(owners==0)));overlap=int(np.sum((owners>1)&~boundary))
if missing or overlap:raise ValueError(('Padded neighbourhood/ownership failed',missing,overlap))
records.append(dict(case='adjacent_cells_padded_neighbourhood',oracle_grid_points=len(points),required_near_solid_points=int(needed.sum()),uncovered_required_points=missing,duplicate_interior_owners=overlap,owned_polygons=sum(len(p)for p in result['polygons_by_triangle'].values()),reference_union_area_m2=result['reference_area_m2'],raw_duplicate_area_removed_m2=result['raw_duplicated_reference_area_m2']-result['reference_area_m2']))
report=dict(passed=True,cases=records,scope='Eight host controls: convex difference, duplicate-cell ownership, degree-two positive quadrature/force/moment/work and independent analytic closed-hull distance membership screen. The plane/AABB expansion is a conservative outer bound, not a strict exact-arithmetic CCD certificate or native contact qualification.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'rl/tomato_padded_material_coverage.py',R/'rl/tomato_host_blade_geometry.py']});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
