"""Capped target-specific numerical starting guess, never a physical endpoint."""
import argparse,os,sys,fcntl,resource,signal,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--iterations',type=int,default=30);a=p.parse_args();assert 1<=a.iterations<=30
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:assert os.environ[n]=='1'
now=datetime.now(timezone.utc);assert now<datetime(2026,10,28,8,18,0,tzinfo=timezone.utc)
lease=json.loads((R/'runs/offline/tomato_continuation_20261027/quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480 and lease['maximum_reported_used_percent']<45
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for manifest in [F/'source_snapshot.json',R/'runs/offline/tomato_curvature_search_01/source_snapshot.json',R/'runs/offline/tomato_curvature_search_01/helper_source_snapshot.json']:
 for n,h in json.loads(manifest.read_text()).items():assert digest(R/n)==h
for folder in [R/'runs/offline/tomato_curvature_search_01',R/'runs/offline/tomato_optimizer_release_01']:
 if (folder/'stability_frontier.json').exists():assert json.loads((folder/'stability_frontier.json').read_text()).get('resolved',False)
assert json.loads((F/'tests.json').read_text())['passed'] and json.loads((F/'tests.json').read_text())['tests']==143
s=json.loads((a.candidate/'candidate.json').read_text());old=json.loads((a.previous/'summary.json').read_text());audit=json.loads((a.previous.parent/(a.previous.name+'_audit.json')).read_text())
assert s['optimization_only'] and not s['passed'];assert old['passed'] and audit['passed'] and old['backend']=='triangle_spectral_evolving_v1'
assert digest(a.previous/'summary.json')==s['previous_summary_sha256'];assert 0<s['depth_mm']-old['depth_mm']<=.25000001
assert s['source_hashes']==old['source_hashes']
for n,h in s['source_hashes'].items():assert digest(R/n)==h
for n,h in old['state_hashes'].items():assert digest(a.previous/n)==h
assert digest(a.candidate/'guess.npy')==s['guess_sha256'];source_hashes=s['source_hashes']|{str(p.relative_to(R)):digest(p) for p in [R/'rl/tomato_contact_global_search.py',Path(__file__).resolve()]}
start=time.monotonic();sys.path.insert(0,str(R/'rl'))
import numpy as np
from scipy.sparse.linalg import lsmr
from tomato_coupled_contact import assemble_model,cut_pairs,supports
from tomato_blade_damage import EvolvingCohesion
from tomato_bonds import DamageState
from tomato_triangle_contact import triangle_geometry
from tomato_contact_global_search import solve_triangle_continuation
data=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((data/'surface_design.json').read_text());assign=json.loads((data/'mass_stiffness_assignments.json').read_text());points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs);model.cohesion.states=[DamageState(**v) for v in s['trial_damage_states']];x=np.load(a.candidate/'guess.npy')
geometry=triangle_geometry(design,points,pairs,float(points[pairs[:,0],2].max())-s['depth_mm']/1000);fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(points.size),ids);C=geometry['matrix'];used=np.flatnonzero(geometry['active'])
def force_balance(x,rows):
 g=model.evaluate(x)['gradient_n'].ravel();loads=lsmr(C[rows][:,free].T,g[free],atol=1e-13,btol=1e-13,maxiter=2500)[0];normal=C[rows].T@loads
 return float(np.linalg.norm((g-normal)[free])/max(np.linalg.norm(g[ids]),np.linalg.norm(normal),1e-4))
rows=used[np.array(s['optimizer_active_rows'],dtype=int)];initial_force=force_balance(x,rows);initial_energy=model.evaluate(x)['energy_j']
final,lam,state,trace,ok,*_=solve_triangle_continuation(model,x,fixed,geometry,max_iterations=a.iterations,initial_active=s['optimizer_active_rows'])
rows=used[np.array(trace[-1]['optimizer_active_rows'],dtype=int)];final_force=force_balance(final,rows)
assert np.isfinite(final).all() and state['energy_j']<=initial_energy+1e-14
assert [v.__dict__ for v in model.cohesion.states]==s['trial_damage_states']
assert not any(n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'} for n in sys.modules)
for n,h in source_hashes.items():assert digest(R/n)==h
for n,h in old['state_hashes'].items():assert digest(a.previous/n)==h
out=a.output;out.mkdir(parents=True,exist_ok=False);np.save(out/'guess.npy',final)
report={'passed':False,'optimization_only':True,'reason':'target_specific_frozen_global_search_guess','depth_mm':s['depth_mm'],'previous_summary_sha256':s['previous_summary_sha256'],'guess_sha256':digest(out/'guess.npy'),'trial_damage_states':s['trial_damage_states'],'optimizer_active_rows':trace[-1]['optimizer_active_rows'],'source_hashes':s['source_hashes'],'prediction_source_hashes':{n:h for n,h in source_hashes.items() if n not in s['source_hashes']},'source_candidate_sha256':digest(a.candidate/'candidate.json'),'physical_endpoint_accepted':False,'damage_modified':False,'work_modified':False,'physical_trajectory_advanced':False,'simulator':False,'training':False}
diagnostic={'optimization_only':True,'physical_endpoint_accepted':False,'initial_force_residual':initial_force,'final_force_residual':final_force,'initial_energy_j':initial_energy,'final_energy_j':state['energy_j'],'frozen_search_converged':bool(ok),'minimum_gap_m':float((C@final.ravel()-geometry['bounds']).min()),'min_J':state['min_cell_ratio'],'trace':trace,'source_hashes':source_hashes,'source_candidate_sha256':digest(a.candidate/'candidate.json'),'previous_summary_sha256':s['previous_summary_sha256'],'guess_sha256':digest(out/'guess.npy'),'runtime_s':time.monotonic()-start,'max_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,'simulator':False,'training':False}
(out/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');(out/'diagnostic.json').write_text(json.dumps(diagnostic,indent=2)+'\n');print({k:diagnostic[k] for k in ['initial_force_residual','final_force_residual','initial_energy_j','final_energy_j','frozen_search_converged','runtime_s','max_rss_bytes']})
