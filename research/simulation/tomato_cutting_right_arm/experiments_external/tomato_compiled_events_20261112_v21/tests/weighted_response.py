"""User-approved velocity norm; force/position/energy criteria unchanged."""
from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate
from response import snap,diff as original_diff
def weighted_diff(b,t,r):
 d=original_diff(t,r);ptr=np.r_[0,np.cumsum([len(p) for p in b.polys])];mass=b.rho*b.V
 d['velocity_mass_weighted_RMS_upper_bound_m_s']=max(float(np.sqrt(mass@np.maximum.reduceat(np.linalg.norm(a['v']-z['v'],axis=1),ptr[:-1])**2/mass.sum())) for a,z in zip(t,r))
 return d
def passes(d):return d['position_m']<=1e-4 and d['velocity_mass_weighted_RMS_upper_bound_m_s']<=.005 and d['force_rms_error_N']<=max(1e-5,.05*d['force_rms_reference_N'])
def run(b,dt,samples=20,threshold=1e-8):
 a=Aggregate(b,threshold);tr=[];m=b.metrics();e0=m['U']+m['T']
 for i in range(samples):
  for j in range(round(.001/dt)):a.step(dt)
  tr.append(snap(a.body))
 return tr,max(abs(s['energy']-e0)/max(e0,1e-10) for s in tr),a
if __name__=='__main__':
 start=time.perf_counter();rows=[];selected={};cases=[('intact',None,0,None),('oblique',[1,.27,.13],.001,None),('partial',[1,.27,.13],.001,([0,-1,0],0)),('heldout',[1,-1,1],1e-6,None)]+[(f'corner_{d}',[1,1,1],d,None) for d in [1.3e-4,1e-5,1e-6,1e-7]]
 try:
  for name,n,d,front in cases:
   b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2]
   if n is not None:b.split(n,d,front=front)
   rr=[];rh=[];g=GPU(b.clone(),.25e-6);h=GPU(b.clone(),.125e-6)
   for _ in range(20):g.step(4000);g.export();rr.append(snap(g.body));h.step(8000);h.export();rh.append(snap(h.body))
   ref=weighted_diff(b,rr,rh);assert passes(ref),(name,'reference',ref)
   dt=25e-6
   while dt>=.78125e-6:
    t0=time.perf_counter();ta,ea,a=run(b,dt);th,eh,ah=run(b,dt/2);half=weighted_diff(b,ta,th);cross=weighted_diff(b,ta,rh);ok=passes(half) and passes(cross) and max(ea,eh)<=.05
    row={'case':name,'threshold':1e-8,'dt_s':dt,'half_dt_s':dt/2,'duration_s':.02,'reference_halfstep':ref,'halfstep':half,'cross_model_at_candidate_dt':cross,'energy_drift_relative':max(ea,eh),'accepted':ok,'aggregated_nodes':a.report['aggregated_nodes'],'wall_s':time.perf_counter()-t0};rows.append(row);print(row,flush=True);(W/'weighted_response.partial.json').write_text(json.dumps({'rows':rows,'selected':selected},indent=2))
    if ok:selected[name]=dt;break
    dt*=.5
   assert name in selected,(name,'no accepted dt')
  result={'status':'pass','threshold':1e-8,'selected_dt_s':selected,'rows':rows,'wall_s':time.perf_counter()-start,'criterion_change_explicitly_user_approved':True,'physical_cut':False}
 except Exception as e:traceback.print_exc();result={'status':'failed','exception':repr(e),'rows':rows,'selected_dt_s':selected,'wall_s':time.perf_counter()-start}
 (W/'weighted_response.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
