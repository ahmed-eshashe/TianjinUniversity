from pathlib import Path
import sys,os,json,numpy as np,time,traceback
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from poly_surface import Surface
from blade_geometry import CAD,certify
from rk4_contact_gpu import ContactGPU
b=Body(n=2,h=.003);b.split([1.,0,0],.0001);a=Aggregate(b);pc,nc=a.body.components();right=max(np.unique(pc),key=lambda c:np.mean(a.body.X[pc==c,0]));right_nodes=nc[a.masters]==right;a.q[right_nodes,0]= .0042;a.q[~right_nodes,0]=-.0042;a.sync();q0=a.q.copy();s=Surface(a);cad=CAD();T=np.array([.0001,-.03,0]);# Locate an admissible starting pose using the whole material, not vertices.
left_face=.0001-.0042;T[0]=left_face-cad.vertices[:,2].min()+.00008
lo=T[0]-.008;hi=T[0];vtets=s.tets(a.q)
assert certify(vtets,cad,T,cad.R,limit=-.00004)['passed']
for _ in range(14):
 mid=(lo+hi)/2;probe=T.copy();probe[0]=mid;clear=certify(vtets,cad,probe,cad.R,limit=-.00004)['passed']
 if clear:hi=mid
 else:lo=mid
T[0]=hi+.000003;travel=np.array([-.00007,0,0]);fixed=np.isclose(a.body.grid[a.masters,1],-.003);g=ContactGPU(a,s,cad,T,travel,fixed=fixed);out=W/'runs/exposed_face_contact_r5';out.mkdir(exist_ok=False);checks={'initial_whole_volume_clear':certify(s.tets(a.q),cad,T,cad.R,limit=0.)['passed'],'initial_force_zero':g.observe()['sum_force_N']==0};assert all(checks.values()),checks;rows=[];states=[];E0=a.metrics()['U']+a.metrics()['T'];start=time.perf_counter();status='completed';worst_energy=0.;max_idle=0.;max_imp=0.
try:
 for frame in range(52):
  g.checked_step(20);q,v=g.state();obs=g.observe();m=g.aggregates[0].metrics();res=m['U']+m['T']+obs['contact_energy']-E0-obs['tool_work_J']+obs['friction_J'];worst_energy=max(worst_energy,abs(res));max_idle=max(max_idle,float(np.max(abs(q[right_nodes]-q0[right_nodes]))),float(np.max(abs(v[right_nodes]))));max_imp=max(max_imp,float(np.linalg.norm(m['momentum']-obs['material_impulse']-obs['support_impulse'])));row={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in obs.items()};row.update(certificate=g.last_certificate,energy_residual_J=res,t=(frame+1)*.00025);rows.append(row);states.append((q.copy(),v.copy()));(out/'progress.json').write_text(json.dumps(row,indent=2))
except Exception as e:status='stopped';traceback.print_exc();(out/'exception.txt').write_text(repr(e));(out/'rejected_certificate.json').write_text(json.dumps({**getattr(g,'last_certificate',{}),'maxspeed':float(g.maxspeed.numpy()[0]),'q_max_change':float(np.max(abs(g.q_view[:g.n]-q0))),'v_max':float(np.max(abs(g.v_view[:g.n])))},indent=2));np.savez(out/'rejected_state.npz',q=g.q_view[:g.n],v=g.v_view[:g.n],q0=q0)
scale=max(max([abs(r['tool_work_J']) for r in rows],default=0),1e-8);checks.update(complete_cycle=status=='completed',positive_contact=max([r['peak_N'] for r in rows],default=0)>1e-4,force_stop=max([r['peak_N'] for r in rows],default=0)<=2,volume_bounds=all(r['certificate']['passed'] for r in rows),independent_other_fragment=max_idle<1e-7,energy=worst_energy/scale<=.05,impulse=max_imp<1e-7,history_preserved=g.aggregates[0].body.history==b.history)
r={'checks':{k:bool(v) for k,v in checks.items()},'passed':all(checks.values()),'status':status,'wall_s':time.perf_counter()-start,'energy_relative':worst_energy/scale,'unloaded_fragment_max_motion_or_velocity':max_idle,'impulse_residual_Ns':max_imp,'physical_cut':False,'initial_tool_position':T.tolist(),'scope':'Pre-separated geometric fixture only: one newly exposed face loaded by original CAD broad side; not a fracture qualification.','rows':rows};(out/'result.json').write_text(json.dumps(r,indent=2));np.savez_compressed(out/'trajectory.npz',q=[s[0] for s in states],v=[s[1] for s in states]);print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2))
