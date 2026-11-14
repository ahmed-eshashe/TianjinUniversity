"""Independent continuum reference: a small-amplitude free longitudinal bar wave.
nu=0 is ONLY this analytical unit fixture; the project candidate remains nu=.4.
"""
from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from consistent_reference import ConsistentReference
from consistent_backend import ConsistentBackend
R=W/'runs/analytic_wave';R.mkdir(exist_ok=False);checks={};results={};traces=[];L=.06;E=1e5;rho=1000.;A=1e-7;k=np.pi/L;omega=np.sqrt(E/rho)*k
for refinement in [1,2]:
 s=.0015/refinement;h=.003/refinement;axes=[(np.arange(n)-(n-1)/2)*s for n in [40*refinement,8*refinement,8*refinement]];X=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3);r=ConsistentReference(X,spacing=s,h=h,nu=0.);u=np.zeros_like(X);u[:,0]=A*np.cos(k*(X[:,0]+L/2));q=r.grid+r.factor.solve(r.mass*(r.W.T@u));b=ConsistentBackend(X,spacing=s,h=h,nu=0.);b.initialize(q=q);initial=b.check();E0=b.metrics(initial)['energy'];dt=12.5e-6/refinement;duration=.012;sample=round(.0005/dt);n=round(duration/dt);tic=time.monotonic();rows=[];dx=0.;dv=0.;dE=0.
 for j in range(0,n,sample):
  b.step(dt,min(sample,n-j));z=b.check();t=b.time;ue=np.zeros_like(X);ve=np.zeros_like(X);ue[:,0]=A*np.cos(k*(X[:,0]+L/2))*np.cos(omega*t);ve[:,0]=-A*omega*np.cos(k*(X[:,0]+L/2))*np.sin(omega*t);ex=float(np.linalg.norm(z['x']-X-ue,axis=1).max()/A);ev=float(np.linalg.norm(z['v']-ve,axis=1).max()/(A*omega));e=b.metrics(z)['energy'];dx=max(dx,ex);dv=max(dv,ev);dE=max(dE,abs(e-E0)/E0);rows.append({'t':t,'displacement_relative_error':ex,'velocity_relative_error':ev,'energy_relative_error':(e-E0)/E0})
  if time.monotonic()-tic>600:raise TimeoutError('analytic wave')
 name='coarse' if refinement==1 else 'fine';results[name]={'particle_count':len(X),'spacing':s,'h':h,'dt':dt,'max_displacement_error_over_amplitude':dx,'max_velocity_error_over_peak':dv,'max_energy_relative_error':dE,'wall_s':time.monotonic()-tic};checks[name]=dx<.02 and dv<.02 and dE<.05;(R/(name+'.json')).write_text(json.dumps({'result':results[name],'rows':rows},indent=2));b.save(R/(name+'.npz'));traces.append(rows)
checks['spatial_refinement']=results['fine']['max_displacement_error_over_amplitude']<results['coarse']['max_displacement_error_over_amplitude'] and results['fine']['max_velocity_error_over_peak']<results['coarse']['max_velocity_error_over_peak']
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'reference':{'equation':'u=A cos(pi*(X+L/2)/L) cos(c*pi*t/L), c=sqrt(E/rho)','model':'Small-strain longitudinal free bar, nu=0 analytic fixture only','amplitude_m':A,'length_m':L,'period_s':2*np.pi/omega,'candidate_project_nu_unchanged':.4},'limits':'A small-strain analytical check of intact dynamics; not a tomato or cut validation.'};(W/'analytic_wave_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
