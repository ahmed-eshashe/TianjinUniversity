"""Use an existing TetGen environment; create integration cells, not a new CAD."""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_mesh_validation_20261108_v02/mesh_deps')
import tetgen
raw=json.loads((W/'assets/blade_export.json').read_text());v=np.array(raw['vertices']);f=np.array(raw['triangles'],np.int32);v=v-[-.24,v[:,1].min(),.00125]
m=tetgen.TetGen(v,f);ret=m.tetrahedralize(switches='pYQ');x=np.asarray(ret[0]);t=np.asarray(ret[1]);vol=np.linalg.det(x[t[:,1:]]-x[t[:,0]][:,None])/6
neg=vol<0;t[neg,0],t[neg,1]=t[neg,1].copy(),t[neg,0].copy();vol=abs(vol)
ff=np.sort(np.concatenate([t[:,[0,1,2]],t[:,[0,1,3]],t[:,[0,2,3]],t[:,[1,2,3]]]),axis=1);faces,n=np.unique(ff,axis=0,return_counts=True);boundary=faces[n==1]
source=abs(np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6)
checks={'positive':bool((vol>0).all()),'volume':bool(abs(vol.sum()/source-1)<1e-12),'exact_vertices':len(x)==len(v) and bool(np.array_equal(x,v)),'same_boundary':set(map(tuple,boundary))==set(map(tuple,np.sort(f,axis=1))),'manifold':bool((n<=2).all())}
planes=[]
for tet in x[t]:
 eq=[]
 for i in range(4):
  p=np.delete(tet,i,axis=0);normal=np.cross(p[1]-p[0],p[2]-p[0]);normal/=np.linalg.norm(normal);d=-p[0]@normal
  if tet[i]@normal+d>0:normal=-normal;d=-d
  eq.append([*normal,d])
 planes.append(eq)
r={'checks':checks,'passed':all(checks.values()),'vertices':len(x),'tetrahedra':len(t),'source_volume_m3':source,'tet_volume_m3':float(vol.sum()),'min_tet_volume_m3':float(vol.min()),'purpose':'Exact CAD interior partition for integration only; no change to contact distance law.'}
(W/'reports/blade_partition.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if not r['passed']:raise RuntimeError('partition failed')
np.savez(W/'assets/blade_partition.npz',x=x,tets=t,planes=planes,volume=vol)
