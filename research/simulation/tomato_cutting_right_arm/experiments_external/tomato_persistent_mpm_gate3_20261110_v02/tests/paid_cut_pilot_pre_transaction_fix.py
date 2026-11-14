from pathlib import Path
import sys,json,time,argparse,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference import block,energy_stress
from physical_backend import PhysicalBackend
from contact_geometry import CAD,Cells
from contact_law import evaluate
from cutting_work import CutLedger
p=argparse.ArgumentParser();p.add_argument('--half',action='store_true');a=p.parse_args();R=W/'runs'/('paid_cut_half' if a.half else 'paid_cut');R.mkdir(exist_ok=False)
X=block(8,.0015);fixed=np.isclose(X[:,1],X[:,1].min());b=PhysicalBackend(X,fixed=fixed);cad=CAD();cells=Cells(X,np.zeros(len(X),int));dt=1.25e-5/(2 if a.half else 1);T0=np.array([0,.00605,0.]);stroke=.0016;load=.05;hold=.01;duration=.11;Gc=80.;direction=np.array([0.,-1.,0.]);marker=None;origin_q=None;origin_T=None;ledger=None;depth0=0.;width=0.;events=[];rows=[];snap=[];cut_done=False;start=time.monotonic();status='completed';sample=round(.0005/dt);maxF=0.;Wtool=0.;Dfr=0.;cut_numeric_loss=0.;work_earned=0.;maxbalance=0.;s=b.check();initial_energy=float(.5*b.mass*np.sum(s['v']**2)+b.vol*energy_stress(s['F'],b.mu,b.lam)[0].sum())
def pose(t):
 if t<load:z=.5*(1-np.cos(np.pi*t/load))
 elif t<load+hold:z=1.
 else:z=.5*(1+np.cos(np.pi*min(1.,(t-load-hold)/load)))
 return T0-[0,stroke*z,0]
