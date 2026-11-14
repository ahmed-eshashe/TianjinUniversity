from pathlib import Path
import sys,os,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate
from contact_surface import Surface
from blade_geometry import CAD,certify
from contact_gpu_precise import ContactGPU
from contact_law import evaluate
checks={};details={};start=time.perf_counter()
b=Body(n=2,h=.003);a=Aggregate(b);s=Surface(a,spacing=.00075);cad=CAD();fixed=np.isclose(b.grid[:,1],-.003)
g=ContactGPU(a,s,cad,[0,.00304,0],[0,-.00007,0],fixed=fixed)
checks['surface_area']=abs(s.area.sum()-6*.006**2)<1e-15
q,v=g.state();checks['initial_state']=np.max(abs(q))+np.max(abs(v))==0
ob=g.observe();checks['initial_no_force']=ob['sum_force_N']==0
# Query agreement in world coordinates against independent float64 CAD winding.
p=np.array([[0,.00302,0],[0,.00305,0],[0,.00307,.001],[.0005,.004,0],[-.0005,.004,0]])
u=cad.query(p,[0,.00304,0]);d=cad.query(p,[0,.00304,0],cpu=True)
checks['cad_distance']=np.max(abs(u['phi']-d['phi']))<2e-6;details['cad_max_error_m']=float(np.max(abs(u['phi']-d['phi'])))
# GPU vs independently evaluated CPU formula with prescribed penetrating pose.
g.T0=np.array([0,.00299,0]);g.travel[:]=0;g.graphs.clear();g.dispatch.clear()
g.observe();x=s.positions(q);query=cad.query(x,g.T0,cpu=True);law=evaluate(query['phi'],query['normal'],s.velocities(v),s.area)
checks['contact_force_cpu_gpu']=np.max(abs(g.cf.numpy()-law['force']))<1e-6
checks['contact_potential_cpu_gpu']=abs(g.cu.numpy().sum()-law['energy'])<1e-9
# Force pullback must preserve resultant, spatial moment, virtual power.
f=law['force'];pb=s.pullback(f);rng=np.random.default_rng(3);vel=rng.normal(size=v.shape)*.001
checks['resultant_pullback']=np.linalg.norm(f.sum(0)-pb.sum(0))<1e-12
checks['moment_pullback']=np.linalg.norm(np.cross(x,f).sum(0)-np.cross(b.grid[a.masters]+q,pb).sum(0))<1e-12
checks['power_pullback']=abs(np.sum(f*s.velocities(vel))-np.sum(pb*vel))<1e-12
c=certify(s.tets(q),cad,g.T0);checks['whole_volume_contact_certified']=c['passed'];details['certificate']=c
# A deliberately deeper blade must fail even with no boundary-center assumption.
c=certify(s.tets(q),cad,[0,.0025,0]);checks['deep_volume_rejected']=not c['passed'];details['deep_certificate']=c
# Recreate a safe dynamic instance after diagnostic configuration changes.
g=ContactGPU(Aggregate(b),s,cad,[0,.00304,0],[0,-.00007,0],fixed=fixed)
g.step(80);q,v=g.state();checks['finite_step']=np.isfinite(q).all() and np.isfinite(v).all();checks['correct_elapsed']=abs(g.observe()['time']-.001)<1e-8
checks['fixed_nodes']=np.max(abs(q[fixed]))==0 and np.max(abs(v[fixed]))==0
result={'checks':{k:bool(v) for k,v in checks.items()},'details':details,'samples':len(s.X),'wall_s':time.perf_counter()-start};result['status']='pass' if all(checks.values()) else 'failed';(W/'preflight_precise.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
