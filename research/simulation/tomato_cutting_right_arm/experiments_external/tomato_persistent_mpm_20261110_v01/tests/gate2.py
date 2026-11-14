from pathlib import Path
import sys,json,time,datetime,resource,os,gc
import numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference import block,Reference,swept_codes,couple,compatible
from backend import Backend,wp
from topology import components
assert json.loads((W/'intact_controls.json').read_text())['status']=='pass'
R=W/'runs/gate2';R.mkdir(exist_ok=False);start=time.monotonic();checks={};results={};C=json.loads((W/'configs/gate2_acceptance.json').read_text());DT=C['dt_s'];X=block(40,.0015);rng=np.random.default_rng(20261110)

def write():
 o={'status':'running','checks':checks,'results':results,'updated':datetime.datetime.now().astimezone().isoformat(),'pid':os.getpid(),'elapsed_s':time.monotonic()-start}
 (W/'persistent_cut_controls.partial.json').write_text(json.dumps(o,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))
 print('PROGRESS',list(results)[-1:] if results else [],'failed',[k for k,v in checks.items() if not v],flush=True)

def make(offset=None):
 return Backend(X if offset is None else X+offset,spacing=.0015,h=.003)

def rotation(a,axis=(0,0,1)):
 u=np.array(axis,float);u/=np.linalg.norm(u);K=np.array([[0,-u[2],u[1]],[u[2],0,-u[0]],[-u[1],u[0],0]])
 return np.eye(3)+np.sin(a)*K+(1-np.cos(a))*(K@K)

