from pathlib import Path
import os,sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from blade_geometry import CAD
from grid_cad_candidates import GridCandidates,query_grid
cad=CAD();g=GridCandidates(cad);print(json.dumps(g.report),flush=True);rng=np.random.default_rng(1729);z=np.load(W/'assets/blade_partition.npz');tets=z['x'][z['tets']];bary=rng.exponential(size=(20,len(tets),4));bary/=bary.sum(-1,keepdims=True);points=np.einsum('nki,kij->nkj',bary,tets).reshape(-1,3)
# Include index-cell boundaries and CAD vertices with tiny inward shifts.
center=tets.mean(1);points=np.concatenate([points,center, center+(np.round(center/g.h)*g.h-center)*.01]);dpoints=wp.array(points,dtype=wp.vec3d,device='cuda:0');phi=wp.empty(len(points),dtype=wp.float64,device='cuda:0');normal=wp.empty(len(points),dtype=wp.vec3d,device='cuda:0');wp.launch(query_grid,len(points),[cad.tri,g.ptr,g.ids,wp.vec3d(g.origin),wp.vec3i(g.shape),g.h,dpoints,phi,normal]);candidate=phi.numpy();reference=cad.query(points,R=np.eye(3),cpu=True);errors=np.abs(candidate+np.abs(reference['phi']));checks=dict(original_CAD_distance=float(errors.max())<1e-10,finite=bool(np.isfinite(normal.numpy()).all()));out=dict(passed=all(checks.values()),checks=checks,points=len(points),maximum_distance_error_m=float(errors.max()),index=g.report,scope='Exact original-triangle distance after conservative candidate exclusion. Mathematical Lipschitz coverage plus independent CPU queries. Not an interpolated SDF.');(W/'reports/grid_candidates_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
