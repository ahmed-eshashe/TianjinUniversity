from pathlib import Path
import sys,os,json,time,numpy as np,traceback
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from blade_geometry import CAD
from partition_reference import integral
old=W.parent/'tomato_contact_integration_20261112_v23';s=np.load(old/'runs/culled_edge_d4_s31/trajectory.npz');cad=CAD();out=[]
for t in [.0095,.010,.01025]:
 i=round(t/.00025)-1;a=Aggregate(Body(n=2,h=.003));a.q=s['q'][i].copy();a.v=s['v'][i].copy();a.sync();z=(t-.008)/.005;shape=.5*(1+np.cos(np.pi*z));speed=-.5*np.pi/.005*np.sin(np.pi*z);T=np.array([0,.00304-.00007*shape,0]);vt=np.array([0,-.00007*speed,0])
 for tol in [.002,.0005]:
  start=time.perf_counter()
  try:r=integral(a,cad,T,cad.R,vt,relative_tol=tol);record={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in r.items()};record.update(t=t,relative_tol=tol,status='completed');print(t,tol,r['force'].sum(0),r['energy'],r['wall_s'],sum(x['leaves'] for x in r['diagnostics']),flush=True)
  except Exception as e:traceback.print_exc();record=dict(t=t,relative_tol=tol,status='failed',error=repr(e),wall_s=time.perf_counter()-start)
  out.append(record);(W/'partition_static_reference.json').write_text(json.dumps(out,indent=2))