def sweep(b,cut=0,axis=0,plane=0.,end_y=-.035,dt=DT,Rm=None,shift=None):
 # This driver sends one short CURRENT segment per call; backend never receives the future endpoint.
 if Rm is None:Rm=np.eye(3)
 if shift is None:shift=np.zeros(3)
 e=np.array([0.,0.,1.]) if axis==0 else np.array([1.,0.,0.]);n=np.eye(3)[axis]
 a=np.zeros(3);a[axis]=plane;a[1]=.035;target=a.copy();target[1]=end_y
 steps=round((.035-end_y)/(.5*.002));history=[];wall=time.monotonic()
 for j in range(steps):
  z=a+(target-a)*(j+1)/steps;old=a+(target-a)*j/steps
  before=b.codes.numpy();b.sweep(cut,Rm@old+shift,Rm@z+shift,Rm@n,Rm@e)
  b.step(dt,round(.002/dt));s=b.check()
  # Existing nonzero digits for all cuts are immutable.
  before_digits=np.stack([(before//3**k)%3 for k in range(4)],axis=1);after_digits=np.stack([(s['codes']//3**k)%3 for k in range(4)],axis=1)
  if np.any((before_digits!=0)&(before_digits!=after_digits)):raise RuntimeError('history changed')
  history.append([j,b.sim_time,int(np.sum(s['codes']!=before)),b.count])
  if time.monotonic()-wall>600:raise TimeoutError('tool sweep')
 return np.array(history)

def classify(b,name):
 s=b.check();labels,info=components(b.X,s['codes'],b.h);b.save(R/f'{name}.npz');np.save(R/f'{name}_components.npy',labels)
 info.update(b.memory());info['mass_kg']=b.mass*b.n;info['minJ']=float(np.linalg.det(s['F']).min());info['maxJ']=float(np.linalg.det(s['F']).max());return labels,info

def run_steps(b,duration,dt=DT):
 t=time.monotonic();n=round(duration/dt)
 for j in range(0,n,160):
  b.step(dt,min(160,n-j));b.check()
  if time.monotonic()-t>600:raise TimeoutError('continuation')
 return time.monotonic()-t

# Pair-exchange invariants independent of GPU transfer.
codes=np.array([0,1,2,3,4,5,6,7,8]);m=rng.uniform(.001,.01,(9,7));p=rng.normal(size=(9,7,3));q=rng.normal(size=p.shape)
pp,qq=couple(m,p,q,codes);results['pair_algebra']={'momentum_error':float(abs(pp.sum(0)-p.sum(0)).max()),'impulse_error':float(abs(qq.sum(0)-q.sum(0)).max())};checks['pair_conservation']=max(results['pair_algebra'].values())<1e-12
v=rng.normal(size=(7,3));pc=m[:,:,None]*v;cp,cq=couple(m,pc,np.zeros_like(pc),codes);checks['common_velocity']=abs(cp-pc).max()<1e-12

# Independent CPU/GPU geometry + nontrivial three-state transfer.
x=block(6);cpu=Reference(x);gpu=Backend(x);old=np.array([0,.02,0]);new=np.array([0,0.,0]);normal=np.array([1,0,0]);edge=np.array([0,0,1]);cpu.codes=swept_codes(x,cpu.codes,0,old,new,normal,edge,.02,.036);gpu.sweep(0,old,new,normal,edge,.02)
checks['history_cpu_gpu']=np.array_equal(cpu.codes,gpu.codes.numpy());vv=rng.normal(size=x.shape)*.001;FF=np.tile(np.diag([1.,.999,1.]),(len(x),1,1));cpu.v=vv.copy();cpu.F=FF.copy();gpu.set_state(v=vv,F=FF)
for _ in range(10):cpu.step(DT)
gpu.step(DT,10);ss=gpu.check();results['cpu_gpu_partial']={'x_error':float(abs(cpu.x-ss['x']).max()),'v_error':float(abs(cpu.v-ss['v']).max()),'F_error':float(abs(cpu.F-ss['F']).max())};checks['cpu_gpu_partial']=results['cpu_gpu_partial']['x_error']<1e-7 and results['cpu_gpu_partial']['v_error']<1e-5 and results['cpu_gpu_partial']['F_error']<1e-5
gpu.save(R/'cpu_gpu_partial.npz');write()

# Untouched, partial, and complete sequences.
b=make();run_steps(b,.02);_,info=classify(b,'untouched');results['untouched']=info;checks['untouched_connected']=info['components']==1 and b.count==1;write()
partial=make();hist=sweep(partial,end_y=0.);np.savetxt(R/'partial_actions.csv',hist,delimiter=',');_,info=classify(partial,'partial_withdrawn');results['partial']=info;checks['partial_bridge']=info['components']==1 and np.any(partial.codes.numpy()==0)
# A tangential impulse must be transmitted through the still-intact bridge.
ss=partial.state();vv=ss['v'].copy();mask=(X[:,0]<0)&(X[:,1]>0);other=(X[:,0]>0)&(X[:,1]>0);vv[mask,2]+=.01;partial.set_state(v=vv);run_steps(partial,.02);ss=partial.check();response=float(abs(ss['v'][other,2].mean())/.01);results['partial']['bridge_response_fraction']=response;checks['partial_transmits']=response>.01;partial.save(R/'partial_loaded.npz');write()

full=make();hist=sweep(full);np.savetxt(R/'full_actions.csv',hist,delimiter=',');labs,info=classify(full,'full_withdrawn');results['full']=info;checks['full_split']=info['components']==2
# Tool is now absent. Open the just-generated cut by an explicit normal velocity fixture.
ss=full.state();vv=ss['v'].copy();vv[:,0]+=np.where(X[:,0]<0,-.02,.02);full.set_state(v=vv);opening_wall=run_steps(full,.1);ss=full.check();gap=float(ss['x'][X[:,0]>0,0].min()-ss['x'][X[:,0]<0,0].max()-.0015);results['full']['free_opening_gap_m']=gap;checks['resolved_gap']=gap>=.003;full.save(R/'full_opened.npz');write()

# Paired continuations isolate probe response from baseline drift. No barrier or tool exists.
def probe(opened,name,mask,tangent=(0,0,1),dt=DT):
 state=opened.state();baseline=Backend(opened.X,spacing=.0015,h=.003);forced=Backend(opened.X,spacing=.0015,h=.003)
 for b in (baseline,forced):b.set_state(x=state['x'],v=state['v'],F=state['F'],codes=state['codes'])
 component_ids,_=components(opened.X,state['codes'],opened.h);other_ids=np.unique(component_ids[~mask]);vv=state['v'].copy();vv[mask]+=.01*np.asarray(tangent);forced.set_state(v=vv);rows=[];peak=0.;drive=0.;t=time.monotonic()
 for j in range(10):
  baseline.step(dt,round(.002/dt));forced.step(dt,round(.002/dt));a=baseline.check();b=forced.check();delta=b['v']-a['v'];peak=max(peak,max(float(np.linalg.norm(delta[component_ids==ci].mean(axis=0))/.01) for ci in other_ids));drive=float(np.mean(delta[mask]@np.asarray(tangent))/.01);rows.append([.002*(j+1),peak,drive,float(np.linalg.norm(delta[~mask],axis=1).max()/.01)])
 np.savetxt(R/f'{name}_probe.csv',rows,delimiter=',',header='t,undriven_mean_fraction,driven_mean_fraction,undriven_max_fraction',comments='');baseline.save(R/f'{name}_baseline.npz');forced.save(R/f'{name}_probe.npz')
 return {'peak_undriven_mean_fraction':peak,'final_driven_mean_fraction':drive,'peak_undriven_particle_fraction':float(np.max(np.array(rows)[:,3])),'wall_s':time.monotonic()-t,'tool_present':False}
results['full']['probe']=probe(full,'full',X[:,0]<0);checks['full_independent']=results['full']['probe']['peak_undriven_mean_fraction']<=.01;write()

parallel=make();sweep(parallel,0,plane=-.012);sweep(parallel,1,plane=.012);_,info=classify(parallel,'parallel');results['parallel']=info;checks['parallel_three']=info['components']==3;write()
inter=make();sweep(inter,0);sweep(inter,1,axis=2);_,info=classify(inter,'intersecting');results['intersecting']=info;checks['intersect_four']=info['components']==4
ss=inter.state();vv=ss['v'].copy();vv[:,0]+=.02*np.sign(X[:,0]);vv[:,2]+=.02*np.sign(X[:,2]);inter.set_state(v=vv);run_steps(inter,.1);inter.save(R/'intersecting_opened.npz');results['intersecting']['probe']=probe(inter,'intersecting',(X[:,0]<0)&(X[:,2]<0),tangent=(0,1,0));checks['intersect_independent']=results['intersecting']['probe']['peak_undriven_mean_fraction']<=.01;write()

# Rigid transform of current cut state; X and codes remain attached to material.
# This is a frame/objectivity fixture, not a simulated grasp/contact action.
ss=full.state();Rm=rotation(.63,(1,2,3));shift=np.array([.019,-.007,.011]);moved=make();moved.set_state(x=ss['x']@Rm.T+shift,v=ss['v']@Rm.T,F=Rm@ss['F'],codes=ss['codes']);before=moved.codes.numpy().copy();run_steps(moved,.01);results['moved_history']={'codes_identical':bool(np.array_equal(before,moved.codes.numpy())),'scope':'Current-state frame transform then dynamic continuation; reference state and cut history unchanged'};results['moved_history']['probe']=probe(moved,'moved',X[:,0]<0,tangent=Rm@np.array([0,0,1]));checks['moved_history']=results['moved_history']['codes_identical'] and results['moved_history']['probe']['peak_undriven_mean_fraction']<=.01;write()

# Matched current-tool sequences at half physical dt; same reference-grid placement.
half=make();sweep(half,0,dt=DT/2);_,inf=classify(half,'full_half');checks['half_full_same_codes']=np.array_equal(half.codes.numpy(),np.load(R/'full_withdrawn.npz')['codes']);checks['half_full_same_components']=inf['components']==2
ph=make();sweep(ph,0,end_y=0.,dt=DT/2);_,infp=classify(ph,'partial_half');checks['half_partial_same_codes']=np.array_equal(ph.codes.numpy(),np.load(R/'partial_withdrawn.npz')['codes']);checks['half_partial_bridge']=infp['components']==1;results['half_step']={'full_components':inf['components'],'partial_components':infp['components']};write()

# Translated reference lattice and rotated current material/tool geometry.
shift=np.array([.0007,-.0004,.0003]);translated=make(shift);sweep(translated,shift=shift);_,info=classify(translated,'translated');checks['translated_split']=info['components']==2;results['translated']=info
rot=make();Rm=rotation(.31,(1,2,3));rot.set_state(x=X@Rm.T,F=np.tile(Rm,(len(X),1,1)));sweep(rot,Rm=Rm);_,info=classify(rot,'rotated');checks['rotated_split']=info['components']==2;results['rotated']=info;write()

# Finite edge and near-miss negative controls cannot split the entire object.
small=make();old=np.array([0,.035,0]);new=np.array([0,-.035,0]);small.sweep(0,old,new,np.array([1,0,0]),np.array([0,0,1]),.0075);_,info=classify(small,'finite_edge');checks['finite_edge_bridge']=info['components']==1 and np.any(small.codes.numpy()==0);results['finite_edge']=info
miss=make();miss.sweep(0,[.06,.035,0],[.06,-.035,0],[1,0,0],[0,0,1]);checks['near_miss_no_change']=bool(np.all(miss.codes.numpy()==0))

four=make();sweep(four,0,plane=-.012);sweep(four,1,plane=.012);sweep(four,2,axis=2,plane=-.012);sweep(four,3,axis=2,plane=.012);_,info=classify(four,'four_cuts');results['four_cuts']=info;checks['four_nine_pieces']=info['components']==9
before=four.state()
try:four.sweep(4,[0,.04,0],[0,-.04,0],[1,0,0],[0,0,1]);checks['overflow_rejected']=False
except ValueError:checks['overflow_rejected']=all(np.array_equal(before[k],four.state()[k]) for k in before)
write()

# Step-only timings after synchronized warmup, same material/resolution/dt.
perf=[]
for name,b in [('zero',make()),('one',full),('two',inter),('four',four)]:
 b.step(DT,1600);b.check();t=time.monotonic();b.step(DT,1600);wp.synchronize();elapsed=time.monotonic()-t;b.check();perf.append({'case':name,'sim_s':1600*DT,'physics_wall_s':elapsed,'wall_per_sim_s':elapsed/(1600*DT),**b.memory()})
results['performance']=perf;checks['all_mass_unchanged']=all(abs(b.mass*b.n/.216-1)<=1e-6 for b in [partial,full,parallel,inter,moved,four]);results['peak_host_RSS_MiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
result={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'timestamp':datetime.datetime.now().astimezone().isoformat(),'total_wall_s':time.monotonic()-start,'scope':'Persistent topology and mechanics component tests only; geometry-driven cut labels, not physical tomato failure or contact qualification'}
(W/'persistent_cut_controls.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)));print(json.dumps(result,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))
