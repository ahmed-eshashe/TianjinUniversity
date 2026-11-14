from pathlib import Path
import sys,os,json,time,argparse,numpy as np,traceback
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from contact_surface import Surface
from blade_geometry import CAD,certify
from contact_gpu import ContactGPU
p=argparse.ArgumentParser();p.add_argument('--half',action='store_true');p.add_argument('--spacing',type=float,default=.0005);p.add_argument('--case',default='edge',choices=['edge','miss','broad','slide']);o=p.parse_args()
name=o.case+('_half' if o.half else '')+'_s'+str(round(o.spacing*1e6));out=W/'runs'/name;out.mkdir(exist_ok=False)
a=Aggregate(Body(n=2,h=.003));b=a.body;s=Surface(a,o.spacing);cad=CAD();fixed=np.isclose(b.grid[:,1],-.003);T=np.array([0.,.00304,0.]);R=cad.R.copy();travel=np.array([0.,-.00007,0.]);dt=12.5e-6/(2 if o.half else 1)
if o.case=='miss':T[0]=.03
if o.case=='slide':travel[2]=.00003
if o.case=='broad':
 R=np.array([[0,1.,0],[0,0,1.],[1.,0,0]]);T=np.array([-.02,.004,0.])
 # Align intact face with CAD broad side using the preserved signed distance.
 top=np.isclose(s.X[:,1],.003)
 for _ in range(3):T[1]+=.00004-cad.query(s.X[top],T,R)['phi'].min()
g=ContactGPU(a,s,cad,T,travel,fixed=fixed,R=R,dt=dt)
rows=[];states=[];checks={};checks['initial_volume_clear']=certify(s.tets(a.q),cad,T,R)['passed'];E0=a.metrics()['U']+a.metrics()['T'];start=time.perf_counter();initial_obs=g.observe();checks['initial_force_zero']=initial_obs['sum_force_N']==0;status='completed';guard_cost=0.;maxbalance=0.;maxres=0.;wall=[]
try:
 for frame in range(52):
  t=time.perf_counter();g.checked_step(round(.00025/dt));stepcost=time.perf_counter()-t;wall.append(stepcost)
  obs=g.observe();q,v=g.state();m=g.aggregates[0].metrics();E=m['U']+m['T']+obs['contact_energy'];res=E-E0-obs['tool_work_J']+obs['friction_J'];balance=np.linalg.norm(m['momentum']-obs['material_impulse']-obs['support_impulse']);maxbalance=max(maxbalance,balance);maxres=max(maxres,abs(res));F=g.aggregates[0].body.fields()[2]
  row={k:x.tolist() if isinstance(x,np.ndarray) else x for k,x in obs.items()};row.update(t=(frame+1)*.00025,energy_J=E,residual_J=res,impulse_balance_Ns=float(balance),minJ=float(np.linalg.det(F).min()),certificate=g.last_certificate,wall_s=stepcost);rows.append(row);states.append((q.copy(),v.copy(),F.copy()));(out/'progress.json').write_text(json.dumps(row,indent=2))
except Exception as e:status='stopped';traceback.print_exc();(out/'exception.txt').write_text(repr(e))
checks['complete_cycle']=status=='completed';checks['loaded' if o.case!='miss' else 'near_miss_zero']=max([r['peak_N'] for r in rows],default=0)>1e-4 if o.case!='miss' else max([r['peak_N'] for r in rows],default=0)==0
checks['force_limit']=max([r['peak_N'] for r in rows],default=0)<=2.;checks['volume_certificates']=all(r['certificate']['passed'] for r in rows)
checks['positive_J']=all(r['minJ']>.1 for r in rows);checks['no_cut_created']=not g.aggregates[0].body.history
checks['momentum_balance']=maxbalance<1e-7
scale=max(max([abs(r['tool_work_J']) for r in rows],default=0),1e-8);checks['energy_balance']=maxres/scale<=.05
result={'status':status,'checks':{k:bool(v) for k,v in checks.items()},'dt_s':dt,'size_m':.006,'h_m':.003,'quadrature_spacing_m':o.spacing,'surface_samples':len(s.X),'max_energy_residual_J':maxres,'max_energy_relative':maxres/scale,'max_impulse_balance_Ns':maxbalance,'wall_s':time.perf_counter()-start,'physical_cut':False,'rows':rows};np.savez_compressed(out/'trajectory.npz',q=np.array([x[0] for x in states]),v=np.array([x[1] for x in states]),F=np.array([x[2] for x in states]));(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
