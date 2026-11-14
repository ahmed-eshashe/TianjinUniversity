from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body,strain_audit
from aggregation import Aggregate
checks={};rows=[];start=time.perf_counter()
def check(k,v,d=None):
 checks[k]=bool(v)
 if not v:raise AssertionError((k,d))
try:
 for name,n,d,front in [('intact',None,0,None),('aligned',[1,0,0],0,None),('oblique',[1,.27,.13],.001,None),('partial_oblique',[1,.27,.13],.001,([0,-1,0],0)),('corner130um',[1,1,1],1.3e-4,None),('corner10um',[1,1,1],1e-5,None),('corner1um',[1,1,1],1e-6,None),('corner0p1um',[1,1,1],1e-7,None)]:
  b=Body();b.u=b.grid@np.array([[-.01,.003,0],[0,.005,0],[.002,0,0]]).T;b.v=b.grid@np.array([[.2,.1,0],[0,.1,.03],[0,0,-.1]]).T
  if n is not None:b.split(n,d,front=front)
  base=strain_audit(b);a=Aggregate(b);r=a.audit();row={'name':name,'base':base,'aggregate':r,'construction':a.report};rows.append(row);print(name,r,a.transfer,flush=True)
  check(name+'_rank',r['rank']==r['expected_rank'],r);check(name+'_mass',a.report['mass_relative_error']<1e-6);check(name+'_affine_transfer',a.transfer['position_m']<1e-12 and a.transfer['velocity_m_s']<1e-12 and a.transfer['energy_relative']<1e-8,row);check(name+'_positive_mass',r['min_mass_eigenvalue']>0)
  U,f=a.energy_force();q=np.random.default_rng(37).normal(size=a.q.shape);q/=np.linalg.norm(q);eps=1e-8;num=(a.energy_force(a.q+eps*q)[0]-a.energy_force(a.q-eps*q)[0])/(2*eps);ana=-np.sum(f*q);err=abs(num-ana)/max(abs(num),abs(ana),1e-10);row['gradient_relative']=err;check(name+'_energy_gradient',err<2e-5,err)
  if name.startswith('corner'):check(name+'_corner_floor',r['linearized_stability_dt_s']>1e-4,r)
  (W/'early_gate.partial.json').write_text(json.dumps({'checks':checks,'rows':rows},indent=2))
 result={'status':'pass_initial_aggregation_algebra','checks':checks,'rows':rows,'wall_s':time.perf_counter()-start,'dynamics_and_speed_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'failed','exception':repr(e),'checks':checks,'rows':rows,'wall_s':time.perf_counter()-start,'dynamics_and_speed_qualified':False}
(W/'early_gate.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True);sys.exit(0 if result['status'].startswith('pass') else 1)
