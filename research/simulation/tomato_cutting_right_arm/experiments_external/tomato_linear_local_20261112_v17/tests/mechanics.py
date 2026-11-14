from pathlib import Path
import sys,time,json,traceback,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from linear_reference import Body,energy_stress,strain_audit
from linear_gpu import GPU
checks={};results={};start=time.perf_counter()
def check(k,v,d=None):
 checks[k]=bool(v)
 if not v:raise AssertionError((k,d))
try:
 b=Body();A=np.array([[.98,.02,0],[0,1.01,.01],[0,0,1.002]]);b.u=b.grid@(A-np.eye(3)).T+[.001,-.002,.001];x,v,F=b.fields();check('mass',abs(b.mass.sum()-.001728)<1e-14);check('partition',np.max(abs(b.N.sum(1)-1))<1e-12 and np.max(abs(b.G.sum(1)))<1e-10);check('affine_position',np.max(abs(x-(b.X@A.T+[.001,-.002,.001])))<1e-12);check('affine_strain',np.max(abs(F-A))<1e-12)
 U,f=b.energy_force();exact=b.V.sum()*energy_stress(A[None,:,:],b.mu,b.lam)[0][0];check('affine_energy',abs(U-exact)<1e-12);q=np.random.default_rng(7).normal(size=b.u.shape);q/=np.linalg.norm(q);eps=1e-8;num=(b.energy_force(b.u+eps*q)[0]-b.energy_force(b.u-eps*q)[0])/(2*eps);ana=-np.sum(f*q);err=abs(num-ana)/max(abs(num),abs(ana),1e-10);results['gradient_relative']=err;check('energy_gradient',err<2e-5,err);check('force_balance',np.linalg.norm(f.sum(0))<1e-10);check('torque_balance',np.linalg.norm(np.cross(b.grid+b.u,f).sum(0))<1e-10)
 R=Rotation.from_rotvec([.2,-.3,.1]).as_matrix();o=b.clone();o.u=(b.grid+b.u)@R.T-b.grid;check('objectivity',abs(o.energy_force()[0]-U)<1e-12)
 b.v=np.random.default_rng(8).normal(size=b.v.shape)*.01;c=b.clone();g=GPU(b.clone(),dt=1e-6)
 for _ in range(10):c.step(1e-6)
 g.step(10);out=g.export();diff={k:float(np.max(abs(a-d))) for k,a,d in zip(['x','v','F'],c.fields(),out.fields())};results['CPU_GPU']=diff;check('CPU_GPU_fields',diff['x']<1e-6 and diff['v']<1e-4 and diff['F']<1e-4,diff)
 cases=[('intact',None,0,None),('aligned',[1,0,0],0,None),('oblique',[1,.27,.13],.001,None),('oblique2',[1,.51,.31],-.0007,None),('diagonal',[1,1,1],.00013,None),('partial',[1,0,0],0,([0,-1,0],0)),('partial_oblique',[1,.27,.13],.001,([0,-1,0],0)),('sliver10um',[1,1,1],1e-5,None),('sliver1um',[1,1,1],1e-6,None)]
 for name,n,d,front in cases:
  o=b.clone();transfer=None if n is None else o.split(n,d,front=front);audit=strain_audit(o);results[name]={'transfer':transfer,'audit':audit};check(name+'_rank',audit['rank']==audit['expected_rank'],audit);check(name+'_components',audit['components']==(1 if front is not None or n is None else 2),audit);o.save(W/'states'/f'{name}.npz');print(name,audit,flush=True)
 # Exact continuation data, not just JSON metadata.
 restored=Body.restore(W/'states/oblique.npz');loaded=Body.restore(W/'states/oblique.npz');g1=GPU(restored,dt=1e-6);g2=GPU(loaded,dt=1e-6);g1.step(20);g2.step(20);g1.export();g2.export();check('restart_arrays',np.array_equal(restored.u,loaded.u) and np.array_equal(restored.v,loaded.v) and np.array_equal(restored.codes,loaded.codes));results['restart_max_x']=float(np.max(abs(restored.fields()[0]-loaded.fields()[0])))
 # Localized force probe; contact omitted on purpose, so this is an algebraic
 # independence unit control, not the physical post-withdrawal contact gate.
 o=Body();o.split([1,.27,.13],.001);pl,nl=o.components();one=nl==nl[0];force=np.zeros_like(o.u);index=np.where(one)[0][0];force[index,2]=.01;control=GPU(o.clone(),dt=2e-6);probe=GPU(o.clone(),dt=2e-6,external=force);control.step(1000);probe.step(1000);control.export();probe.export();dv=probe.body.v-control.body.v;untouched=float(np.max(np.linalg.norm(dv[~one],axis=1)));touched=float(np.max(np.linalg.norm(dv[one],axis=1)));ratio=untouched/max(touched,1e-12);results['independence']={'untouched_m_s':untouched,'touched_m_s':touched,'ratio':ratio,'scope':'geometry fixture; no contact or fracture law'};check('independent_fragment',ratio<=.01 and touched>1e-5,ratio)
 result={'status':'pass_initial_component_controls','checks':checks,'results':results,'wall_s':time.perf_counter()-start}
except Exception as e:traceback.print_exc();result={'status':'failed','exception':repr(e),'checks':checks,'results':results,'wall_s':time.perf_counter()-start}
(W/'mechanics.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True);sys.exit(0 if result['status'].startswith('pass') else 1)
