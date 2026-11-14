from pathlib import Path
import sys,os,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from contact_surface import Surface
from blade_geometry import CAD
from contact_gpu import ContactGPU
from contact_law import evaluate
from resistance_adapter import trial
from cutting_work import CutLedger
checks={};rows=[];start=time.perf_counter()
a=Aggregate(Body(n=2,h=.003));s=Surface(a,.001);cad=CAD();fixed=np.isclose(a.body.grid[:,1],-.003);T=np.array([0.,.00299,0.]);travel=np.array([0.,0.,.000025]);g=ContactGPU(a,s,cad,T,travel,fixed=fixed)
c=Aggregate(a.body);support=np.zeros(3);impulse=np.zeros(3)
def acceleration(q,v,t):
 T,vt=g.pose(t);x=s.positions(q);query=cad.query(x,T);law=evaluate(query['phi'],query['normal'],s.velocities(v)-vt,s.area);f=c.energy_force(q)[1]+s.pullback(law['force']);acc=c.solve(f);acc[fixed]=0.;return acc,f,law
errors=[]
for step in range(80):
 t=step*g.dt;acc,f,law=acceleration(c.q,c.v,t);vh=c.v+.5*g.dt*acc;vh[fixed]=0;q=c.q+g.dt*vh;acc2,f2,law2=acceleration(q,vh,t+g.dt);v=vh+.5*g.dt*acc2;v[fixed]=0;c.q,c.v=q,v;c.sync();support-=.5*g.dt*(f[fixed].sum(0)+f2[fixed].sum(0));impulse+=.5*g.dt*(law['force'].sum(0)+law2['force'].sum(0))
 g.step(1);qg,vg=g.state();Fg=g.aggregates[0].body.fields()[2];Fc=c.body.fields()[2];errors.append([np.max(abs(q-qg)),np.max(abs(v-vg)),np.max(abs(Fg-Fc))])
err=np.max(errors,axis=0);checks['cpu_gpu_position']=err[0]<=1e-6;checks['cpu_gpu_velocity']=err[1]<=1e-4;checks['cpu_gpu_F']=err[2]<=1e-4;rows.append({'strict_loaded_comparison':err.tolist()})
obs=g.observe();checks['cpu_gpu_support_impulse']=np.linalg.norm(obs['support_impulse']-support)<1e-8;checks['cpu_gpu_tool_impulse']=np.linalg.norm(obs['material_impulse']-impulse)<1e-8
# Runtime force rejection rolls back mechanics, clocks and accumulated work.
h=ContactGPU(Aggregate(Body(n=2,h=.003)),s,cad,[0,.001,0],[0,0,0],fixed=fixed,mode=1)
before=[h.q.numpy().copy(),h.vh.numpy().copy()];ledger_before={k:v.numpy().copy() for k,v in h.ca.items() if k in h.tx}
try:h.step(8);checks['force_rejected']=False
except ValueError:checks['force_rejected']=True
checks['force_rejection_atomic']=h.steps==0 and np.array_equal(before[0],h.q.numpy()) and np.array_equal(before[1],h.vh.numpy()) and all(np.array_equal(x,h.ca[k].numpy()) for k,x in ledger_before.items())
# Cut surfaces cannot be silently admitted by the intact-only contact adapter.
b=Body(n=2,h=.003);b.split([1.,.2,0],.0001)
try:Surface(Aggregate(b));checks['unqualified_cut_surface_rejected']=False
except ValueError:checks['unqualified_cut_surface_rejected']=True
# Exact work-conjugate resistance on both ordinary and aggregated inertia.
for case,b in [('intact',Body(n=2,h=.003)),('aggregated',b)]:
 a=Aggregate(b);marker=np.ones(len(a.q))/len(a.q);a.v[:]=[0.,.001,0.];d=np.array([0.,1.,0.]);dt=12.5e-6;width=.006
 for label,vt,eligible in [('stick',.00101,True),('slip',1.,True),('reverse',-.1,True),('blunt',1.,False)]:
  state=a.v.copy();r=trial(a,marker,d,np.array([0.,vt,0.]),dt,width,eligible)
  checks[f'{case}_{label}_work']=abs(r['energy_residual_J'])<1e-12
  checks[f'{case}_{label}_no_mutation']=np.array_equal(state,a.v)
  checks[f'{case}_{label}_force_limit']=r['force_N']<=2.
  if label in ['stick','reverse','blunt']:checks[f'{case}_{label}_no_fracture']=r['area_m2']==0
  else:checks[f'{case}_{label}_positive_work']=r['area_m2']>0 and r['fracture_J']>0
  rows.append({'case':case,'mode':label,**{k:v for k,v in r.items() if k!='velocity'}})
# Transactional original area ledger: actual measured work required, query/retry
# cannot mutate it, and prior paid area cannot be charged again.
ledger=CutLedger((-.003,0,.003,.003));before=ledger.fingerprint();tr=ledger.trial(0,[[-.003,0],[.003,0]],[[-.003,.0001],[.003,.0001]],'edge',True)
checks['preview_no_mutation']=ledger.fingerprint()==before
try:ledger.commit(tr,0.,True);checks['unpaid_rejected']=False
except ValueError:checks['unpaid_rejected']=True
checks['unpaid_no_mutation']=ledger.fingerprint()==before
ledger.commit(tr,tr.required_work,True);tr2=ledger.trial(1,[[-.003,0],[.003,0]],[[-.003,.0001],[.003,.0001]],'edge',True);checks['reentry_no_double_charge']=tr2.area==0
checks['checkpoint_ledger']=CutLedger.restore(ledger.state()).fingerprint()==ledger.fingerprint()
result={'status':'pass' if all(checks.values()) else 'failed','checks':{k:bool(v) for k,v in checks.items()},'rows':rows,'wall_s':time.perf_counter()-start,'physical_cut':False};(W/'mechanics_controls.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
