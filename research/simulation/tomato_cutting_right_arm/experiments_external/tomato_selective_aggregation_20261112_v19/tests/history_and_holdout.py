from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate,vertex_fields
from response import snap,diff,passes
checks={};rows=[];start=time.perf_counter();threshold=1e-16
def check(k,v):checks[k]=bool(v)
try:
 # Additional cut direction, same declared 1% strain loading as the response gate.
 b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2];b.split([1,-1,1],1e-6);a=Aggregate(b,threshold);c=Aggregate(b,threshold);g=GPU(b.clone(),.0625e-6);ta=[];tc=[];tr=[];dt=3.125e-6;e0=b.metrics()['U']
 for i in range(5):
  for j in range(320):a.step(dt)
  for j in range(640):c.step(dt/2)
  g.step(16000);g.export();ta.append(snap(a.body));tc.append(snap(c.body));tr.append(snap(g.body))
 cross=diff(tc,tr);half=diff(ta,tc);energy=max(abs(s['energy']-e0)/e0 for s in ta+tc+tr);check('heldout_response',passes(cross));check('heldout_halfstep',passes(half));check('heldout_energy',energy<=.05);rows.append({'case':'heldout_signed_diagonal','duration_s':.005,'dt_s':dt,'cross_model':cross,'halfstep':half,'energy_drift_relative':energy,'aggregated_nodes':a.report['aggregated_nodes']});print(rows[-1],flush=True)
 # True loaded save/restore and unchanged continuation of the reduced field.
 a.body.save(W/'states/restart_mid.npz');r=Aggregate(Body.restore(W/'states/restart_mid.npz'),threshold)
 for i in range(20):a.step(1e-6);r.step(1e-6)
 xf,vf=vertex_fields(a.body);xr,vr=vertex_fields(r.body);restart={'x_m':float(np.max(abs(xf-xr))),'v_m_s':float(np.max(abs(vf-vr)))};check('loaded_restart',restart['x_m']<1e-12 and restart['v_m_s']<1e-10);rows.append({'case':'restart','difference':restart})
 # Repeated geometric history on a previously moving, nonaffine field.
 b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.v=np.cross([.3,.2,.1],b.grid);b.v[:,0]+=.004*np.sin(b.grid[:,1]/.024*2*np.pi)
 for i in range(100):b.step(1e-6)
 events=[('partial',[1,1,1],1e-6,0,([0,-1,0],0)),('complete',[1,1,1],1e-6,0,None),('second',[1,0,0],.006,1,None),('third',[0,1,0],-.006,2,None),('fourth',[0,0,1],0,3,None)]
 for name,n,d,slot,front in events:
  before=b.clone();event=b.split(n,d,cut_id=slot,front=front);a=Aggregate(b,threshold);t=a.transfer;ok=t['position_m']<=1e-4 and t['velocity_m_s']<=.005 and t['energy_relative']<=.05 and t['angular_relative']<=.01 and a.report['mass_relative_error']<=1e-6;check(name+'_loaded_projection',ok);rows.append({'case':name,'transfer':t,'geometric_transfer':event,'components':len(np.unique(b.components()[0])),'aggregated_nodes':a.report['aggregated_nodes'],'unresolved_nodes':len(a.report['unresolved_nodes'])});b=a.body
  print(rows[-1],flush=True)
 before=b.clone();rejected=False
 try:b.split([1,0,0],0,cut_id=4)
 except ValueError:rejected=True
 check('capacity_stop',rejected and np.array_equal(b.u,before.u) and np.array_equal(b.v,before.v) and b.history==before.history)
 # Larger oblique blocks: verify restored identity operator and same-time dynamics.
 for n,h,duration in [(10,.006,.005),(20,.003,.002)]:
  b=Body(n=n,h=h);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2];b.split([1,.27,.13],.001);a=Aggregate(b,threshold);check(f'large_{n}_identity',a.report['aggregated_nodes']==0);assert a.report['aggregated_nodes']==0
  gs=[GPU(b.clone(),d) for d in [.25e-6,.125e-6,.0625e-6]];traces=[[],[],[]]
  for sample in range(round(duration/.001)):
   for g,tr in zip(gs,traces):g.step(round(.001/g.dt));g.export();tr.append(snap(g.body))
  half=diff(traces[0],traces[1]);cross=diff(traces[1],traces[2]);check(f'large_{n}_response',passes(cross));check(f'large_{n}_halfstep',passes(half));rows.append({'case':f'large_{n}','h_m':h,'extent_m':.06,'duration_s':duration,'candidate_dt_s':.25e-6,'halfstep':half,'cross_model':cross,'identity_operator_verified':True});print(rows[-1],flush=True)
 result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'wall_s':time.perf_counter()-start,'physical_cut':False,'arbitrary_path_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'rows':rows,'wall_s':time.perf_counter()-start}
(W/'history_and_holdout.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
