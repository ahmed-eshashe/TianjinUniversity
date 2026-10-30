"""Bounded saved-state cubic contact diagnostic. No mechanics/state acceptance."""
import os,sys,json,hashlib,resource,signal,fcntl,time,unittest
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent;V=R/'runs/offline/tomato_curvature_search_01'
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
start=time.monotonic();now=datetime.now(timezone.utc)
assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
lease=json.loads((R/'runs/offline/tomato_triangle_withdrawal_01/quota_lease.json').read_text())
assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480 and lease['maximum_reported_used_percent']<45
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:assert os.environ[n]=='1'
handles=[]
for name in ['logs/offline_overnight.lock','logs/right_arm_control.lock']:
 h=(R/name).open('a');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);handles.append(h)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for cohort,manifest in [(V,'source_snapshot.json'),(V,'helper_source_snapshot.json'),(R/'runs/offline/tomato_global_search_01','source_snapshot_v5.json')]:
 for n,h in json.loads((cohort/manifest).read_text()).items():assert digest(R/n)==h,n
front=V/'stability_frontier.json'
if front.exists():assert json.loads(front.read_text()).get('resolved') is True
sys.path.insert(0,str(R/'rl'));sys.path.insert(0,str(F))
import numpy as np
from curve_math import hermite,evaluate,restrict,gap_coefficients,scalar_minimum
suite=unittest.defaultTestLoader.discover(str(F),pattern='test_curve_math.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
(F/'tests.json').write_text(json.dumps({'tests':result.testsRun,'passed':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors)})+'\n')
assert result.wasSuccessful(),'Analytic reference tests failed; no saved-state geometry evaluated'
if '--tests-only' in sys.argv:sys.exit(0)
from tomato_coupled_contact import assemble_model,cut_pairs,supports
from tomato_linear_contact import independent_rows,affine_space
from tomato_triangle_contact import triangle_geometry,swept_triangle_gap
from tomato_blade_damage import BLADE
from audit_tomato_triangle_contact import minimum_polygon_gap
source=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
design=json.loads((source/'surface_design.json').read_text());assign=json.loads((source/'mass_stiffness_assignments.json').read_text())
points,_=assemble_model(design,assign,0.);pairs=cut_pairs(design)
fixed,_=supports(design,points,'indentation',0.);zero_fixed={i:0. for i in fixed}

def read(folder,allow_rejected=False):
 s=json.loads((folder/'summary.json').read_text());assert s['passed'] or (allow_rejected and s['flags']==['contact'])
 for n,h in s['source_hashes'].items():assert digest(R/n)==h
 for n,h in s['state_hashes'].items():assert digest(folder/n)==h
 x=np.load(folder/'positions.npy');lam=np.load(folder/'multipliers.npy')
 assert np.isfinite(x).all() and np.isfinite(lam).all()
 return s,x,lam

def endpoint_velocity(x,lam,tip,inside_tip,step,chord):
 g=triangle_geometry(design,points,pairs,tip);inside=triangle_geometry(design,points,pairs,inside_tip)
 strong=np.flatnonzero(lam>1e-9)
 if not np.all(g['active'][strong]&inside['active'][strong]):raise ValueError('Strong row activation changes at endpoint; unsupported')
 C=g['matrix'];rhs=step*(inside['d_bounds']-inside['d_matrix']@x.ravel())
 rows=independent_rows(C,strong,zero_fixed,points.size)
 offset,T=affine_space(C[rows],rhs[rows],zero_fixed,points.size)
 v=offset+T@(T.T@(chord-offset))
 residual=float(np.max(np.abs(C[strong]@v-rhs[strong]),initial=0))
 support=float(max(abs(v[i]) for i in zero_fixed))
 if residual>1e-10 or support>1e-14:raise ValueError('Velocity constraints inconsistent')
 return v,{'strong_rows':len(strong),'independent_rows':len(rows),'maximum_contact_velocity_residual_m':residual,'maximum_support_velocity_m':support,'chord_correction_norm_m':float(np.linalg.norm(v-chord))}

