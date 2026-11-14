from pathlib import Path
import sys,json,time,datetime,os
import numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference import block,stencil,energy_stress,Reference
from backend import Backend,wp,k
R=W/'runs/gate1_refined';R.mkdir(exist_ok=False)
C=json.loads((W/'configs/gate1_acceptance.json').read_text());results={};checks={};start=time.monotonic()

def rotation(angle,axis=(0,0,1)):
 a=np.asarray(axis,float);a/=np.linalg.norm(a);K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
 return np.eye(3)+np.sin(angle)*K+(1-np.cos(angle))*(K@K)

def write():
 (W/'intact_controls.partial.json').write_text(json.dumps({'checks':checks,'results':results,'updated':datetime.datetime.now().astimezone().isoformat()},indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o)))

def state_metrics(b,s):
 e,_=energy_stress(s['F'].astype(float),b.mu,b.lam);mom=b.mass*s['v'].astype(float).sum(axis=0)
 L=b.mass*np.cross(s['x'].astype(float)-s['x'].mean(axis=0),s['v'].astype(float)).sum(axis=0)
 return {'momentum':mom.tolist(),'angular':L.tolist(),'energy':float(.5*b.mass*(s['v'].astype(float)**2).sum()+b.vol*e.sum()),'minJ':float(np.linalg.det(s['F']).min()),'maxJ':float(np.linalg.det(s['F']).max())}

# Analytic partition/linear completeness of reference-grid basis.
X=block(40,.0015);ids,ww,gg,grid=stencil(X,.003)
results['stencil']={'partition_error':float(abs(ww.sum(1)-1).max()),'gradient_sum':float(abs(gg.sum(1)).max()),'linear_reproduction_m':float(abs((ww[:,:,None]*grid[ids]).sum(1)-X).max())}
checks['stencil']=results['stencil']['partition_error']<1e-12 and results['stencil']['gradient_sum']<1e-10 and results['stencil']['linear_reproduction_m']<1e-12

# Independent finite-difference energy gradient, objectivity, GPU constitutive.
rng=np.random.default_rng(904);F=np.tile(np.eye(3),(64,1,1))+.1*rng.normal(size=(64,3,3));mu=1e5/2.8;lam=1e5*.4/(1.4*.2)
We,P=energy_stress(F,mu,lam);fd=np.zeros_like(P);eps=1e-6
for i in range(3):
 for j in range(3):
  d=np.zeros_like(F);d[:,i,j]=eps;fd[:,i,j]=(energy_stress(F+d,mu,lam)[0]-energy_stress(F-d,mu,lam)[0])/(2*eps)
Rot=rotation(.8,(1,2,3));Wr,Pr=energy_stress(Rot@F,mu,lam)
f=wp.array(F,dtype=wp.mat33,device='cuda:0');p=wp.zeros(64,dtype=wp.mat33,device='cuda:0');w=wp.zeros(64,dtype=float,device='cuda:0');wp.launch(k.constitutive,dim=64,inputs=[f,mu,lam,p,w]);wp.synchronize()
scale=max(np.linalg.norm(P),1.);results['constitutive']={'energy_gradient_relative':float(np.linalg.norm(fd-P)/scale),'objectivity_stress_relative':float(np.linalg.norm(Pr-Rot@P)/scale),'objectivity_energy_relative':float(np.linalg.norm(Wr-We)/np.linalg.norm(We)),'gpu_stress_relative':float(np.linalg.norm(p.numpy()-P)/scale),'gpu_energy_relative':float(np.linalg.norm(w.numpy()-We)/np.linalg.norm(We))}
checks['constitutive']=all(v<2e-5 for v in results['constitutive'].values())
np.savez_compressed(R/'constitutive.npz',F=F,P=P,fd=fd,P_gpu=p.numpy(),W=We,W_gpu=w.numpy())

# Affine compression/unload cycle: analytic force and elastic work close.
scales=np.r_[np.linspace(1,.98,101),np.linspace(.98,1,101)[1:]];cycle=np.tile(np.eye(3),(len(scales),1,1));cycle[:,1,1]=scales;en,pp=energy_stress(cycle,mu,lam)
work=np.trapezoid(pp[:,1,1],scales)*.06**3
results['affine_compression_unload']={'closed_cycle_work_J':float(work),'final_energy_J':float(en[-1]*.06**3),'peak_energy_J':float(max(en)*.06**3),'force_at_2percent_compression_N':float(pp[100,1,1]*.06**2),'scope':'prescribed homogeneous constitutive fixture; external fixture force is not knife force'}
checks['affine_cycle']=abs(work)<2e-8 and abs(en[-1])<1e-8
np.savez_compressed(R/'affine_cycle.npz',scale=scales,energy=en,stress=pp)
write()

