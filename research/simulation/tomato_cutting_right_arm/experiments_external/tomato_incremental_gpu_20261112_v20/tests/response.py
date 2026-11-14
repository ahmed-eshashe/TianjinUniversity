"""Fixed two-selector candidate comparison with preserved physical tolerances."""
from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate,vertex_fields
def snap(b):
 x,v=vertex_fields(b);U,f=b.energy_force();m=b.metrics()
 return {'x':x.copy(),'v':v.copy(),'force':f.copy(),'energy':U+m['T']}
def diff(t,r):
 df=np.array([a['force']-b['force'] for a,b in zip(t,r)]);rf=np.array([b['force'] for b in r]);fa=float(np.sqrt(np.mean(np.sum(df*df,axis=-1))));fr=float(np.sqrt(np.mean(np.sum(rf*rf,axis=-1))))
 return {'position_m':max(float(np.max(np.linalg.norm(a['x']-b['x'],axis=1))) for a,b in zip(t,r)), 'velocity_m_s':max(float(np.max(np.linalg.norm(a['v']-b['v'],axis=1))) for a,b in zip(t,r)),'force_rms_error_N':fa,'force_rms_reference_N':fr,'force_relative':fa/max(fr,1e-5)}
def passes(d):return d['position_m']<=1e-4 and d['velocity_m_s']<=.005 and d['force_rms_error_N']<=max(1e-5,.05*d['force_rms_reference_N'])
def run(b,threshold,dt,samples):
 a=Aggregate(b,threshold);tr=[];e0=b.metrics();e0=e0['U']+e0['T']
 for _ in range(samples):
  for _ in range(round(.001/dt)):a.step(dt)
  tr.append(snap(a.body))
 return tr,max(abs(s['energy']-e0)/max(e0,1e-10) for s in tr),a
if __name__=='__main__':
 rows=[];start=time.perf_counter();selected={};cases=[('intact',None,0,None),('oblique',[1,.27,.13],.001,None),('partial',[1,.27,.13],.001,([0,-1,0],0))]+[(f'corner_{d}',[1,1,1],d,None) for d in [1.3e-4,1e-5,1e-6,1e-7]]
 try:
  for name,normal,offset,front in cases:
   b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2]
   if normal is not None:b.split(normal,offset,front=front)
   # Fine baseline is independently checked at half dt over the same time.
   rr=[];rrh=[];g=GPU(b.clone(),dt=.25e-6);gh=GPU(b.clone(),dt=.125e-6)
   for _ in range(20):g.step(4000);g.export();rr.append(snap(g.body));gh.step(8000);gh.export();rrh.append(snap(gh.body))
   refdiff=diff(rr,rrh);assert passes(refdiff),(name,'reference refinement',refdiff)
   for threshold in [1e-8,1e-12]:
    dt=6.25e-6;audit=Aggregate(b,threshold).audit()
    while dt>.4*audit['linearized_stability_dt_s']:dt*=.5
    while dt>=.1953125e-6:
     t0=time.perf_counter();ta,ea,a=run(b,threshold,dt,20);th,eh,ah=run(b,threshold,dt/2,20);half=diff(ta,th);cross=diff(th,rrh);passhalf=passes(half) and max(ea,eh)<=.05;passcross=passes(cross)
     row={'case':name,'threshold':threshold,'dt_s':dt,'duration_s':.02,'aggregate_nodes':len(a.q),'original_nodes':len(b.u),'aggregated_nodes':a.report['aggregated_nodes'],'mass_block_max':a.report['max_mass_block'],'halfstep':half,'reference_halfstep':refdiff,'cross_model':cross,'halfstep_pass':passhalf,'cross_model_pass':passcross,'energy_drift_relative':max(ea,eh),'wall_s':time.perf_counter()-t0};rows.append(row);print(row,flush=True);(W/'response.partial.json').write_text(json.dumps({'rows':rows,'selected':selected},indent=2))
     if passhalf:
      if passcross:selected[f'{name}:{threshold}']=dt;ah.body.save(W/'states'/f'{name}_{threshold}_final.npz')
      break
     dt*=.5
    if name in ['intact','oblique','partial'] and a.report['aggregated_nodes']==0:break
  result={'status':'complete','rows':rows,'selected':selected,'wall_s':time.perf_counter()-start}
 except Exception as e:traceback.print_exc();result={'status':'failed_exception','exception':repr(e),'rows':rows,'selected':selected,'wall_s':time.perf_counter()-start}
 (W/'response.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
