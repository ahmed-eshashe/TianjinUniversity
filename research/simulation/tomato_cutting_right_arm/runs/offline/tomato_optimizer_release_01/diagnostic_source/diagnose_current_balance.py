"""Exact current KKT force diagnostic on an uncommitted search candidate."""
import fcntl,resource,signal,sys,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
with (R/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import numpy as np
 from scipy.sparse.linalg import lsmr
 sys.path.insert(0,str(R/'rl'))
 from tomato_coupled_contact import assemble_model,cut_pairs,supports
 from tomato_blade_damage import EvolvingCohesion
 from tomato_bonds import DamageState
 from tomato_triangle_contact import triangle_geometry
 from tomato_linear_contact import affine_space
 folder=F/'search_batch07/attempt011_11';s=json.loads((folder/'candidate.json').read_text());assert s['optimization_only'] and not s['passed']
 for n,h in s['source_hashes'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
 assert hashlib.sha256((folder/'guess.npy').read_bytes()).hexdigest()==s['guess_sha256']
 data=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((data/'surface_design.json').read_text());assign=json.loads((data/'mass_stiffness_assignments.json').read_text());points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs);model.cohesion.states=[DamageState(**v) for v in s['trial_damage_states']];x=np.load(folder/'guess.npy');state=model.evaluate(x,tangent=True)
 geometry=triangle_geometry(design,points,pairs,float(points[pairs[:,0],2].max())-s['depth_mm']/1000);C,b=geometry['matrix'],geometry['bounds'];used=np.flatnonzero(geometry['active']);active=used[np.array(s['optimizer_active_rows'],dtype=int)]
 fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(x.size),ids);g=state['gradient_n'].ravel()
 loads=lsmr(C[active][:,free].T,g[free],atol=1e-13,btol=1e-13,maxiter=2500);lam=np.zeros(len(b));lam[active]=loads[0];r=g-C.T@lam;scale=max(np.linalg.norm(g[ids]),np.linalg.norm(C.T@lam),1e-4);gap=C@x.ravel()-b
 _,T=affine_space(C[active],b[active],fixed,points.size)
 report={'optimization_only':True,'physical_endpoint_accepted':False,'depth_mm':s['depth_mm'],'exact_current_force_residual':float(np.linalg.norm(r[free])/scale),'projected_free_gradient_fraction':float(np.linalg.norm(T.T@g)/scale),'minimum_current_active_multiplier_n':float(lam[active].min()),'current_complementarity_n_m':float(np.max(np.abs(lam*gap))),'minimum_contact_gap_m':float(gap.min()),'last_predicted_force_residual':s['outer_iterations'][-1]['trace'][-1]['force_residual'],'lsmr_termination':int(loads[1]),'runtime_s':time.monotonic()-start,'simulator':False,'training':False}
 (F/'current_balance_diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
