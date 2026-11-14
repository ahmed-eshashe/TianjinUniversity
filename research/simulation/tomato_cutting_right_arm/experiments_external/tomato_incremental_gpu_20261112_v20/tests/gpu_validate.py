from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from aggregation import Aggregate,vertex_fields
from selective_gpu import GPU
from response import snap
from weighted_response import weighted_diff,passes
rows=[];checks={};start=time.perf_counter();dt=12.5e-6
try:
 for name,n,d,front in [('intact',None,0,None),('oblique',[1,.27,.13],.001,None),('partial',[1,.27,.13],.001,([0,-1,0],0)),('corner',[1,1,1],1e-6,None),('heldout',[1,-1,1],1e-6,None)]:
  b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2]
  if n is not None:b.split(n,d,front=front)
  c=Aggregate(b,1e-8);g=GPU(Aggregate(b,1e-8),dt);cpu=[];gpu=[];maxF=0.;e0=b.metrics()['U']
  for frame in range(20):
   for _ in range(80):c.step(dt)
   g.step(80);gb=g.export();cpu.append(snap(c.body));gpu.append(snap(gb));maxF=max(maxF,float(np.max(abs(c.body.fields()[2]-gb.fields()[2]))))
  delta=weighted_diff(b,gpu,cpu);ed=max(abs(s['energy']-e0)/e0 for s in gpu);ok=delta['position_m']<=1e-6 and delta['velocity_m_s']<=1e-4 and maxF<=1e-4 and passes(delta) and ed<=.05;checks[name+'_CPU_GPU']=ok;rows.append({'case':name,'duration_s':.02,'dt_s':dt,'difference':delta,'F_max':maxF,'energy_drift_relative':ed,'accepted':ok});print(rows[-1],flush=True)
 # Full velocity reconstruction when external actions change.
 b=Body(n=4);b.split([1,1,1],1e-6);c=Aggregate(b,1e-8);force=np.zeros_like(b.u);force[0]=[.02,-.01,0];g=GPU(Aggregate(b,1e-8),dt,external=force)
 for _ in range(40):c.step(dt,force)
 g.step(40);force=-force;g.set_external(force)
 for _ in range(40):c.step(dt,force)
 g.step(40);gb=g.export();delta=weighted_diff(b,[snap(gb)],[snap(c.body)]);checks['action_change_velocity_phase']=delta['position_m']<=1e-6 and delta['velocity_m_s']<=1e-4;rows.append({'case':'force_direction_change','difference':delta});print(rows[-1],flush=True)
 # Independent batches, no force on other environments.
 b=Body(n=4);b.split([1,1,1],1e-6);forces=np.zeros((3,len(b.u),3));forces[0,0]=[.02,0,0];gg=GPU(Aggregate(b),dt,batch=3,external=forces);gg.step(80);q,v=gg.state();checks['batch_independence']=np.max(abs(q[1:]))==0 and np.max(abs(v[1:]))==0 and np.max(abs(q[0]))>0
 # Saved physical state and resumed half-step conversion.
 b=g.export();b.save(W/'states/gpu_restart_mid.npz');reload=GPU(Aggregate(Body.restore(W/'states/gpu_restart_mid.npz')),dt,external=force);g.step(40);reload.step(40);x,v=vertex_fields(g.export());xr,vr=vertex_fields(reload.export());rx=float(np.max(abs(x-xr)));rv=float(np.max(abs(v-vr)));checks['gpu_loaded_restart']=rx<=1e-6 and rv<=1e-4;rows.append({'case':'gpu_restart','position_m':rx,'velocity_m_s':rv})
 result={'status':'pass' if all(checks.values()) else 'failed','checks':{k:bool(v) for k,v in checks.items()},'rows':rows,'wall_s':time.perf_counter()-start,'physical_contact_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':{k:bool(v) for k,v in checks.items()},'rows':rows,'wall_s':time.perf_counter()-start}
(W/'gpu_validation.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
