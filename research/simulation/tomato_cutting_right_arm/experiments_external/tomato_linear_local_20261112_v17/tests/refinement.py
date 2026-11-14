"""Bounded timestep selection. Keep the initial 25us rejection as evidence."""
from pathlib import Path
import sys,json,time,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from linear_reference import Body,strain_audit
from linear_gpu import GPU
checks={};rows=[];selected={};start=time.perf_counter()
def check(k,v,d=None):
 checks[k]=bool(v)
 if not v:raise AssertionError((k,d))
def run(b,dt):
 g=GPU(b,dt);m=b.metrics();E0=m['U']+m['T'];tr=[];worst=0.;t=time.perf_counter()
 for j in range(20):
  g.step(round(.001/dt));g.export();x,v,F=b.fields();e,f=b.energy_force();mm=b.metrics();worst=max(worst,abs(e+mm['T']-E0)/max(abs(E0),1e-10));tr.append((x.copy(),v.copy(),F.copy(),f.copy()))
 return b,tr,worst,time.perf_counter()-t
try:
 for name,n,d in [('intact',None,0),('oblique',[1,.27,.13],.001),('diagonal',[1,1,1],.00013),('sliver10um',[1,1,1],1e-5),('sliver1um',[1,1,1],1e-6)]:
  b=Body();b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]+=.005*b.grid[:,2]
  if n is not None:b.split(n,d)
  audit=strain_audit(b);dt=25e-6
  while dt>.4*audit['linearized_stability_dt_s']:dt*=.5
  while dt>=.1953125e-6:
   a,ta,ea,wa=run(b.clone(),dt);c,tc,ec,wc=run(b.clone(),dt/2);diffs={k:max(float(np.max(np.linalg.norm(x[i]-y[i],axis=-1))) for x,y in zip(ta,tc)) for i,k in enumerate(['x','v','F','force_max'])};df=np.array([a[3]-c[3] for a,c in zip(ta,tc)]);rf=np.array([c[3] for c in tc]);force_abs=float(np.sqrt(np.mean(np.sum(df*df,axis=-1))));force_ref=float(np.sqrt(np.mean(np.sum(rf*rf,axis=-1))));passed=max(ea,ec)<=.05 and diffs['x']<=1e-4 and diffs['v']<=.005 and force_abs<=max(1e-5,.05*force_ref)
   row={'name':name,'dt_s':dt,'half_dt_s':dt/2,'stability_dt_s':audit['linearized_stability_dt_s'],'duration_s':.02,'energy_residual_max':ea,'half_energy_residual_max':ec,'field_difference':diffs,'force_rms_difference_N':force_abs,'force_rms_reference_N':force_ref,'force_relative':force_abs/max(force_ref,1e-5),'wall_s':wa+wc,'regions':len(b.X),'nodes':len(b.u),'accepted':passed};rows.append(row);print(row,flush=True);(W/'refinement.partial.json').write_text(json.dumps({'rows':rows,'checks':checks,'selected':selected},indent=2))
   if passed:selected[name]=dt;a.save(W/'states'/f'{name}_refined_final.npz');break
   dt*=.5
  check(name+'_converged',name in selected)
 # True saved/loaded continuation against uninterrupted active GPU state.
 b=Body.restore(W/'states/oblique.npz');g=GPU(b,dt=1e-6);g.step(17);g.export();b.save(W/'states/restart_mid.npz');r=Body.restore(W/'states/restart_mid.npz');rg=GPU(r,dt=1e-6);g.step(23);rg.step(23);g.export();rg.export();check('loaded_restart_exact',np.array_equal(b.u,r.u) and np.array_equal(b.v,r.v) and np.array_equal(b.ids,r.ids) and b.history==r.history)
 b=Body();b.v[:]=[.02,-.01,.015];m=b.metrics();g=GPU(b,dt=12.5e-6);g.step(8000);g.export();err=float(np.max(np.linalg.norm(b.fields()[0]-b.X-[.002,-.001,.0015],axis=1)));pe=float(np.linalg.norm(b.metrics()['momentum']-m['momentum'])/np.linalg.norm(m['momentum']));check('translation_0p1s',err<=1e-4,err);check('linear_momentum',pe<=.001,pe)
 b=Body();b.v=np.cross(np.array([0.,0.,2.]),b.grid);m=b.metrics();g=GPU(b,dt=12.5e-6);g.step(1600);g.export();ae=float(np.linalg.norm(b.metrics()['angular']-m['angular'])/np.linalg.norm(m['angular']));check('angular_momentum',ae<=.01,ae);rows.append({'translation_error_m':err,'linear_momentum_relative':pe,'angular_momentum_relative':ae})
 result={'status':'pass_dynamic_components','checks':checks,'selected_dt_s':selected,'rows':rows,'wall_s':time.perf_counter()-start,'contact_fracture_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'failed','exception':repr(e),'checks':checks,'selected_dt_s':selected,'rows':rows,'wall_s':time.perf_counter()-start,'contact_fracture_qualified':False}
(W/'refinement.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True);sys.exit(0 if result['status'].startswith('pass') else 1)
