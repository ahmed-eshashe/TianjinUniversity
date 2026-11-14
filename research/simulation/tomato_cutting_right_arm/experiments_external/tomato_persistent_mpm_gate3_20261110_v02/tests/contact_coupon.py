from pathlib import Path
import sys,json,time,argparse,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference import block,energy_stress
from physical_backend import PhysicalBackend
from contact_geometry import CAD,Cells
from contact_law import evaluate
p=argparse.ArgumentParser();p.add_argument('--half',action='store_true');p.add_argument('--name',default='edge');p.add_argument('--tag',default='clock');a=p.parse_args();name=a.name+'_'+a.tag+('_half' if a.half else '');R=W/'runs'/name;R.mkdir(exist_ok=False)
X=block(8,.0015);fixed=np.isclose(X[:,1],X[:,1].min());b=PhysicalBackend(X,fixed=fixed);cad=CAD();cells=Cells(X,np.zeros(len(X),int));dt=1.25e-5/(2 if a.half else 1);K=1e9;mu=.2
# Finite original CAD edge load/hold/unload; no fracture yet.
T0=np.array([0,.00605,0.]);Rtool=cad.rotation.copy();stroke=.00009;load=.005;hold=.003;duration=.013
if a.name=='broad':
 Rtool=np.array([[0,1.,0],[0,0,1.],[1.,0,0]]);T0=np.array([-.02,.007,0.]);pts=cells.points(X)
 for _ in range(3):
  q=cad.query(pts,T0,Rtool);phi=q['phi'];T0[1]+=.00005-phi.min()
if a.name=='miss':T0[0]=.02

def pose(t):
 if t<load:s=.5*(1-np.cos(np.pi*t/load));speed=.5*np.pi/load*np.sin(np.pi*t/load)
 elif t<load+hold:s=1.;speed=0.
 else:u=min(1.,(t-load-hold)/load);s=.5*(1+np.cos(np.pi*u));speed=-.5*np.pi/load*np.sin(np.pi*u)
 return T0-[0,stroke*s,0],np.array([0,-stroke*speed,0])

def energy(s):return float(.5*b.mass*np.sum(s['v'].astype(float)**2)+b.vol*energy_stress(s['F'].astype(float),b.mu,b.lam)[0].sum())
rows=[];snap=[];Wtool=0.;Dfr=0.;supportJ=np.zeros(3);toolJ=np.zeros(3);t0=time.monotonic();s=b.state();E0=energy(s);max_force=0.;maxpen=0.;status='completed';max_balance=0.;max_certificate_queries=0;n=round(duration/dt);sample=round(.00025/dt)
initial=cells.certificate(s['x'],cad,*[pose(0)[0]],Rtool)
if not initial['passed']:raise RuntimeError(initial)
for step in range(n):
 t=step*dt;T,vt=pose(t);Tnext,_=pose((step+1)*dt);old=s;q=cells.points(old['x']);vq=cells.Q@old['v'];ev=cad.query(q,T,Rtool);law=evaluate(ev['phi'],ev['normal'],vq-vt,cells.area,K,mu);f=law['force'];fp=cells.pullback(f);reaction=-f.sum(0);moment=-np.cross(q-T,f).sum(0)
 if max(np.linalg.norm(reaction),law['sum_magnitudes_N'])>2:status='force_stop';break
 b.physical_step(dt,fp);s=b.check();motion=(float(np.linalg.norm(cells.C@(s['x']-old['x']),axis=1).max())+np.linalg.norm(Tnext-T));cert=cells.certificate(s['x'],cad,Tnext,Rtool,motion_bound=motion);max_certificate_queries=max(max_certificate_queries,cert['queries'])
 if not cert['passed']:
  b.set_state(x=old['x'],v=old['v'],F=old['F']);s=old;status='penetration_or_uncertified_stop';break
 qs=cells.points(s['x']);dq=qs-q;deltaT=Tnext-T;Wtool+=float(np.sum(f*deltaT));Dfr+=float(-np.sum(law['friction_force']*(dq-deltaT)));toolJ+=dt*fp.sum(0);sj=b.support.numpy().astype(float).sum(0);supportJ+=sj
 dp=b.mass*(s['v'].astype(float)-old['v'].astype(float)).sum(0);max_balance=max(max_balance,float(np.linalg.norm(dp-dt*fp.sum(0)-sj)));max_force=max(max_force,float(np.linalg.norm(reaction)),law['sum_magnitudes_N']);maxpen=max(maxpen,cert.get('certified_max_penetration_bound_m') or 0.)
 if (step+1)%sample==0 or step==n-1:
  newev=cad.query(qs,Tnext,Rtool);newlaw=evaluate(newev['phi'],newev['normal'],cells.Q@s['v']-pose((step+1)*dt)[1],cells.area,K,mu);Uc=newlaw['energy'];reaction=-newlaw['force'].sum(0);moment=-np.cross(qs-Tnext,newlaw['force']).sum(0);E=energy(s)+Uc;rows.append({'t':(step+1)*dt,'reaction':reaction.tolist(),'moment':moment.tolist(),'Wtool':Wtool,'Dfriction':Dfr,'energy':E,'energy_residual':E-E0-Wtool+Dfr,'penetration_bound':maxpen,'minJ':float(np.linalg.det(s['F']).min()),'max_speed':float(np.linalg.norm(s['v'],axis=1).max())});snap.append((s['x'].copy(),s['v'].copy()));(R/'progress.json').write_text(json.dumps(rows[-1],indent=2))
 if time.monotonic()-t0>600:status='wall_cap';break
np.savez_compressed(R/'trajectory.npz',x=np.array([x[0] for x in snap]),v=np.array([x[1] for x in snap]),t=np.array([r['t'] for r in rows]));b.save(R/'final.npz');out={'status':status,'dt':dt,'sim_time':b.sim_time,'wall_s':time.monotonic()-t0,'max_force_N':max_force,'max_penetration_bound_m':maxpen,'max_impulse_balance_error_Ns':max_balance,'reaction_impulse_Ns':(-toolJ).tolist(),'support_impulse_Ns':supportJ.tolist(),'work_J':Wtool,'friction_J':Dfr,'max_certificate_queries':max_certificate_queries,'initial_certificate':initial,'last_certificate':cert,'rows':rows,'scope':'Finite CAD contact on supported 12mm coupon; no fracture; reconstructed entire-cell volume certificate each accepted step'};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
