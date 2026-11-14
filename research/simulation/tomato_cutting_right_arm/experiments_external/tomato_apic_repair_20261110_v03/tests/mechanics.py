from pathlib import Path
import sys,time,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from apic_backend import APICBackend
from apic_reference import kinetic,momentum
from reference import block,energy_stress
from contact_geometry import Cells
from volume_guard import certificate
R=W/'runs/mechanics';R.mkdir(exist_ok=False);checks={};results={};start=time.monotonic()
def write():
 (W/'mechanics.partial.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.monotonic()-start},indent=2,default=lambda x:x.item()))
def metrics(b,s):
 p,L=momentum(s['x'],s['v'],s['C'],b.mass,b.h);E=kinetic(s['v'],s['C'],b.mass,b.h)+b.vol*energy_stress(s['F'],b.mu,b.lam)[0].sum();return p,L,float(E)
def run(name,X,dt,duration,v=None,C=None,F=None):
 b=APICBackend(X,margin=.025);x=X.copy();state={}
 if F is not None:state.update(x=X@F.T,F=np.tile(F,(len(X),1,1)))
 if v is not None:state['v']=v
 if C is not None:state['C']=np.tile(C,(len(X),1,1))
 b.set_state(**state);s0=b.check();p0,L0,E0=metrics(b,s0);rows=[];pe=0.;Le=0.;energyerror=0.;tic=time.monotonic();n=round(duration/dt);batch=40
 for j in range(0,n,batch):
  b.step(dt,min(batch,n-j));s=b.check();p,L,E=metrics(b,s);loss=float(b.totals.numpy().sum());pe=max(pe,float(np.linalg.norm(p-p0)));Le=max(Le,float(np.linalg.norm(L-L0)));energyerror=max(energyerror,abs(E+loss-E0));rows.append({'t':b.sim_time,'energy':E,'transfer_and_support_loss':loss,'corrected_energy_error':E+loss-E0,'minJ':float(np.linalg.det(s['F']).min())})
  if time.monotonic()-tic>600:raise TimeoutError(name)
 res={'wall_s':time.monotonic()-tic,'sim_s':duration,'momentum_error':pe,'angular_error':Le,'angular_scale':float(np.linalg.norm(L0)),'initial_energy':E0,'max_energy_residual':energyerror,'mass_relative_error':abs(b.mass*len(X)/(1000*(round(len(X)**(1/3))*.0015)**3)-1),'memory':b.memory()}
 if name in ['rest','translation','rotated_rest']:res['position_error']=float(np.linalg.norm(s['x']-s0['x']-duration*s0['v'],axis=1).max());checks[name+'_position']=res['position_error']<1e-4
 checks[name+'_momentum']=pe<max(1e-9,1e-3*np.linalg.norm(p0));checks[name+'_angular']=Le<max(1e-10,.01*np.linalg.norm(L0));checks[name+'_mass']=res['mass_relative_error']<1e-6;checks[name+'_energy']=energyerror<max(2e-8,.05*E0);results[name]=res;b.save(R/f'{name}.npz');(R/f'{name}.json').write_text(json.dumps({'result':res,'rows':rows},indent=2));write();return s
X=block(40,.0015);run('rest',X,1.25e-5,.1);run('translation',X,1.25e-5,.1,v=np.tile([.01,.02,-.005],(len(X),1)));a=.7;rot=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);run('rotated_rest',X,1.25e-5,.02,F=rot);C=np.array([[0,-1.,0],[1.,0,0],[0,0,0]]);run('spin',X,1.25e-5,.01,v=X@C.T,C=C)
a=run('compression',X,1.25e-5,.02,F=np.diag([1,.99,1]));b=run('compression_half',X,6.25e-6,.02,F=np.diag([1,.99,1]));diff={'x':float(np.linalg.norm(a['x']-b['x'],axis=1).max()),'v':float(np.linalg.norm(a['v']-b['v'],axis=1).max())};results['compression_refinement']=diff;checks['compression_refinement']=diff['x']<1e-4 and diff['v']<.005;write()
# Localized loading directly tests the defect that affine Gate 1 controls missed.
def localized(half=False):
 X=block(8,.0015);fixed=np.isclose(X[:,1],X[:,1].min());b=APICBackend(X,fixed=fixed,margin=.012);cells=Cells(X,np.zeros(len(X),int));dt=1.25e-5/(2 if half else 1);shape=np.exp(-((X[:,0]/.0015)**2+((X[:,1]-.006)/.0015)**2));shape/=shape.sum();work=0.;rows=[];snap=[];worst=0.;ratio=[];tic=time.monotonic();old=b.check();sample=round(.00025/dt);maxE=0.;maxW=0.
 for j in range(round(.01/dt)):
  t=(j+.5)*dt;mag=.05*np.sin(np.pi*t/.01)**2;f=np.zeros_like(X);f[:,1]=-mag*shape;b.physical_step(dt,f);s=b.check();work+=float(np.sum(f*(s['x']-old['x'])));old=s
  if (j+1)%sample==0:
   cert=certificate(cells,s['x']);assert cert['passed'],cert;Fg=np.einsum('nki,kj->nij',cells.corners(s['x']),(2*cells.bits-1)/(4*cells.spacing));err=float(np.linalg.norm(Fg-s['F'],axis=(1,2)).max());den=np.linalg.norm(s['F']-np.eye(3))/np.sqrt(len(X));rat=float(np.linalg.norm(Fg-np.eye(3))/np.sqrt(len(X))/den) if den>1e-4 else None;worst=max(worst,err)
   if rat is not None:ratio.append(rat)
   p,L,E=metrics(b,s);loss=float(b.totals.numpy().sum());res=E+loss-work;maxE=max(maxE,abs(res));maxW=max(maxW,abs(work));rows.append({'t':(j+1)*dt,'work':work,'energy':E,'transfer_support_loss':loss,'energy_residual':res,'F_difference':err,'strain_ratio':rat,'min_geometry_J_bound':cert['minJ_lower_bound']});snap.append(s['x'].copy())
  if time.monotonic()-tic>600:raise TimeoutError('localized')
 name='localized_half' if half else 'localized';result={'max_F_difference':worst,'strain_ratio_min':min(ratio),'strain_ratio_max':max(ratio),'max_energy_residual':maxE,'work_scale':maxW,'wall_s':time.monotonic()-tic,'final_work':work,'transfer_support_loss':float(b.totals.numpy().sum())};b.save(R/f'{name}.npz');np.savez_compressed(R/f'{name}_trace.npz',x=np.array(snap));(R/f'{name}.json').write_text(json.dumps({'result':result,'rows':rows},indent=2));results[name]=result;checks[name+'_geometry_consistent']=worst<.02 and min(ratio)>.5 and max(ratio)<2.;checks[name+'_energy']=maxE<max(2e-8,.05*maxW);write();return np.array(snap)
a=localized();b=localized(True);checks['localized_refinement']=float(np.linalg.norm(a-b,axis=-1).max())<1e-4
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'wall_s':time.monotonic()-start,'scope':'APIC repaired mechanics, affine momentum included; not cutting qualification'};(W/'mechanics_controls.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()));print(json.dumps(out,indent=2,default=lambda x:x.item()))
