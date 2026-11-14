from pathlib import Path
import sys,numpy as np,json
from scipy.interpolate import BSpline
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from basis_volume_guard import certificate
from block_basis import block_basis
from reference import block
checks={};out={};X=block(8,.0015);_,_,_,grid,meta=block_basis(X,.0015,.003)
for name,F,should in [('identity',np.eye(3),True),('compression',np.diag([1,.9,1]),True),('collapse',np.diag([1,.05,1]),False),('inversion',np.diag([1,-1,1]),False)]:
 c=certificate(X,grid@F.T);checks[name]=c['passed']==should;out[name]=c
X=block(40,.0015);_,_,_,grid,meta=block_basis(X,.0015,.003);projections=[]
for knots,axis in zip(meta['knots'],meta['particle_axes']):
 A=BSpline(knots,np.eye(len(knots)-3),2)(axis);projections.append(np.linalg.solve(A.T@A,A.T))
def recover(x):
 v=x.reshape(40,40,40,3);v=np.einsum('ai,ijkd->ajkd',projections[0],v);v=np.einsum('bj,ajkd->abkd',projections[1],v);return np.einsum('ck,abkd->abcd',projections[2],v).reshape(-1,3)
with np.load(W/'runs/mechanics_selected/compression_shared_times.npz') as z:
 cases=[]
 for key in ['x','x_half']:
  for idx,x in enumerate(z[key]):
   c=certificate(X,recover(x));c.update(case=key,sample=idx+1);cases.append(c)
checks['whole_compression_window']=all(c['passed'] for c in cases);out['compression']={'samples':len(cases),'minJ_lower_bound':min(c['minJ_lower_bound'] for c in cases),'maxJ_upper_bound':max(c['maxJ_upper_bound'] for c in cases),'trace':cases}
with np.load(W/'runs/mechanics_selected/compression.npz') as z:out['recovered_q_max_error']=float(abs(recover(z['x'])-z['q']).max());checks['saved_reconstruction']=out['recovered_q_max_error']<1e-10
result={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':out,'new_simulation':False};(W/'basis_volume_controls.json').write_text(json.dumps(result,indent=2));print(json.dumps({'checks':checks,'compression_bound':{k:v for k,v in out['compression'].items() if k!='trace'}},indent=2))
