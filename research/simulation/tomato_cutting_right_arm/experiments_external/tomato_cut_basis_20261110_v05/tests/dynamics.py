from pathlib import Path
import sys,json,numpy as np,time
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from cut_reference import CutReference,RejectedEvent
from consistent_reference import ConsistentReference
from reference import block
from basis_volume_guard import certificate
R=W/'runs/dynamics';R.mkdir(exist_ok=False);X=block(8,.0015);dt0=3.90625e-7;checks={};results={};start=time.monotonic()
def write():(W/'dynamics.partial.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.monotonic()-start},indent=2,default=lambda x:x.item()))
def volume(b):
 Q,_=b.refined_coefficients();dims=b.plane_data['dims'];Q=Q.reshape(*dims,3);nl=int(np.count_nonzero(b.plane_data['t']<b.plane));return [certificate(X[X[:,0]<b.plane],Q[:nl].reshape(-1,3)),certificate(X[X[:,0]>b.plane],Q[nl:].reshape(-1,3))]
# No cut command means exact same mechanical equations as v04.
a=ConsistentReference(X);b=CutReference(X);F=np.diag([1,.99,1]);a.initialize(F=F);b.initialize(F=F)
for i in range(20):a.step(dt0);b.step(dt0)
results['untouched']={n:float(abs(getattr(a,n)-getattr(b,n)).max()) for n in ['x','v','F']};checks['untouched']=max(results['untouched'].values())<1e-12;write()
yz=np.stack(np.meshgrid(np.linspace(-.006,.006,41),np.linspace(-.006,.006,7),indexing='ij'),axis=-1).reshape(-1,2)
def partial(half=False):
 b=CutReference(X);p=b.propose([0,.006,-.006,.006]);b.commit(p);dt=dt0/(2 if half else 1);duration=.001;shape=np.exp(-((X[:,1]-.004)/.002)**2-(X[:,2]/.004)**2);left=(X[:,0]<0);right=~left;f=np.zeros_like(X);f[right,0]=.02*shape[right]/shape[right].sum();f[left,0]=-.02*shape[left]/shape[left].sum();E0=b.metrics()['energy'];work=0.;maxerr=0.;maxwork=0.;ahead=0.;behind=0.;rows=[];xs=[];vs=[];n=round(duration/dt);sample=round(.00005/dt);tic=time.monotonic();minJ=10.;maxJ=0.
 for i in range(n):
  f0=f*np.sin(np.pi*i*dt/duration)**2;f1=f*np.sin(np.pi*(i+1)*dt/duration)**2;x0=b.x.copy();b.step(dt,f0,f1);work+=float(np.sum(.5*(f0+f1)*(b.x-x0)));maxwork=max(maxwork,abs(work))
  if (i+1)%sample==0:
   z=b.face_jump(yz);aa=float(np.linalg.norm(z[yz[:,0]<=0],axis=1).max());bb=float(np.linalg.norm(z[yz[:,0]>.001],axis=1).max());ahead=max(ahead,aa);behind=max(behind,bb);E=b.metrics()['energy'];err=E-E0-work;maxerr=max(maxerr,abs(err));certs=volume(b);assert all(c['passed'] for c in certs),certs;minJ=min(minJ,*[c['minJ_lower_bound'] for c in certs]);maxJ=max(maxJ,*[c['maxJ_upper_bound'] for c in certs]);rows.append({'t':b.time,'ahead_jump':aa,'behind_jump':bb,'energy':E,'work':work,'energy_error':err});xs.append(b.x.copy());vs.append(b.v.copy())
  if time.monotonic()-tic>600:raise TimeoutError('partial')
 name='partial_half' if half else 'partial';res={'wall_s':time.monotonic()-tic,'sim_s':duration,'max_ahead_jump_m':ahead,'max_behind_jump_m':behind,'max_energy_error_J':maxerr,'work_scale_J':maxwork,'J_bound':[minJ,maxJ],'keys_retained':len(b.keys)};checks[name+'_bridge']=ahead<1e-11 and behind>1e-9;checks[name+'_energy']=maxerr<max(1e-12,.05*maxwork);results[name]=res;(R/(name+'.json')).write_text(json.dumps({'result':res,'rows':rows},indent=2));b.save(R/(name+'.npz'));write();return np.array(xs),np.array(vs)
a,av=partial();b,bv=partial(True);results['partial_refinement']={'x':float(np.linalg.norm(a-b,axis=-1).max()),'v':float(np.linalg.norm(av-bv,axis=-1).max())};checks['partial_refinement']=results['partial_refinement']['x']<1e-4 and results['partial_refinement']['v']<.005;write()
def full(half=False):
 left=X[:,0]<0;l=ConsistentReference(X[left]);r=ConsistentReference(X[~left]);r.initialize(F=np.diag([1,.995,1]));rot=Rotation.from_rotvec([.1,.2,.25]).as_matrix();center=r.q.mean(0);r.q=(r.q-center)@rot.T+center+[.008,.001,0];r.vg[:]=[.02,0,0];r.update_state();b=CutReference(X);b.commit(b.propose([-.006,.006,-.006,.006]));b.set_full_piece_state(l.q,r.q,l.vg,r.vg);initial=b.metrics();dt=dt0/(2 if half else 1);duration=.001;n=round(duration/dt);sample=round(.00005/dt);tic=time.monotonic();maxleft=0.;maxp=0.;maxL=0.;maxE=0.;independent=0.;rows=[];xs=[];vs=[]
 for i in range(n):
  b.step(dt)
  if not half:l.step(dt);r.step(dt)
  if (i+1)%sample==0:
   m=b.metrics();vl=float(np.linalg.norm(b.v[left],axis=1).max());maxleft=max(maxleft,vl);pe=float(np.linalg.norm(m['momentum']-initial['momentum']));Le=float(np.linalg.norm(m['angular']-initial['angular']));maxp=max(maxp,pe);maxL=max(maxL,Le);maxE=max(maxE,abs(m['energy']-initial['energy']));certs=volume(b);assert all(c['passed'] for c in certs),certs
   if not half:independent=max(independent,float(abs(b.v-np.concatenate([l.v,r.v])).max()),float(abs(b.x-np.concatenate([l.x,r.x])).max()))
   rows.append({'t':b.time,'left_speed':vl,'energy':m['energy'],'momentum_error':pe,'angular_error':Le});xs.append(b.x.copy());vs.append(b.v.copy())
  if time.monotonic()-tic>600:raise TimeoutError('full')
 name='full_half' if half else 'full';res={'wall_s':time.monotonic()-tic,'sim_s':duration,'stationary_fragment_max_speed':maxleft,'leak_fraction_of_0_02m_s_probe':maxleft/.02,'momentum_error':maxp,'angular_error':maxL,'max_energy_error':maxE,'initial_energy':initial['energy'],'independent_two_body_state_difference':independent if not half else None,'manufactured_geometry':'Unit fixture: translated 8mm and rotated detached piece; no physical cut or contact inferred.'};checks[name+'_independence']=maxleft/.02<.01;checks[name+'_momentum']=maxp<1e-9;checks[name+'_angular']=maxL<1e-10;checks[name+'_energy']=maxE<max(1e-12,.05*initial['energy']);
 if not half:checks['independent_two_body_reference']=independent<1e-8
 results[name]=res;(R/(name+'.json')).write_text(json.dumps({'result':res,'rows':rows},indent=2));b.save(R/(name+'.npz'));write();return np.array(xs),np.array(vs)
a,av=full();b,bv=full(True);results['full_refinement']={'x':float(np.linalg.norm(a-b,axis=-1).max()),'v':float(np.linalg.norm(av-bv,axis=-1).max())};checks['full_refinement']=results['full_refinement']['x']<1e-4 and results['full_refinement']['v']<.005;np.savez_compressed(R/'full_trace.npz',x=a,v=av,x_half=b,v_half=bv)
out={'status':'pass_restricted_unit_scope' if all(checks.values()) else 'fail','checks':checks,'results':results,'wall_s':time.monotonic()-start,'scope':'Prescribed topology only, no tool/work-based fracture or RL qualification'};(W/'dynamics_controls.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()));print(json.dumps(out,indent=2,default=lambda x:x.item()))
