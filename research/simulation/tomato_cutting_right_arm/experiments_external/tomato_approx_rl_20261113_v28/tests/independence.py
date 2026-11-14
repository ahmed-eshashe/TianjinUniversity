from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from model import lattice
from solver import Solver
z=np.load(W/'runs/task_full_cycle/state.npz');labels=z['labels'];m=lattice('tomato');runs=[]
for impulse in [0.,-.01]:
 g=Solver(m)
 for key in g.initial:
  if key in z:getattr(g,key).assign(z[key])
 g.fixed.zero_();g.bad.zero_();v=g.v.numpy();v[labels==0,0]+=impulse;g.v.assign(v);g.step([0,0,0],200);runs.append({'x':g.x.numpy(),'v':g.v.numpy(),'bad':g.bad.numpy()})
other=labels!=0;own=labels==0;otherdx=float(np.max(np.linalg.norm(runs[0]['x'][other]-runs[1]['x'][other],axis=1)));owndx=float(np.mean(np.linalg.norm(runs[0]['x'][own]-runs[1]['x'][own],axis=1)));result={'duration_s':.02,'unforced_piece_max_change_between_matched_runs_m':otherdx,'impulsed_piece_mean_change_m':owndx,'cross_response_ratio':otherdx/max(owndx,1e-12),'bad':[r['bad'].tolist() for r in runs],'pass':bool(otherdx<2e-6 and owndx>1e-5 and not any(r['bad'].any() for r in runs)),'scope':'Same withdrawn blade-generated two-piece state in both runs. Release fixed support in both; one run adds -0.01 m/s velocity to one piece. Compare other piece between runs, rather than assuming it should stay motionless.'};(W/'reports/independence.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
