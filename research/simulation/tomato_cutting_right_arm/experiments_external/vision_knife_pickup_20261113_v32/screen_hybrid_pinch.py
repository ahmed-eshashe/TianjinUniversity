"""Static friction-cone diagnostic of recorded handle contacts, not a pickup pass."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import linprog
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent
trace=json.loads((W/'datasets/hybrid_v01_fine_diagnostic/validation_001/trajectory.json').read_text());r=min(trace,key=lambda r:abs(r['sim_s']-8.5));kp=np.array(r['knife_pose']);rot=Rotation.from_quat(kp[3:]).as_matrix();com=kp[:3]+rot@np.array([-.14077148591,.00592554054,.00144075624]);contacts=r['contacts'];results=[]
for mu in [.2,.3,.4,.6]:
 rays=[];groups=[]
 for ci,c in enumerate(contacts):
  normal=-np.array(c['normal']);t=np.cross(normal,[0,0,1]);t/=np.linalg.norm(t);b=np.cross(normal,t);p=np.array(c['point'])
  for angle in np.linspace(0,2*np.pi,24,endpoint=False):
   f=normal+mu*(t*np.cos(angle)+b*np.sin(angle));rays.append(np.r_[f,np.cross(p-com,f)]);groups.append(ci)
 A=np.array(rays).T;G=np.zeros((len(contacts),len(rays)))
 for i,ci in enumerate(groups):G[ci,i]=1
 rhs=np.array([0,0,.1750893633*9.81,0,0,0])
 fit=linprog(np.ones(len(rays)),A_ub=G,b_ub=np.full(len(contacts),8.),A_eq=A,b_eq=rhs,bounds=(0,None),method='highs')
 result=dict(mu=mu,feasible=fit.success)
 if fit.success:result['normal_N']={c['part']:float(v) for c,v in zip(contacts,G@fit.x)}
 results.append(result)
(W/'reports/hybrid_pinch_balance_screen.json').write_text(json.dumps(dict(scope='Necessary point-contact static equilibrium; not a dynamics/retention guarantee',results=results),indent=2));print(results)