for step in range(round(duration/dt)):
 t=step*dt;T=pose(t);Tn=pose(t+dt);tool_velocity=(Tn-T)/dt;old=s;state_backup={k:s[k].copy() for k in ['x','v','F','codes']};q=cells.points(s['x']);vq=cells.Q@s['v'];query=cad.query(q,T);law=evaluate(query['phi'],query['normal'],vq-tool_velocity,cells.area);f=law['force'];fp=cells.pullback(f);bulk=b.predict(dt);vfree=bulk+dt*fp/b.mass;vfree[fixed]=0;eligible=(query['phi']<0)&(query['kind']==1)
 if marker is None and np.any(eligible):
  weights=cells.area[eligible]/cells.area[eligible].sum();marker=np.asarray(weights@cells.Q[eligible]).ravel();origin_q=marker@s['x'];origin_T=T.copy();owner=cells.qowner[eligible];zidx=np.rint((X[owner,2]-X[:,2].min())/.0015).astype(int);width=len(np.unique(zidx))*.0015;ledger=CutLedger((-width/2,0,width/2,.0015),Gc)
 Fc=0.;J=0.;u=0.;can_cut=False;trial=None
 if marker is not None and np.any(eligible) and not cut_done:
  u=float(direction@(tool_velocity-marker@vfree));meff=b.mass/np.sum(marker[~fixed]**2);yield_force=Gc*width
  # Backward-Euler rate-independent resistance: stick below yield, slide at yield.
  J=min(yield_force*dt,meff*max(u,0.));Fc=J/dt;vfree+=J/b.mass*marker[:,None]*direction;vfree[fixed]=0;can_cut=J>=yield_force*dt*(1-1e-8)
 total_force=fp+marker[:,None]*direction*Fc if marker is not None else fp
 force_norm=max(float(np.linalg.norm(total_force.sum(0))),law['sum_magnitudes_N']+Fc);maxF=max(maxF,force_norm)
 if force_norm>2:status='force_stop';break
 b.finish(dt,vfree);s=b.check();motion=float(np.linalg.norm(cells.C@(s['x']-old['x']),axis=1).max())+np.linalg.norm(Tn-T);cert=cells.certificate(s['x'],cad,Tn,motion_bound=motion)
 if not cert['passed']:
  b.set_state(**state_backup);s=old;b.sim_time-=dt;b.steps-=1;status='whole_material_contact_stop';break
 earned=0.;depth=0.
 if marker is not None:
  point=marker@s['x'];prevpoint=marker@old['x'];depth=float(direction@((Tn-origin_T)-(point-origin_q)));prior_depth=float(direction@((T-origin_T)-(prevpoint-origin_q)));ds=float(direction@((Tn-T)-(point-prevpoint)));earned=Fc*max(ds,0.);work_earned+=earned;cut_numeric_loss+=.5*J*J/max(meff,1e-30) if J else 0.
  trial=ledger.trial(step,[[-width/2,prior_depth],[width/2,prior_depth]],[[-width/2,depth],[width/2,depth]],'edge',bool(np.any(eligible) and can_cut))
  if trial.required_work>earned+1e-10:status='cut_work_mismatch';b.set_state(**state_backup);s=old;b.sim_time-=dt;b.steps-=1;break
  ledger.commit(trial,earned,True)
  if ledger.covered.area>=width*.0015*(1-1e-8) and not cut_done:
   codes=s['codes'].copy();row=X[:,1]>X[:,1].max()-1e-8;codes[row]=np.where(X[row,0]<0,1,2);b.set_state(codes=codes);s=b.state();newcells=Cells(X,codes);newcert=newcells.certificate(s['x'],cad,Tn,motion_bound=motion)
   if not newcert['passed']:
    b.set_state(**state_backup);s=old;b.sim_time-=dt;b.steps-=1;status='new_surface_contact_stop';break
   cells=newcells;cut_done=True;events.append({'t':t+dt,'newly_labelled_particles':int(row.sum()),'fracture_work_J':ledger.fracture_work,'reference_area_m2':ledger.covered.area});status='first_paid_patch_committed'
 # Force and work ledger: contact work, physical cutting work and numerical projection loss distinct.
 Wtool+=float(np.sum(fp*(Tn-T)))+Fc*float(direction@(Tn-T));Dfr+=law['friction_power_W']*dt
 support=-b.mass*(bulk+dt*total_force/b.mass)[fixed].sum(0);dp=b.mass*(s['v'].astype(float)-old['v'].astype(float)).sum(0);maxbalance=max(maxbalance,float(np.linalg.norm(dp-dt*total_force.sum(0)-support)))
 if (step+1)%sample==0 or cut_done:
  E=float(.5*b.mass*np.sum(s['v'].astype(float)**2)+b.vol*energy_stress(s['F'].astype(float),b.mu,b.lam)[0].sum());rows.append({'t':t+dt,'force_N':force_norm,'cut_force_N':Fc,'relative_speed_m_s':u,'reference_depth_m':depth,'paid_area_m2':0. if ledger is None else float(ledger.covered.area),'fracture_J':0. if ledger is None else ledger.fracture_work,'earned_cut_work_J':work_earned,'tool_work_J':Wtool,'friction_J':Dfr,'cut_projection_loss_J':cut_numeric_loss,'bulk_kinetic_J':E,'minJ':float(np.linalg.det(s['F']).min()),'contact_points':int(eligible.sum())});snap.append((s['x'].copy(),s['v'].copy(),s['codes'].copy()));(R/'progress.json').write_text(json.dumps(rows[-1],indent=2))
 if cut_done:break
 if time.monotonic()-start>600:status='wall_cap';break
b.save(R/'final.npz');np.savez_compressed(R/'trajectory.npz',x=np.array([v[0] for v in snap]),v=np.array([v[1] for v in snap]),codes=np.array([v[2] for v in snap]),t=np.array([r['t'] for r in rows]));out={'status':status,'physical_topology_event':cut_done,'events':events,'dt':dt,'sim_time':b.sim_time,'wall_s':time.monotonic()-start,'peak_total_force_N':maxF,'max_impulse_balance_Ns':maxbalance,'initial_bulk_kinetic_J':initial_energy,'cut_ledger':None if ledger is None else ledger.state(),'last_certificate':cert if 'cert' in locals() else None,'rows':rows,'scope':'Bounded first paid crack-front patch on actual CAD-loaded MPM coupon; no tomato or full-slice claim'};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
