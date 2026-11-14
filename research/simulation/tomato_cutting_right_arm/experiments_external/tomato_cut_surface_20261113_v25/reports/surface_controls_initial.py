from pathlib import Path
import os,sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from fast_aggregation import Aggregate
from poly_surface import Surface
checks={};rows=[]
for name,front in [('intact','none'),('partial',([0,1,0],0.)),('full',None)]:
 b=Body(n=2,h=.003)
 if name!='intact':b.split([1.,0,0],.0001,front=front)
 a=Aggregate(b);start=time.perf_counter();s=Surface(a);wall=time.perf_counter()-start;area=s.tri_area.sum();expected=6*.006**2+(0 if name=='intact' else (.006**2 if name=='partial' else 2*.006**2));checks[name+'_area']=abs(area-expected)<1e-12
 checks[name+'_volume']=abs(s.metadata['volume_coverage_m3']-b.V.sum())<b.V.sum()*1e-10
 affine=np.array([[.01,.002,0],[.001,-.002,.001],[0,.001,.003]]);a.q=b.grid[a.masters]@affine.T+[.001,.002,-.001];a.v=b.grid[a.masters]@affine.T*.1;a.sync();x=s.positions(a.q);checks[name+'_affine']=np.max(abs(x-(s.X+s.X@affine.T+[.001,.002,-.001])))<1e-12
 F=np.broadcast_to(np.eye(3)+affine,(len(s.volume_tets),3,3));checks[name+'_deformed_volume']=abs(np.abs(np.linalg.det(s.tets(a.q)[:,1:]-s.tets(a.q)[:,:1])).sum()/6-b.V.sum()*np.linalg.det(np.eye(3)+affine))<1e-14
 forces=np.random.default_rng(23).normal(size=x.shape)*1e-5;dq=np.random.default_rng(24).normal(size=a.q.shape)*1e-5;checks[name+'_virtual_work']=abs(np.sum(forces*(s.Q@dq))-np.sum(s.pullback(forces)*dq))<1e-16
 _,nodecomp=b.components();checks[name+'_components']=len(np.unique(nodecomp))==(2 if name=='full' else 1)
 if name=='full':
  a.q[:]=0;a.q[b.grid[a.masters,0]>.0001,0]=.001;a.sync();mapped=s.positions(a.q);centers=np.mean(s.triangles,axis=1);mask=np.abs(centers[:,0]-.0001)<1e-12;norm=s.ref_normals[mask,0];faceworld=mapped.reshape(-1,3,3)[mask].mean(1);checks['separate_faces_independent']=np.max(abs(faceworld[norm>0,0]-.0001))<1e-10 and np.max(abs(faceworld[norm<0,0]-.0011))<1e-10
 rows.append({'case':name,'expected_area':expected,'area':area,'wall_s':wall,'coupled_mass':a.coupled,**s.metadata})
r={'checks':{k:bool(v) for k,v in checks.items()},'passed':all(checks.values()),'cases':rows,'physical_cut':False,'note':'Splits are geometry controls only. No fracture work or physical slice is claimed.'};(W/'reports/surface_controls.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
