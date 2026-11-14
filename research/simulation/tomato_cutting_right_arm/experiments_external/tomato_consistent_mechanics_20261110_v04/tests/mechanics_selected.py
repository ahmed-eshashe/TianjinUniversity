from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from consistent_backend import ConsistentBackend
from consistent_reference import ConsistentReference
from reference import block
from contact_geometry import Cells
from volume_guard import certificate
from scipy.spatial.transform import Rotation
R=W/'runs/mechanics_selected';R.mkdir(exist_ok=False);checks={};results={};start=time.monotonic()
def write(): (W/'mechanics_selected.partial.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.monotonic()-start},indent=2,default=lambda v:v.item()))
def run(name,dt,duration,mode='compression'):
 b=ConsistentBackend(block(40,.0015));Rmat=Rotation.from_rotvec([.2,-.3,.1]).as_matrix()
 if mode=='compression':b.initialize(F=np.diag([1,.99,1]))
 if mode=='translation':b.initialize(vg=np.tile([.01,-.02,.005],(b.ng,1)))
 if mode=='rotated_rest':b.initialize(F=Rmat)
 if mode=='spin':b.initialize(vg=np.cross([0,0,1.],b.grid))
 initial=b.check();m0=b.metrics(initial);rows=[];xs=[];vs=[];tic=time.monotonic();batch=round(.001/dt);maxp=0.;maxL=0.;maxE=0.;n=round(duration/dt)
 for j in range(0,n,batch):
  b.step(dt,min(batch,n-j));s=b.check();m=b.metrics(s);pe=float(np.linalg.norm(m['momentum']-m0['momentum']));Le=float(np.linalg.norm(m['angular']-m0['angular']));ee=abs(m['energy']-m0['energy']);maxp=max(maxp,pe);maxL=max(maxL,Le);maxE=max(maxE,ee);rows.append({'t':b.time,'energy':m['energy'],'energy_error':m['energy']-m0['energy'],'minJ':float(np.linalg.det(s['F']).min()),'maxJ':float(np.linalg.det(s['F']).max())})
  if mode=='compression':xs.append(s['x']);vs.append(s['v'])
  if time.monotonic()-tic>600:raise TimeoutError(name)
 result={'dt':dt,'wall_s':time.monotonic()-tic,'sim_s':duration,'mass':b.mass*b.n,'initial_energy':m0['energy'],'max_energy_error':maxE,'energy_relative_error':maxE/max(m0['energy'],1e-30),'momentum_error':maxp,'angular_error':maxL,'memory':b.memory()};checks[name+'_mass']=abs(result['mass']-.216)<1e-9;checks[name+'_momentum']=maxp<max(1e-9,.001*np.linalg.norm(m0['momentum']));checks[name+'_angular']=maxL<max(1e-10,.01*np.linalg.norm(m0['angular']));checks[name+'_energy']=maxE<max(2e-8,.05*m0['energy'])
 if mode in ['rest','translation','rotated_rest']:result['rigid_error']=float(np.linalg.norm(s['x']-initial['x']-duration*initial['v'],axis=1).max());checks[name+'_position']=result['rigid_error']<1e-4
 (R/(name+'.json')).write_text(json.dumps({'result':result,'rows':rows},indent=2));b.save(R/(name+'.npz'));results[name]=result;write();return np.array(xs),np.array(vs)
a,av=run('compression',3.90625e-7,.02);b,bv=run('compression_half',1.953125e-7,.02);dx=float(np.linalg.norm(a-b,axis=-1).max());dv=float(np.linalg.norm(av-bv,axis=-1).max());results['compression_refinement']={'max_shared_time_position_m':dx,'max_shared_time_velocity_m_s':dv,'samples':20,'final_position_m':float(np.linalg.norm(a[-1]-b[-1],axis=-1).max()),'final_velocity_m_s':float(np.linalg.norm(av[-1]-bv[-1],axis=-1).max())};checks['compression_refinement']=dx<1e-4 and dv<.005;np.savez_compressed(R/'compression_shared_times.npz',x=a,v=av,x_half=b,v_half=bv);write()
# Preserve the previous localized material-force and fixed-point fixture exactly.
def localized(half):
 X=block(8,.0015);fixed=np.isclose(X[:,1],X[:,1].min());b=ConsistentReference(X,fixed=fixed);cells=Cells(X,np.zeros(len(X),int));dt=12.5e-6/(2 if half else 1);shape=np.exp(-((X[:,0]/.0015)**2+((X[:,1]-.006)/.0015)**2));shape/=shape.sum();work=0.;rows=[];xs=[];vs=[];tic=time.monotonic();worst=0.;ratios=[];maxE=0.;maxW=0.;minJ=10.
 def force(t):f=np.zeros_like(X);f[:,1]=-.05*np.sin(np.pi*t/.01)**2*shape;return f
 for j in range(round(.01/dt)):
  x0=b.x.copy();f0=force(j*dt);f1=force((j+1)*dt);b.step(dt,f0,f1);work+=float(np.sum(.5*(f0+f1)*(b.x-x0)))
  if (j+1)%round(.00025/dt)==0:
   cert=certificate(cells,b.x);assert cert['passed'],cert;Fg=np.einsum('nki,kj->nij',cells.corners(b.x),(2*cells.bits-1)/(4*cells.spacing));err=float(np.linalg.norm(Fg-b.F,axis=(1,2)).max());den=np.linalg.norm(b.F-np.eye(3))/np.sqrt(len(X));ratio=float(np.linalg.norm(Fg-np.eye(3))/np.sqrt(len(X))/den) if den>1e-4 else None;worst=max(worst,err)
   if ratio is not None:ratios.append(ratio)
   E=b.metrics()['energy'];res=E-work;maxE=max(maxE,abs(res));maxW=max(maxW,abs(work));minJ=min(minJ,cert['minJ_lower_bound']);rows.append({'t':(j+1)*dt,'work':work,'energy':E,'energy_residual':res,'F_difference':err,'strain_ratio':ratio,'min_geometry_J_bound':cert['minJ_lower_bound']});xs.append(b.x.copy());vs.append(b.v.copy())
  if time.monotonic()-tic>600:raise TimeoutError('localized')
 name='localized_half' if half else 'localized';result={'wall_s':time.monotonic()-tic,'max_F_difference':worst,'strain_ratio_min':min(ratios),'strain_ratio_max':max(ratios),'max_energy_error':maxE,'work_scale':maxW,'final_work':work,'min_geometry_J_bound':minJ,'support_drift':float(abs(b.x[fixed]-X[fixed]).max()),'numerical_filter_loss':0};results[name]=result;checks[name+'_geometry']=worst<.02 and min(ratios)>.5 and max(ratios)<2;checks[name+'_energy']=maxE<max(2e-8,.05*maxW);checks[name+'_support']=result['support_drift']<1e-9;b.save(R/(name+'.npz'));(R/(name+'.json')).write_text(json.dumps({'result':result,'rows':rows},indent=2));write();return np.array(xs),np.array(vs)
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'wall_s':time.monotonic()-start,'scope':'Intact block mechanics only. Persistent cuts and CAD contact are not requalified.'};(W/'mechanics_selected_controls.json').write_text(json.dumps(out,indent=2,default=lambda v:v.item()));print(json.dumps(out,indent=2,default=lambda v:v.item()))
