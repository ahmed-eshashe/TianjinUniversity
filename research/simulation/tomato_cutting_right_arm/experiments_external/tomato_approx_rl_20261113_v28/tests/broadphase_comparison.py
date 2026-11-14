from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from model import lattice
from solver import Solver
z=np.load(W/'runs/task_partial_state.npz');runs=[]
for interval in [1,10]:
 g=Solver(lattice('tomato'),grid_interval=interval)
 for key in z:getattr(g,key).assign(z[key])
 g.graph(200);start=time.perf_counter()
 for k in range(30):g.step([0,-.0015*abs(np.sin(k*.4)),.15*np.sin(k*.4)])
 elapsed=time.perf_counter()-start;runs.append({k:getattr(g,k).numpy() for k in ['x','v','alive','paid','ledger','peak','bad']});runs[-1]['wall_s']=elapsed
r={'exact_grid_wall_s':runs[0]['wall_s'],'guarded_grid_wall_s':runs[1]['wall_s'],'position_max_error_m':float(np.max(np.linalg.norm(runs[0]['x']-runs[1]['x'],axis=1))),'velocity_rms_error_m_s':float(np.sqrt(np.mean((runs[0]['v']-runs[1]['v'])**2))),'same_broken_bonds':bool(np.array_equal(runs[0]['alive'],runs[1]['alive'])),'work_relative_error':float(abs(runs[0]['paid'].sum()-runs[1]['paid'].sum())/runs[0]['paid'].sum()),'peak_relative_error':float(abs(runs[0]['peak'][0]-runs[1]['peak'][0])/max(runs[0]['peak'][0],1e-8)),'bad':[x['bad'].tolist() for x in runs]};r['pass']=bool(r['position_max_error_m']<1e-6 and r['same_broken_bonds'] and r['work_relative_error']<1e-4 and not any(x['bad'].any() for x in runs));(W/'reports/broadphase_comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
