"""Compare conservative parent search with original exhaustive face framing."""
from pathlib import Path
import os,sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate as Intact
from local_continuity import Aggregate as Fractured
from surface_cache import cached_surface
from poly_surface import Surface
from blade_geometry import CAD
from hierarchical_contact_gpu import ContactGPU,corner_frame,parent_faces,exact_active_frame
from parallel_partition_gpu import frame
from scipy.spatial.transform import Rotation
cad=CAD();rng=np.random.default_rng(738);rows=[]
for kind,path,Aggregate in [('tomato',Path('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz'),Intact),('cracked',W/'runs/earlier_hold/last_accepted.npz',Fractured)]:
 a=Aggregate(Body.restore(path));b=a.body;s=cached_surface(a,W/'states/tomato_surface_cache.npz') if kind=='tomato' else Surface(a)
 g=ContactGPU(a,s,cad,np.zeros(3),np.zeros(3),exact_interior=True,grid_query=True,capacity=4096,face_capacity=len(s.triangles),candidate_capacity=65536)
 orig=wp.empty(g.nfaces,dtype=wp.mat33d,device='cuda:0');x=wp.empty_like(orig);v=wp.empty_like(orig);pose=wp.empty(2,dtype=wp.vec3d,device='cuda:0')
 for i in range(40):
  R=Rotation.random(random_state=rng).as_matrix();T=b.X.mean(0)+rng.uniform(-1,1,3)*np.ptp(s.X,axis=0)*.6-R@cad.vertices.mean(0)
  affine=rng.normal(size=(3,3))*.02;dq=b.grid[a.masters]@affine.T;noise=rng.normal(size=a.q.shape)*1e-6;q=np.asarray(a.q+dq+noise,dtype=np.float32);g.q.assign(q);g.bad.zero_();g.hcount.zero_();g.face_count.zero_()
  for fn,n,args in [(corner_frame,g.href.size,[wp.mat33d(R),wp.vec3d(T),wp.vec3d(0.),wp.float64(g.load),wp.float64(g.hold),g.clock,g.hptr,g.hids,g.hw,g.href,g.q,g.hcorners,g.toolpose]),(parent_faces,g.nfaces,[g.hparent,g.howner,g.hcorners,g.hroundoff,wp.vec3d(cad.vertices.min(0)),wp.vec3d(cad.vertices.max(0)),g.hcount,g.hfaces,g.bad]),(exact_active_frame,g.nfaces,[wp.mat33d(R),g.toolpose,g.sptr,g.sids,g.sw,g.reference,g.q,g.vh,g.xx,g.vv,g.local,g.hcount,g.hfaces,wp.vec3d(cad.vertices.min(0)),wp.vec3d(cad.vertices.max(0)),g.face_count,g.face_ids,g.bad]),(frame,g.nfaces,[wp.mat33d(R),wp.vec3d(T),wp.vec3d(0.),wp.float64(g.load),wp.float64(g.hold),g.clock,g.sptr,g.sids,g.sw,g.reference,g.q,g.vh,x,v,orig,pose])]:wp.launch(fn,n,args)
  allx=orig.numpy().reshape(-1,3,3);mask=np.all((allx.max(1)>=cad.vertices.min(0))&(allx.min(1)<=cad.vertices.max(0)),axis=1);expected=set(np.flatnonzero(mask));actual=set(g.face_ids.numpy()[:int(g.face_count.numpy()[0])]);missing=sorted(expected-actual);extra=sorted(actual-expected)
  rows.append(dict(kind=kind,case=i,expected=len(expected),actual=len(actual),broad=int(g.hcount.numpy()[0]),missing=missing,extra=extra,bad=int(g.bad.numpy()[0])))
  assert not missing and not extra and not g.bad.numpy()[0],rows[-1]
 print(kind,'passed',flush=True)
report=dict(passed=True,cases=len(rows),scope='80 varied poses, rotations and small deformations on intact tomato and actual paid crack. Exact original all-face CAD-AABB search versus conservative hierarchical search. No performance or full-cut claim.',rows=rows);(W/'reports/hierarchy_coverage.json').write_text(json.dumps(report,indent=2))
