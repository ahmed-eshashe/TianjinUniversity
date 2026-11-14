from pathlib import Path
import os,sys,json,numpy as np,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from fast_aggregation import Aggregate
from poly_surface import Surface
from reference_v17 import moments
b=Body.restore(W/'states/tomato_baseline.npz');a=Aggregate(b);start=time.perf_counter();s=Surface(a);wall=time.perf_counter()-start;z=np.load(W/'states/tomato_baseline_exterior.npz');tri=z['vertices'][z['triangles']];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1).sum()/2;checks={'exterior_area':abs(s.tri_area.sum()/area-1)<1e-8,'volume_coverage':abs(s.metadata['volume_coverage_m3']/b.V.sum()-1)<1e-10,'finite_surface':np.isfinite(s.X).all()};rows=[]
for i,(normal,off) in enumerate([([1,0,0],.00013),([0,0,1],.00413)]):
 candidate=b.clone();before=candidate.metrics();candidate.split(normal,off,cut_id=i);actual=np.array([moments(p)[0] for p in candidate.polys]);rel=float(np.sum(abs(actual-candidate.V))/candidate.V.sum());checks[f'cut_{i}_independent_volume']=rel<1e-6;checks[f'cut_{i}_mass']=abs(candidate.mass.sum()/b.mass.sum()-1)<1e-6;rows.append(dict(cut=i,independent_local_volume_relative=rel,geometry_only=True,regions=len(actual),update=candidate.last_update));candidate.save(W/'states'/f'tomato_geometric_audit_{i}.npz')
out=dict(passed=all(checks.values()),checks={k:bool(v) for k,v in checks.items()},surface=s.metadata,original_area_m2=float(area),boundary_build_s=wall,geometric_controls=rows,physical_cut=False,rl_ready=False);(W/'reports/tomato_surface_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
