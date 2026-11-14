from pathlib import Path
import sys,json,time,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from local_reference import LocalBody,energy_stress
from local_gpu import GPU
checks={};results={};start=time.perf_counter()
def check(k,v,detail=None):
 checks[k]=bool(v)
 if not v:raise AssertionError((k,detail))
def rank_audit(b):
 B=np.zeros((6*len(b.X),3*len(b.u)))
 for p in range(len(b.X)):
  for k,a in enumerate(b.ids[p]):
   x,y,z=b.G[p,k];j=3*a;r=6*p
   B[r,j]+=x;B[r+1,j+1]+=y;B[r+2,j+2]+=z
   B[r+3,j]+=y;B[r+3,j+1]+=x;B[r+4,j]+=z;B[r+4,j+2]+=x;B[r+5,j+1]+=z;B[r+5,j+2]+=y
 B*=np.repeat(np.sqrt(b.V),6)[:,None];s=np.linalg.svd(B,compute_uv=False);rank=int(np.sum(s>s[0]*1e-9));components=len(np.unique(b.components()));return {'rank':rank,'expected_rank':3*len(b.u)-6*components,'nodes':len(b.u),'components':components,'nullity':3*len(b.u)-rank}
try:
 b=LocalBody();check('partition',np.max(abs(b.N.sum(1)-1))<1e-14 and np.max(abs(b.G.sum(1)))<1e-12)
 check('mass',abs(b.mass.sum()-.001728)<1e-14)
 A=np.array([[.98,.02,0],[0,1.01,.01],[0,0,1.002]]);b.u=b.grid@(A-np.eye(3)).T+np.array([.001,-.002,.001]);x,v,F=b.fields();check('affine_position',np.max(abs(x-(b.X@A.T+[.001,-.002,.001])))<1e-14);check('affine_strain',np.max(abs(F-A))<1e-13)
 U,f=b.energy_force();expected=b.V.sum()*energy_stress(A[None,:,:],b.mu,b.lam)[0][0];check('affine_energy',abs(U-expected)<1e-12)
 q=np.random.default_rng(7).normal(size=b.u.shape);q/=np.linalg.norm(q);eps=1e-8;num=(b.energy_force(b.u+eps*q)[0]-b.energy_force(b.u-eps*q)[0])/(2*eps);ana=-np.sum(f*q);err=abs(num-ana)/max(abs(num),abs(ana),1e-10);check('energy_gradient',err<2e-5,err);results['energy_gradient_relative']=err
 check('internal_force_balance',np.linalg.norm(f.sum(0))<1e-10);check('internal_torque_balance',np.linalg.norm(np.cross(b.grid+b.u,f).sum(0))<1e-10)
 R=Rotation.from_rotvec([.2,-.3,.1]).as_matrix();rot=b.clone();rot.u=(b.grid+b.u)@R.T-b.grid;check('objectivity',abs(rot.energy_force()[0]-U)<1e-12)
 v=np.random.default_rng(8).normal(size=b.v.shape)*.01;b.v=v
 c=b.clone();g=GPU(b.clone(),dt=1e-6)
 for _ in range(10):c.step(1e-6)
 g.step(10);gc=g.export();ce=c.fields();ge=gc.fields();err={k:float(np.max(abs(a-d))) for k,a,d in zip(['x','v','F'],ce,ge)};results['CPU_GPU']=err;check('CPU_GPU_fields',err['x']<1e-6 and err['v']<.0001 and err['F']<.0001,err)
 clean=LocalBody();forrank=rank_audit(clean);results['intact_rank']=forrank;check('intact_no_hourglass',forrank['rank']==forrank['expected_rank'],forrank)
 # Cut-rank tests are prospective controls, not claimed physical fracture.
 for name,normal,plane,depth in [('full_aligned',[1,0,0],0,1),('partial_aligned',[1,0,0],0,0),('full_offset',[1,0,0],.001,1),('full_oblique',[1,.27,.13],.001,1)]:
  body=LocalBody();body.u=b.u.copy();body.v=b.v.copy();code=np.where(body.X@normal<plane,1,2)
  if depth==0:code=np.where(body.X[:,1]>0,code,0)
  _,err=body.topology(code);r=rank_audit(body);results[name]={'transfer':err,'rank':r};check(name+'_no_hourglass',r['rank']==r['expected_rank'],r);check(name+'_components',r['components']==(1 if depth==0 else 2),r)
 result={'status':'pass','checks':checks,'results':results,'wall_s':time.perf_counter()-start}
except Exception as e:
 import traceback;traceback.print_exc();result={'status':'failed','exception':repr(e),'checks':checks,'results':results,'wall_s':time.perf_counter()-start}
(W/'preflight.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));sys.exit(0 if result['status']=='pass' else 1)
