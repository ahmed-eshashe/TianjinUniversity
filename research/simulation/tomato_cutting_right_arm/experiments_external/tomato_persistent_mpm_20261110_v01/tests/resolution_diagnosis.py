from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference import block
from backend import Backend
R=W/'runs/resolution_diagnosis';R.mkdir(exist_ok=False);result=[]
for n,h,spacing,dt in [(20,.006,.003,2.5e-5),(40,.003,.0015,1.25e-5)]:
 X=block(n,spacing);b=Backend(X,spacing=spacing,h=h);v=np.cross(np.tile([0,0,1.],(len(X),1)),X);b.set_state(v=v);s=b.state();L0=b.mass*np.cross(s['x'],s['v']).sum(0);peak=0;t=time.monotonic()
 rows=[]
 for _ in range(20):
  b.step(dt,round(.0005/dt));s=b.check();L=b.mass*np.cross(s['x'].astype(float),s['v'].astype(float)).sum(0);err=np.linalg.norm(L-L0)/np.linalg.norm(L0);peak=max(peak,err);rows.append([b.sim_time,*L,err])
 np.savetxt(R/f'spin_{n}.csv',rows,delimiter=',');b.save(R/f'spin_{n}.npz');result.append({'n':n,'particles':len(X),'h':h,'dt':dt,'angular_relative_error':float(peak),'wall_s':time.monotonic()-t})
(R/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
