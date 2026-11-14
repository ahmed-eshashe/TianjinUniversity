from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from consistent_backend import ConsistentBackend
from consistent_reference import ConsistentReference
from reference import block
from contact_geometry import Cells
from volume_guard import certificate
from scipy.spatial.transform import Rotation
R=W/'runs/localized_selected';R.mkdir(exist_ok=False);checks={};results={};start=time.monotonic()
def write(): (W/'localized_selected.partial.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.monotonic()-start},indent=2,default=lambda v:v.item()))
def localized(half):
 X=block(8,.0015);fixed=np.isclose(X[:,1],X[:,1].min());b=ConsistentReference(X,fixed=fixed);cells=Cells(X,np.zeros(len(X),int));dt=3.90625e-7/(2 if half else 1);shape=np.exp(-((X[:,0]/.0015)**2+((X[:,1]-.006)/.0015)**2));shape/=shape.sum();work=0.;rows=[];xs=[];vs=[];tic=time.monotonic();worst=0.;ratios=[];maxE=0.;maxW=0.;minJ=10.
 def force(t):f=np.zeros_like(X);f[:,1]=-.05*np.sin(np.pi*t/.01)**2*shape;return f
 for j in range(round(.01/dt)):
  x0=b.x.copy();f0=force(j*dt);f1=force((j+1)*dt);b.step(dt,f0,f1);work+=float(np.sum(.5*(f0+f1)*(b.x-x0)))
  if (j+1)%round(.00025/dt)==0:
   cert=certificate(cells,b.x);assert cert['passed'],cert;Fg=np.einsum('nki,kj->nij',cells.corners(b.x),(2*cells.bits-1)/(4*cells.spacing));err=float(np.linalg.norm(Fg-b.F,axis=(1,2)).max());den=np.linalg.norm(b.F-np.eye(3))/np.sqrt(len(X));ratio=float(np.linalg.norm(Fg-np.eye(3))/np.sqrt(len(X))/den) if den>1e-4 else None;worst=max(worst,err)
   if ratio is not None:ratios.append(ratio)
   E=b.metrics()['energy'];res=E-work;maxE=max(maxE,abs(res));maxW=max(maxW,abs(work));minJ=min(minJ,cert['minJ_lower_bound']);rows.append({'t':(j+1)*dt,'work':work,'energy':E,'energy_residual':res,'F_difference':err,'strain_ratio':ratio,'min_geometry_J_bound':cert['minJ_lower_bound']});xs.append(b.x.copy());vs.append(b.v.copy())
  if time.monotonic()-tic>600:raise TimeoutError('localized')
 name='localized_half' if half else 'localized';result={'wall_s':time.monotonic()-tic,'max_F_difference':worst,'strain_ratio_min':min(ratios),'strain_ratio_max':max(ratios),'max_energy_error':maxE,'work_scale':maxW,'final_work':work,'min_geometry_J_bound':minJ,'support_drift':float(abs(b.x[fixed]-X[fixed]).max()),'numerical_filter_loss':0};results[name]=result;checks[name+'_geometry']=worst<.02 and min(ratios)>.5 and max(ratios)<2;checks[name+'_energy']=maxE<max(2e-8,.05*maxW);checks[name+'_support']=result['support_drift']<1e-9;b.save(R/(name+'.npz'));(R/(name+'.json')).write_text(json.dumps({'result':result,'rows':rows},indent=2));write();return np.array(xs),np.array(vs)
a,av=localized(False);b,bv=localized(True);results['localized_refinement']={'position_m':float(np.linalg.norm(a-b,axis=-1).max()),'velocity_m_s':float(np.linalg.norm(av-bv,axis=-1).max())};checks['localized_refinement']=results['localized_refinement']['position_m']<1e-4 and results['localized_refinement']['velocity_m_s']<.005
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'wall_s':time.monotonic()-start,'scope':'Intact block mechanics only. Persistent cuts and CAD contact are not requalified.'};(W/'localized_selected_controls.json').write_text(json.dumps(out,indent=2,default=lambda v:v.item()));print(json.dumps(out,indent=2,default=lambda v:v.item()))
