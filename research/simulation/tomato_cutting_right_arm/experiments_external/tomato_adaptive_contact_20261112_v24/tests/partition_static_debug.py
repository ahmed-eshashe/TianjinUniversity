from pathlib import Path
import sys,os,json,time,numpy as np,traceback
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from blade_geometry import CAD
from partition_gpu import ContactGPU,TriangleSurface
old=W.parent/'tomato_contact_integration_20261112_v23';state=np.load(old/'runs/culled_edge_d4_s31/trajectory.npz');refs=json.loads((W/'partition_static_reference.json').read_text());cad=CAD();rows=[]
for ref in refs:
 t=ref['t'];i=round(t/.00025)-1;a=Aggregate(Body(n=2,h=.003));a.q=state['q'][i].copy();a.v=state['v'][i].copy();a.sync();s=TriangleSurface(a);g=ContactGPU(a,s,cad,[0,.00304,0],[0,-.00007,0],relative_tol=ref['relative_tol']);g.clock.assign(np.array([t]));start=time.perf_counter()
 try:
  o=g.observe();f=g.external.numpy()[:g.n];rf=np.array(ref['force']);r={'t':t,'tol':ref['relative_tol'],'status':'completed','wall_s':time.perf_counter()-start,'force_N':f.sum(0).tolist(),'force_error_N':float(np.linalg.norm(f-rf,axis=1).sum()),'reference_force_N':rf.sum(0).tolist(),'U_error_J':o['contact_energy']-ref['energy'],'max_leaves':int(g.leaves.numpy().max()),'leaves':int(g.leaves.numpy().sum()),'queries':int(g.queries.numpy().sum())};print(r,flush=True)
 except Exception as e:
  counts=g.leaves.numpy();ii=np.flatnonzero(counts>=g.capacity);print('FAILED PAIRS',ii,flush=True);np.savez(W/'reports'/('failed_t'+str(t)+'_tol'+str(ref['relative_tol'])+'.npz'),counts=counts,indices=ii,B=g.Bs.numpy()[ii],values=g.vals.numpy()[ii],depths=g.depths.numpy()[ii]);traceback.print_exc();r={'t':t,'tol':ref['relative_tol'],'status':'failed','error':repr(e)}
 rows.append(r);(W/'partition_static_gpu_debug.json').write_text(json.dumps(rows,indent=2))
