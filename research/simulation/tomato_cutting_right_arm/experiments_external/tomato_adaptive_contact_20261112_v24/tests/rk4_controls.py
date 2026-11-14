from pathlib import Path
import os,sys,time,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.enable_backward=False;wp.config.kernel_cache_dir=str(W/'cache/warp')
from compiled_body import Body
from fast_aggregation import Aggregate
from rk4_contact_gpu import ContactGPU,TriangleSurface
from blade_geometry import CAD,certify
from parallel_reference import integral
cad=CAD();a=Aggregate(Body(n=2,h=.003));s=TriangleSurface(a);fixed=np.isclose(a.body.grid[:,1],-.003);g=ContactGPU(a,s,cad,[0,.00299,0],[0,0,.000025],fixed=fixed);c=Aggregate(Body(n=2,h=.003));support=np.zeros(3);impulse=np.zeros(3);work=diss=0.;errors=[];checks={};dt=g.dt
for step in range(12):
 q0=c.q.copy();v0=c.v.copy();t0=step*dt;dq=np.zeros_like(q0);dv=np.zeros_like(v0)
 for weight,beta,last,frac in [(1/6,.5,False,0),(1/3,.5,False,.5),(1/3,1,False,.5),(1/6,1,True,1)]:
  T,vt=g.pose(t0+frac*dt);law=integral(c,cad,T,g.R,vt);force=c.energy_force(c.q)[1]+law['force'];acc=c.solve(force);acc[fixed]=0;vv=c.v.copy();dq+=weight*vv;dv+=weight*acc;support-=dt*weight*force[fixed].sum(0);impulse+=dt*weight*law['force'].sum(0);work+=dt*weight*law['tool_power'];diss+=dt*weight*law['friction_power']
  c.q=q0+dt*(dq if last else beta*vv);c.v=v0+dt*(dv if last else beta*acc);c.q[fixed]=q0[fixed];c.v[fixed]=0
 c.sync();g.step(1);q,v=g.state();F=g.aggregates[0].body.fields()[2];Fc=c.body.fields()[2];errors.append([np.max(abs(q-c.q)),np.max(abs(v-c.v)),np.max(abs(F-Fc))])
err=np.max(errors,axis=0);checks.update(cpu_gpu_position=err[0]<1e-6,cpu_gpu_velocity=err[1]<1e-4,cpu_gpu_F=err[2]<1e-4);o=g.observe();checks.update(cpu_gpu_support=np.linalg.norm(o['support_impulse']-support)<1e-8,cpu_gpu_impulse=np.linalg.norm(o['material_impulse']-impulse)<1e-8,cpu_gpu_work=abs(o['tool_work_J']-work)<1e-9,cpu_gpu_friction=abs(o['friction_J']-diss)<1e-9)
h=ContactGPU(Aggregate(Body(n=2,h=.003)),s,cad,[0,.001,0],[0,0,0],fixed=fixed);before=[h.q.numpy().copy(),h.vh.numpy().copy()];ledger={k:v.numpy().copy() for k,v in h.ca.items() if k in h.tx}
try:h.step(8);checks['overforce_rejected']=False
except ValueError:checks['overforce_rejected']=True
checks['rejection_atomic']=h.steps==0 and np.array_equal(before[0],h.q.numpy()) and np.array_equal(before[1],h.vh.numpy()) and all(np.array_equal(v,h.ca[k].numpy()) for k,v in ledger.items())
checks['deep_penetration_rejected']=not certify(s.tets(np.zeros_like(a.q)),cad,np.array([0,.001,0]),cad.R)['passed']
r={'checks':{k:bool(v) for k,v in checks.items()},'passed':all(checks.values()),'same_operator_errors':err.tolist(),'support_error_Ns':float(np.linalg.norm(o['support_impulse']-support)),'impulse_error_Ns':float(np.linalg.norm(o['material_impulse']-impulse)),'work_error_J':o['tool_work_J']-work,'friction_error_J':o['friction_J']-diss,'scope':'12 loaded sliding RK4 steps, independent double-precision CPU implementation and exact original-triangle queries; explicit overforce/penetration rejection and mechanics/work rollback'};(W/'reports/rk4_controls.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
