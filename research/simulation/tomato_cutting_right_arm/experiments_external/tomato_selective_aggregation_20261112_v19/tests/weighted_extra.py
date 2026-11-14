from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate,vertex_fields
from response import snap
from weighted_response import weighted_diff,passes,run
checks={};rows=[];start=time.perf_counter()
try:
 b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.v=np.cross([.3,.2,.1],b.grid)+[.01,-.02,.03];b.v[:,0]+=.004*np.sin(b.grid[:,1]/.024*2*np.pi)
 for _ in range(100):b.step(1e-6)
 events=[('partial',[1,1,1],1e-6,0,([0,-1,0],0)),('complete',[1,1,1],1e-6,0,None),('second',[1,0,0],.006,1,None),('third',[0,1,0],-.006,2,None),('fourth',[0,0,1],0,3,None)]
 for name,n,d,slot,front in events:
  b.split(n,d,cut_id=slot,front=front);a=Aggregate(b,1e-8);t=a.transfer;delta=weighted_diff(b,[snap(a.body)],[snap(b)]);ok=delta['position_m']<=1e-4 and delta['velocity_mass_weighted_RMS_upper_bound_m_s']<=.005 and t['energy_relative']<=.05 and t['angular_relative']<=.01 and a.report['mass_relative_error']<=1e-6;checks[name+'_projection']=ok;rows.append({'case':name,'projection':t,'weighted_fields':delta,'components':len(np.unique(b.components()[0])),'unresolved_nodes':len(a.report['unresolved_nodes'])});print(rows[-1],flush=True);b=a.body
 b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.split([1,-1,1],1e-6);a=Aggregate(b,1e-8)
 for _ in range(100):a.step(1e-6)
 a.body.save(W/'states/weighted_restart_mid.npz');r=Aggregate(Body.restore(W/'states/weighted_restart_mid.npz'),1e-8)
 for _ in range(20):a.step(1e-6);r.step(1e-6)
 xx,vv=vertex_fields(a.body);xr,vr=vertex_fields(r.body);checks['restart']=np.max(abs(xx-xr))<1e-12 and np.max(abs(vv-vr))<1e-10
 # Repeat large-block controls with the same selected representation, even if nonidentity.
 for n,h,samples in [(10,.006,5),(20,.003,2)]:
  b=Body(n=n,h=h);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2];b.split([1,.27,.13],.001);ta,ea,a=run(b,12.5e-6,samples);th,eh,ah=run(b,6.25e-6,samples);g=GPU(b.clone(),.125e-6);rr=[]
  for _ in range(samples):g.step(8000);g.export();rr.append(snap(g.body))
  half=weighted_diff(b,ta,th);cross=weighted_diff(b,ta,rr);checks[f'large_{n}_response']=passes(cross);checks[f'large_{n}_refinement']=passes(half) and max(ea,eh)<=.05;rows.append({'case':f'large_{n}','extent_m':.06,'h_m':h,'duration_s':samples*.001,'dt_s':12.5e-6,'halfstep':half,'cross_model':cross,'energy_drift_relative':max(ea,eh),'aggregated_nodes':a.report['aggregated_nodes']});print(rows[-1],flush=True)
 result={'status':'pass' if all(checks.values()) else 'failed','checks':{k:bool(v) for k,v in checks.items()},'rows':rows,'wall_s':time.perf_counter()-start,'physical_cut':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':{k:bool(v) for k,v in checks.items()},'rows':rows,'wall_s':time.perf_counter()-start}
(W/'weighted_extra.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
