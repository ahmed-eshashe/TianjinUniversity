"""Finite component coverage only; no dynamics or physical-cut pass implied."""
from pathlib import Path
import sys,json,time,traceback,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from aggregation import Aggregate
rows=[];checks={};start=time.perf_counter()
def check(name,value):checks[name]=bool(value)
try:
 for name,normal,d,front in [('intact',None,0,None),('aligned',[1,0,0],0,None),('oblique',[1,.27,.13],.001,None),('partial',[1,.27,.13],.001,([0,-1,0],0))]+[(f'corner_{d}',[1,1,1],d,None) for d in [1.3e-4,1e-5,1e-6,1e-7]]:
  b=Body(n=4);b.u=b.grid@np.array([[-.01,.003,0],[0,.005,0],[.002,0,0]]).T;b.v=np.cross([.2,.3,.1],b.grid)+[.01,-.02,.03]
  if normal is not None:b.split(normal,d,front=front)
  a=Aggregate(b);audit=a.audit();U,f=a.energy_force();direction=np.random.default_rng(37).normal(size=a.q.shape);direction/=np.linalg.norm(direction);eps=1e-8;num=(a.energy_force(a.q+eps*direction)[0]-a.energy_force(a.q-eps*direction)[0])/(2*eps);ana=-np.sum(f*direction);gradient=abs(num-ana)/max(abs(num),abs(ana),1e-10)
  R=Rotation.from_rotvec([.2,-.1,.3]).as_matrix();X=b.grid[a.masters];rotq=(X+a.q)@R.T-X+[.1,-.04,.02];objectivity=abs(a.energy_force(rotq)[0]-U)/max(U,1e-10)
  _,ff=a.body.energy_force();netf=float(np.linalg.norm(ff.sum(0)));nettorque=float(np.linalg.norm(np.cross(a.body.grid+a.body.u,ff).sum(0)))
  check(name+'_rank',audit['rank']==audit['expected_rank']);check(name+'_positive_mass',audit['min_mass_eigenvalue']>0);check(name+'_mass',a.report['mass_relative_error']<=1e-6);check(name+'_affine_projection',a.transfer['position_m']<1e-12 and a.transfer['velocity_m_s']<1e-12 and a.transfer['energy_relative']<1e-8);check(name+'_gradient',gradient<2e-5);check(name+'_objectivity',objectivity<1e-8);check(name+'_force_torque',netf<1e-10 and nettorque<1e-10)
  if name.startswith('corner'):check(name+'_corner_stability_floor',audit['linearized_stability_dt_s']>1e-4)
  rows.append({'name':name,'audit':audit,'gradient_error':gradient,'objectivity_error':objectivity,'net_force_N':netf,'net_torque_Nm':nettorque,'construction':a.report})
 b=Body(n=4);b.split([1,1,1],1e-6);a=Aggregate(b);pc,nc=b.components();ext=np.zeros_like(b.u);left=np.flatnonzero(nc==np.unique(nc)[0]);ext[left[0]]=[.1,.02,0];a.step(1e-6,ext);other=nc!=nc[left[0]];response=float(np.max(abs(a.body.v[other])));check('disconnected_fragment_independence',response<1e-14)
 # Deliberately undersized: no root for a whole fragment, kept explicitly.
 b=Body(n=2);b.split([1,1,1],1e-6);a=Aggregate(b);check('unsupported_small_fragment_not_deleted',len(a.report['unresolved_nodes'])>0 and a.report['mass_relative_error']<1e-6)
 result={'status':'component_algebra_pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'independent_other_fragment_velocity':response,'undersized_unresolved_nodes':len(a.report['unresolved_nodes']),'wall_s':time.perf_counter()-start,'dynamic_accuracy_qualified':False,'physical_cut_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'rows':rows,'wall_s':time.perf_counter()-start}
(W/'algebra.json').write_text(json.dumps(result,indent=2));print(result['status'],len(checks),[k for k,v in checks.items() if not v],flush=True)