cases=json.loads((R/'runs/offline/tomato_global_search_01/swept_path_diagnostic.json').read_text())['records'];records=[]
for num,reference in enumerate(cases):
 folder=R/reference['checkpoint'];s,x1,lam1=read(folder,True);prev=R/s['previous_checkpoint'];ps,x0,lam0=read(prev)
 assert digest(folder/'summary.json')==reference['summary_sha256']
 assert digest(prev/'summary.json')==s['previous_summary_sha256']==reference['previous_summary_sha256']
 t0,t1=ps['tip_z_m'],s['tip_z_m'];dt=t1-t0;step=-dt;chord=(x1-x0).ravel()
 assert dt<0
 knots={0.,1.}
 for z in points[pairs[:,0],2]:
  for event in [z,z-BLADE['single_bevel_length_m']]:
   t=(event-t0)/dt
   if 0<t<1:knots.add(float(t))
 knots=sorted(knots)
 eps=min(knots[1],1-knots[-2])*1e-6
 v0,diag0=endpoint_velocity(x0,lam0,t0,t0+eps*dt,step,chord)
 v1,diag1=endpoint_velocity(x1,lam1,t1,t1-eps*dt,step,chord)
 p=hermite(x0.ravel(),x1.ravel(),v0,v1)
 assert np.max(np.abs(evaluate(p,0)-x0.ravel()))<1e-14 and np.max(np.abs(evaluate(p,1)-x1.ravel()))<1e-14
 # Fixed/guide coordinates remain fixed through all polynomial coefficients.
 ids=np.array(sorted(fixed));assert np.max(np.abs(p[1:,ids]))<1e-13
 path=F/('curve_%02d.npy'%num);np.save(path,p)
 best=None;dense_difference=0.;coefficient_error=0.
 for a,b in zip(knots[:-1],knots[1:]):
  ga=triangle_geometry(design,points,pairs,t0+a*dt);gb=triangle_geometry(design,points,pairs,t0+b*dt)
  gm=triangle_geometry(design,points,pairs,t0+(a+b)/2*dt);rows=np.flatnonzero(gm['active'])
  q=restrict(p,a,b);c=gap_coefficients(ga['matrix'],gb['matrix'],ga['physical'],gb['physical'],q)
  # Direct geometry checks ensure the matrix really is affine on this interval.
  for u in [.137,.5,.863]:
   t=a+(b-a)*u;g=triangle_geometry(design,points,pairs,t0+t*dt)
   direct=g['matrix']@evaluate(p,t)-g['physical'];predicted=np.polynomial.polynomial.polyval(u,c)
   coefficient_error=max(coefficient_error,float(np.max(np.abs(direct[rows]-predicted[rows]))))
  for row in rows:
   value,u=scalar_minimum(c[:,row]);sample=float(np.min(np.polynomial.polynomial.polyval(np.linspace(0,1,17),c[:,row])))
   # Dense samples may overestimate minimum, never underestimate it significantly.
   if sample<value-1e-12:raise ValueError('Extremum search misses sampled penetration')
   dense_difference=max(dense_difference,sample-value)
   if best is None or value<best['minimum_gap_m']:best={'minimum_gap_m':value,'row':int(row),'time_fraction':a+(b-a)*u,'activation_interval':[a,b],'interval_fraction':u}
 assert coefficient_error<1e-12
 t=best['time_fraction'];x=evaluate(p,t).reshape(x0.shape);g=triangle_geometry(design,points,pairs,t0+t*dt)
 row=best['row'];direct=float((g['matrix'].getrow(row)@x.ravel())[0]-g['physical'][row]);poly,n=minimum_polygon_gap(design,x,t0+t*dt,BLADE)
 assert abs(direct-best['minimum_gap_m'])<1e-12 and abs(poly-best['minimum_gap_m'])<1e-12
 linear=swept_triangle_gap(design,points,pairs,x0,x1,t0,t1)
 assert abs(linear-reference['minimum_gap_m'])<1e-12
 best.update(checkpoint=reference['checkpoint'],previous_checkpoint=s['previous_checkpoint'],summary_sha256=digest(folder/'summary.json'),previous_summary_sha256=digest(prev/'summary.json'),physical_endpoint_previously_accepted=s['passed'],original_flags=s['flags'],original_linear_minimum_gap_m=linear,candidate_minimum_satisfies_original_contact_allowance=best['minimum_gap_m']>=-1e-9,direct_row_gap_m=direct,independent_polygon_gap_m=poly,coefficient_direct_maximum_error_m=coefficient_error,dense_sampling_maximum_overestimate_m=dense_difference,endpoint_velocity_diagnostics=[diag0,diag1],curve_file=path.name,curve_sha256=digest(path),activation_intervals=len(knots)-1)
 records.append(best);print({k:best[k] for k in ['checkpoint','original_linear_minimum_gap_m','minimum_gap_m','candidate_minimum_satisfies_original_contact_allowance']},flush=True)
assert not any(n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'} for n in sys.modules)
report={'diagnostic_only':True,'mechanical_trajectory_accepted':False,'history_or_work_or_damage_changed':False,'physical_laws_changed':False,'thresholds_changed':False,'new_physical_endpoints_accepted':False,'simulator':False,'training':False,'qualification_missing':['intermediate equilibrium','constitutive history and damage evolution','work and fracture-energy balance','continuous volume and surface validity','certified floating-point root bounds'],'reference_tests':result.testsRun,'records':records,'source_hashes':{str(p.relative_to(R)):digest(p) for p in [Path(__file__),F/'curve_math.py',F/'test_curve_math.py']},'input_geometry_hashes':{str((source/n).relative_to(R)):digest(source/n) for n in ['surface_design.json','mass_stiffness_assignments.json']},'runtime_s':time.monotonic()-start,'max_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024}
assert datetime.now(timezone.utc)<datetime(2026,10,26,4,54,40,tzinfo=timezone.utc)
(F/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print({'runtime_s':report['runtime_s'],'max_rss_bytes':report['max_rss_bytes'],'physical_trajectory_accepted':False})
