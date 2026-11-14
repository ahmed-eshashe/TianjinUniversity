from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from solver import Solver
from model import lattice
m=lattice();m['x'][:,1]+=.05;runs=[]
for dt,adaptive in [(.0002,True),(.00005,False)]:
 g=Solver(m,dt=dt,adaptive=adaptive);tool=g.tool.numpy();tool[:,1]=m['x'][:,1].min()-.0305;g.tool.assign(tool);g.save_initial();g.step([0,0,0],round(.02/dt));runs.append({k:getattr(g,k).numpy() for k in g.initial});runs[-1]['attempts']=g.last_attempts;runs[-1]['refinements']=g.refinements
fields=[k for k in runs[0] if k not in ['attempts','refinements']];errors={k:float(np.max(np.abs(runs[0][k].astype(float)-runs[1][k].astype(float)))) for k in fields};result={'bad':runs[0]['bad'].tolist(),'attempts':runs[0]['attempts'],'full_state_errors_vs_fresh_small_step':errors,'pass':bool(runs[0]['refinements']==2 and np.all(runs[0]['bad']==4) and max(errors.values())<1e-7),'scope':'Rejected penetration retries restore all positions, velocities, damage, paid work, forces, ledgers, pose and counters. Final unresolved penetration remains a terminal failure; no limit relaxation.'};(W/'reports/adaptive_controls.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