# CPU/GPU short nonuniform field and deformation comparison.
x=block(6);cpu=Reference(x);gpu=Backend(x);vel=rng.normal(size=x.shape)*.001;deform=np.tile(np.diag([1.,.995,1.]),(len(x),1,1))
cpu.v=vel.copy();cpu.F=deform.copy();cpu.x=x@deform[0].T;gpu.set_state(v=vel,F=deform,x=cpu.x)
for _ in range(10):cpu.step(5e-5)
gpu.step(5e-5,10);s=gpu.check();results['cpu_gpu']={'position_m':float(abs(s['x']-cpu.x).max()),'velocity_m_s':float(abs(s['v']-cpu.v).max()),'F':float(abs(s['F']-cpu.F).max())}
checks['cpu_gpu']=results['cpu_gpu']['position_m']<1e-7 and results['cpu_gpu']['velocity_m_s']<1e-5 and results['cpu_gpu']['F']<1e-5
gpu.save(R/'cpu_gpu.npz')

# Full block tests. Zero gravity/contact; explicit impulses only in initial condition.
def run(name,dt,duration,velocity=None,A=None,offset=(0,0,0)):
 b=Backend(X,spacing=.0015,h=.003);x=X+np.asarray(offset);F0=np.tile(np.eye(3),(len(X),1,1));v=np.zeros_like(X)
 if A is not None:x=X@A.T+offset;F0[:]=A
 if velocity is not None:v=velocity.copy()
 b.set_state(x=x,v=v,F=F0);s0=b.check();initial=state_metrics(b,s0);rows=[];n=round(duration/dt);batch=min(40,n);t=time.monotonic();peakp=0.;peakL=0.;peakenergy=initial['energy'];pm=np.array(initial['momentum']);lm=np.array(initial['angular'])
 for j in range(0,n,batch):
  b.step(dt,min(batch,n-j));s=b.check();met=state_metrics(b,s);peakp=max(peakp,float(np.linalg.norm(np.array(met['momentum'])-pm)));peakL=max(peakL,float(np.linalg.norm(np.array(met['angular'])-lm)));peakenergy=max(peakenergy,met['energy']);rows.append([b.sim_time,*met['momentum'],*met['angular'],met['energy'],met['minJ'],met['maxJ']])
  if time.monotonic()-t>600:raise TimeoutError(name)
 np.savetxt(R/f'{name}.csv',rows,delimiter=',',header='t,px,py,pz,Lx,Ly,Lz,energy,minJ,maxJ',comments='');b.save(R/f'{name}.npz')
 expected=x+v*duration if name.startswith(('translation','rest','rotated_rest')) else None
 result={'duration':duration,'wall_s':time.monotonic()-t,'mass_kg':b.mass*b.n,'mass_relative_error':abs(b.mass*b.n/.216-1),'peak_momentum_error':peakp,'momentum_scale':float(np.linalg.norm(pm)),'peak_angular_error':peakL,'angular_scale':float(np.linalg.norm(lm)),'initial_energy':initial['energy'],'peak_energy':peakenergy,'max_translation_error_m':float(np.max(np.linalg.norm(s['x']-expected,axis=1))) if expected is not None else None,'memory':b.memory(),'initial':initial,'final':met}
 results[name]=result;checks[name+'_mass']=result['mass_relative_error']<=1e-6;checks[name+'_momentum']=peakp<=max(1e-9,1e-3*np.linalg.norm(pm))
 if expected is not None:checks[name+'_translation']=result['max_translation_error_m']<=1e-4
 write();return s,result
run('rest',1.25e-5,.1)
run('translation',1.25e-5,.1,np.tile([.01,.02,-.005],(len(X),1)))
run('rotated_rest',1.25e-5,.02,A=rotation(.7,(1,2,3)))
vel=np.cross(np.tile([0,0,1.],(len(X),1)),X)
s,r=run('spin',1.25e-5,.01,velocity=vel);checks['spin_angular']=r['peak_angular_error']<=max(1e-10,.01*r['angular_scale'])
sc,rc=run('compression_release',1.25e-5,.02,A=np.diag([1,.99,1]))
sh,rh=run('compression_release_half',6.25e-6,.02,A=np.diag([1,.99,1]))
checks['compression_energy']=rc['peak_energy']<=rc['initial_energy']*1.05+2e-8
results['half_step']={'position_max_m':float(np.linalg.norm(sc['x']-sh['x'],axis=1).max()),'velocity_max_m_s':float(np.linalg.norm(sc['v']-sh['v'],axis=1).max())}
checks['half_step']=results['half_step']['position_max_m']<=1e-4 and results['half_step']['velocity_max_m_s']<=.005
result={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'total_wall_s':time.monotonic()-start,'timestamp':datetime.datetime.now().astimezone().isoformat(),'scope':'Intact TL mechanics only; no fracture/contact qualification'}
(W/'intact_controls.json').write_text(json.dumps(result,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o)));print(json.dumps(result,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o)))
