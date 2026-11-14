import numpy as np,json
from pathlib import Path
from scipy.linalg import expm
W=Path(__file__).resolve().parent
rows=[]
for dt in [.01,.005,.0025]:
 x=1.;v=0.;xp=vp=None;k=30.;c=3.;m=1.
 for _ in range(round(1/dt)):
  if xp is None:h=dt;xb=x;vb=v
  else:h=2*dt/3;xb=(4*x-xp)/3;vb=(4*v-vp)/3
  q=(xb+h*vb+h*c/m*xb)/(1+h*c/m+h*h*k/m);vn=(q-xb)/h;xp,vp=x,v;x,v=q,vn
 ref=expm(np.array([[0,1],[-k/m,-c/m]]))@np.array([1.,0.]);err=np.linalg.norm([x-ref[0],v-ref[1]]);rows.append(dict(dt=dt,error=float(err)))
ratios=[rows[i]['error']/rows[i+1]['error'] for i in range(2)];out=dict(oscillator=rows,refinement_ratios=ratios,passed=bool(all(3.5<r<4.5 for r in ratios)))
(W/'bdf_control.json').write_text(json.dumps(out,indent=2));print(out);assert out['passed']
