from pathlib import Path
import os,sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate as Intact
from local_continuity import Aggregate as Cracked
from surface_cache import cached_surface
from poly_surface import Surface
from blade_geometry import CAD
from convex_guard_gpu import GPUConvexGuard
from compact_proof import CompactProof
from hierarchical_contact_gpu import ContactGPU,corner_frame
from resident_clearance import ResidentProof
from scipy.spatial.transform import Rotation
cad=CAD();rng=np.random.default_rng(942);rows=[]
for kind,path,A in [('tomato',Path('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz'),Intact),('cracked',W/'runs/space_guard_matched_3ms/last_accepted.npz',Cracked)]:
 a=A(Body.restore(path));s=cached_surface(a,W/'states/tomato_surface_cache.npz') if kind=='tomato' else Surface(a);g=ContactGPU(a,s,cad,np.zeros(3),np.zeros(3),exact_interior=True,grid_query=True,face_capacity=len(s.triangles),capacity=4096,candidate_capacity=65536);proof=CompactProof(a,s,GPUConvexGuard(cad));resident=ResidentProof(g,proof)
 for i in range(16):
  R=Rotation.random(random_state=rng).as_matrix();T=a.body.X.mean(0)-R@cad.vertices.mean(0)+rng.normal(size=3)*(.1 if i%4==0 else .002)
  q=a.q+a.body.grid[a.masters]@rng.normal(size=(3,3))*.01+1e-7*rng.normal(size=a.q.shape);pad=np.zeros((g.ncap,3),np.float32);pad[:g.n]=q;g.q.assign(pad);g.R=R;g.maxspeed.zero_();g.bad.zero_();resident.cursor.zero_()
  wp.launch(corner_frame,g.href.size,[wp.mat33d(R),wp.vec3d(T),wp.vec3d(0.),wp.float64(g.load),wp.float64(g.hold),g.clock,g.hptr,g.hids,g.hw,g.href,g.q,g.hcorners,g.toolpose]);resident.certify(0)
  actual=set(resident.active_ids.numpy()[:int(resident.active_count.numpy()[0])]);local=(proof.tets0+(proof.Q@pad[:g.n].astype(float)).reshape(-1,4,3)-T)@R;mask=np.all((local.max(1)+1e-12>=cad.vertices.min(0))&(local.min(1)-1e-12<=cad.vertices.max(0)),axis=1);expected=set(np.flatnonzero(mask));missing=sorted(expected-actual);extra=sorted(actual-expected);bad=int(g.bad.numpy()[0]);row=dict(kind=kind,index=i,expected=len(expected),actual=len(actual),missing=missing,extra=extra,stopped=bool(bad));rows.append(row);assert not missing and not extra,row
 # Test rejected-action rollback through the real transactional runtime.
 g.q.assign(np.pad(a.q.astype(np.float32),((0,g.ncap-len(a.q)),(0,0))));g.R=cad.R;g.T0=np.array([2.,2.,2.]);g.travel=np.array([0.,-1.,0.]);g.bad.zero_();g.clock.assign(np.array([0.]));g.graphs.clear();resident=ResidentProof(g,proof)
 q0=g.q.numpy().copy();v0=g.vh.numpy().copy();ledger={k:v.numpy().copy() for k,v in g.ca.items() if k in g.tx};rejected=False
 try:resident.step_async(10);g.finish()
 except ValueError:rejected=True
 checks=dict(rejected=rejected,q=np.array_equal(q0,g.q.numpy()),v=np.array_equal(v0,g.vh.numpy()),ledger=all(np.array_equal(v,g.ca[k].numpy()) for k,v in ledger.items()),no_pending=g.pending is None)
 rows.append(dict(kind=kind,rollback=checks));assert all(checks.values()),checks
report=dict(passed=True,coverage_cases=32,rollback_cases=2,has_clear=any(not r.get('stopped',True) for r in rows),has_reject=any(r.get('stopped',False) for r in rows),rows=rows);(W/'reports/resident_clearance_controls.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2));assert report['has_clear'] and report['has_reject']
