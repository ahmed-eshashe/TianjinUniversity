from pathlib import Path
import sys,time,json,argparse,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference import block,energy_stress
from physical_backend import PhysicalBackend
from contact_geometry import Cells
from fragment_contact import FragmentContact
p=argparse.ArgumentParser();p.add_argument('--half',action='store_true');p.add_argument('--tag',default='rhs_fixed');a=p.parse_args();R=W/'runs'/('recontact_'+a.tag+('_half' if a.half else ''));R.mkdir(exist_ok=False)
X=block(8,.0015);left=X[:,0]<0;right=~left;codes=np.where(left,1,2);b=PhysicalBackend(X);x=X.copy();x[:,0]+=.0001*np.sign(X[:,0]);v=np.zeros_like(X);v[:,0]=np.where(left,.02,-.02);v[left,2]=.01;b.set_state(x=x,v=v,codes=codes);cells=Cells(X,codes);contact=FragmentContact(cells,x,left,right);dt=1.25e-5/(2 if a.half else 1);duration=.03;sample=round(.00025/dt);n=round(duration/dt);rows=[];snap=[];Dfr=0.;status='completed';start=time.monotonic();maxF=0.;maxmom=0.;maxnet=0.;maxpen=0.;s=b.check();p0=b.mass*s['v'].astype(float).sum(0);E0=float(.5*b.mass*np.sum(v*v));maxbalance=0.
for step in range(n):
 old=s;ev=contact.evaluate(s['x'],s['v']);maxF=max(maxF,ev['sum_force']);maxmom=max(maxmom,ev['net_moment']);maxnet=max(maxnet,ev['net_force'])
 if ev['sum_force']>2:status='force_stop';break
 b.physical_step(dt,ev['force']);s=b.check();contact.surface.update(s['x']);motion=float(np.linalg.norm(cells.C@(s['x']-old['x']),axis=1).max())*2+contact.surface.deviation();cert=cells.certificate(s['x'],contact.surface,limit=.0001,motion_bound=motion,cell_mask=left)
 if not cert['passed']:status='penetration_stop';b.set_state(x=old['x'],v=old['v'],F=old['F']);s=old;break
 maxpen=max(maxpen,cert.get('certified_max_penetration_bound_m') or 0.);Dfr+=ev['friction_power']*dt;maxbalance=max(maxbalance,float(np.linalg.norm(b.mass*s['v'].astype(float).sum(0)-p0)))
 if (step+1)%sample==0 or step==n-1:
  new=contact.evaluate(s['x'],s['v']);E=float(.5*b.mass*np.sum(s['v'].astype(float)**2)+b.vol*energy_stress(s['F'].astype(float),b.mu,b.lam)[0].sum()+new['energy']);corn=cells.corners(s['x']);gap=float(corn[right,:,0].min()-corn[left,:,0].max());rows.append({'t':(step+1)*dt,'force':new['max_force'],'energy':E,'friction_J':Dfr,'energy_residual':E-E0+Dfr,'active':new['active'],'x_gap':gap,'mean_v_left':s['v'][left].mean(0).tolist(),'mean_v_right':s['v'][right].mean(0).tolist(),'minJ':float(np.linalg.det(s['F']).min())});snap.append((s['x'].copy(),s['v'].copy()));(R/'progress.json').write_text(json.dumps(rows[-1],indent=2))
 if time.monotonic()-start>600:status='wall_cap';break
b.save(R/'final.npz');np.savez_compressed(R/'trajectory.npz',x=np.array([z[0] for z in snap]),v=np.array([z[1] for z in snap]),t=np.array([r['t'] for r in rows]));out={'status':status,'dt':dt,'wall_s':time.monotonic()-start,'sim_time':b.sim_time,'peak_force_N':maxF,'max_net_force_N':maxnet,'max_net_moment_Nm':maxmom,'max_penetration_bound_m':maxpen,'total_momentum_error_Ns':maxbalance,'initial_energy_J':E0,'friction_dissipated_J':Dfr,'history_identical':bool(np.array_equal(codes,s['codes'])),'last_certificate':cert,'rows':rows,'scope':'Two pre-separated material fragments collide and slide. Contact fixture, not proof that a physical cutting run created the initial split.'};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
