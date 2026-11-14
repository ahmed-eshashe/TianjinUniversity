import numpy as np,json
from pathlib import Path
p=Path(__file__).parent;a=np.load(p/'extended_trajectory.npz');b=np.load(p.parent/'disect_completion_20261108_v07/window_reference_trajectory.npz');rows=[]
for j,t in enumerate(a['t']):
 i=int(np.argmin(abs(b['t']-t)))
 if abs(b['t'][i]-t)>1e-10 or t==0:continue
 row=dict(time_s=float(t))
 for k in ['x','v','force']:
  delta=a[k][j]-b[k][i];row[k+'_max_difference']=float(np.linalg.norm(delta,axis=-1).max());row[k+'_relative_l2']=float(np.linalg.norm(delta)/max(np.linalg.norm(b[k][i]),1e-30))
 rows.append(row)
out=dict(scope='Matched 1ms samples only, no cutting or damage; force relative L2 diagnostic',rows=rows)
(p/'extended_comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
