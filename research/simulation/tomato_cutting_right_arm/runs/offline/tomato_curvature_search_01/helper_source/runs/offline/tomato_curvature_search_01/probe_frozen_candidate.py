"""Bounded numerical search diagnostic only: never advances physical history."""
import os,sys,fcntl,resource,signal,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:assert os.environ[n]=='1'
now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
lease=json.loads((R/'runs/offline/tomato_triangle_withdrawal_01/quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480;assert lease['maximum_reported_used_percent']<45
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
start=time.monotonic();sys.path.insert(0,str(R/'rl'))
import numpy as np
from scipy.sparse.linalg import lsmr
from tomato_coupled_contact import assemble_model,cut_pairs,supports
from tomato_blade_damage import EvolvingCohesion
from tomato_bonds import DamageState
from tomato_triangle_contact import triangle_geometry
from tomato_contact_spectral_search import solve_triangle_continuation

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
candidate=R/'runs/offline/tomato_optimizer_release_01/search_batch09_curvature/attempt011_11'
s=json.loads((candidate/'candidate.json').read_text());assert s['optimization_only'] and not s['passed']
for n,h in s['source_hashes'].items():assert digest(R/n)==h
assert digest(candidate/'guess.npy')==s['guess_sha256']
data=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((data/'surface_design.json').read_text());assign=json.loads((data/'mass_stiffness_assignments.json').read_text());points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs);model.cohesion.states=[DamageState(**v) for v in s['trial_damage_states']];x=np.load(candidate/'guess.npy')
geometry=triangle_geometry(design,points,pairs,float(points[pairs[:,0],2].max())-s['depth_mm']/1000);fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(points.size),ids)
C=geometry['matrix'];used=np.flatnonzero(geometry['active'])
def force_balance(x,rows):
 g=model.evaluate(x)['gradient_n'].ravel();loads=lsmr(C[rows][:,free].T,g[free],atol=1e-13,btol=1e-13,maxiter=2500)[0];normal=C[rows].T@loads
 return float(np.linalg.norm((g-normal)[free])/max(np.linalg.norm(g[ids]),np.linalg.norm(normal),1e-4))
rows=used[np.array(s['optimizer_active_rows'],dtype=int)];initial_force=force_balance(x,rows);initial_energy=model.evaluate(x)['energy_j']
result=solve_triangle_continuation(model,x,fixed,geometry,max_iterations=6,initial_active=s['optimizer_active_rows']);final,lam,state,trace,ok,*_=result
rows=used[np.array(trace[-1]['optimizer_active_rows'],dtype=int)];final_force=force_balance(final,rows)
assert not any(n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'} for n in sys.modules)
for n,h in s['source_hashes'].items():assert digest(R/n)==h
report={'optimization_only':True,'physical_endpoint_accepted':False,'physical_trajectory_advanced':False,'damage_modified':False,'work_modified':False,'frozen_trial_damage_only':True,'depth_mm':s['depth_mm'],'source_candidate':str(candidate.relative_to(R)),'source_candidate_sha256':digest(candidate/'candidate.json'),'previous_summary_sha256':s['previous_summary_sha256'],'source_hashes':s['source_hashes']|{str(p.relative_to(R)):digest(p) for p in [R/'rl/tomato_contact_spectral_search.py',Path(__file__)]},'initial_force_residual':initial_force,'final_force_residual':final_force,'initial_energy_j':initial_energy,'final_energy_j':state['energy_j'],'frozen_search_converged':bool(ok),'min_gap_m':float((C@final.ravel()-geometry['bounds']).min()),'min_J':state['min_cell_ratio'],'trace':trace,'runtime_s':time.monotonic()-start,'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'simulator':False,'training':False}
np.save(F/'diagnostic_guess.npy',final);report['diagnostic_guess_sha256']=digest(F/'diagnostic_guess.npy')
(F/'frozen_candidate_diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print({k:report[k] for k in ['initial_force_residual','final_force_residual','initial_energy_j','final_energy_j','frozen_search_converged','runtime_s','max_rss_bytes']})
