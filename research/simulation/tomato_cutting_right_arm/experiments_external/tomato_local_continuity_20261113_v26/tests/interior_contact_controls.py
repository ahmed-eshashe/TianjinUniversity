from pathlib import Path
import sys,os,json,numpy as np,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from local_continuity import Aggregate
from poly_surface import Surface
from blade_geometry import CAD
from supported_contact_gpu import ContactGPU,constrained_inverse
from poly_reference import integral
from constrained_resistance import inverse_free
checks={};rows=[];cad=CAD();dt=6.25e-6
for label,cut in [('intact',None),('partial',.00013)]:
 b=Body(n=2,h=.003)
 if cut is not None:b.split([1,0,0],cut,front=(np.array([0.,-1.,0.]),-.002))
 a=Aggregate(b);fixed=np.isclose(a.body.grid[a.masters,1],-.003)
 physical_fixed=np.isclose(a.body.grid[:,1],-.003);checks[label+'_physical_support']=abs(a.E[physical_fixed][:,~fixed]).max()<1e-12
 s=Surface(a);g=ContactGPU(a,s,cad,[0,.00299,0],[0,0,.000025],fixed=fixed,dt=dt,exact_interior=True);c=Aggregate(b);ref_surface=Surface(c);support=np.zeros(3);impulse=np.zeros(3);work=diss=0.;errors=[]
 inv=constrained_inverse(a,fixed).toarray();free=~fixed;expected=np.zeros_like(inv);expected[np.ix_(free,free)]=np.linalg.inv(a.M[free][:,free].toarray());checks[label+'_constrained_inverse']=np.max(abs(inv-expected))/max(np.max(abs(expected)),1)<1e-12
 for step in range(6):
  q0=c.q.copy();v0=c.v.copy();dq=np.zeros_like(q0);dv=np.zeros_like(v0);t0=step*dt
  for weight,beta,last,frac in [(1/6,.5,False,0),(1/3,.5,False,.5),(1/3,1,False,.5),(1/6,1,True,1)]:
   T,tv=g.pose(t0+frac*dt);law=integral(c,cad,T,g.R,tv,surface=ref_surface);force=c.energy_force(c.q)[1]+law['force'];acc=inverse_free(c,force,fixed);vv=c.v.copy();dq+=weight*vv;dv+=weight*acc;support+=dt*weight*(c.M@acc-force).sum(0);impulse+=dt*weight*law['force'].sum(0);work+=dt*weight*law['tool_power'];diss+=dt*weight*law['friction_power'];c.q=q0+dt*(dq if last else beta*vv);c.v=v0+dt*(dv if last else beta*acc);c.q[fixed]=q0[fixed];c.v[fixed]=0
  c.sync();g.step(1);q,v=g.state();errors.append([np.max(abs(q-c.q)),np.max(abs(v-c.v)),np.max(abs(g.aggregates[0].body.fields()[2]-c.body.fields()[2]))])
 err=np.max(errors,axis=0);o=g.observe();checks[label+'_position']=err[0]<1e-6;checks[label+'_velocity']=err[1]<1e-4;checks[label+'_F']=err[2]<1e-4;checks[label+'_support']=np.linalg.norm(o['support_impulse']-support)<1e-8;checks[label+'_impulse']=np.linalg.norm(o['material_impulse']-impulse)<1e-8;checks[label+'_work']=abs(o['tool_work_J']-work)<1e-9;checks[label+'_friction']=abs(o['friction_J']-diss)<1e-9;checks[label+'_fixed']=np.max(abs(q[fixed]))+np.max(abs(v[fixed]))==0;rows.append(dict(case=label,errors=err.tolist(),aggregated_nodes=a.report['aggregated_nodes'],mass_block=a.report['max_mass_block'],support_error_Ns=float(np.linalg.norm(o['support_impulse']-support))))
out=dict(checks={k:bool(v) for k,v in checks.items()},passed=all(checks.values()),cases=rows,scope='Independent CPU/GPU supported dynamics with actual CAD on intact and aggregated material. No fracture or RL qualification.');(W/'reports/interior_contact_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
