"""Energy-screened curvature restart of optimizer guesses, never physical history."""
import argparse,fcntl,resource,signal,sys,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
with (R/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import numpy as np
 from scipy.sparse import diags
 from scipy.sparse.linalg import eigsh
 sys.path.insert(0,str(R/'rl'))
 from tomato_coupled_contact import assemble_model,cut_pairs,supports,proper_surface_intersections
 from tomato_blade_damage import EvolvingCohesion
 from tomato_bonds import DamageState
 from tomato_triangle_contact import triangle_geometry
 from tomato_linear_contact import affine_space
 from tomato_volume_protection import InfeasibleVolume
 def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 s=json.loads((a.candidate/'candidate.json').read_text());assert s['optimization_only'] and not s['passed']
 for n,h in s['source_hashes'].items():assert digest(R/n)==h
 assert digest(a.candidate/'guess.npy')==s['guess_sha256']
 data=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((data/'surface_design.json').read_text());assign=json.loads((data/'mass_stiffness_assignments.json').read_text());points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs);model.cohesion.states=[DamageState(**v) for v in s['trial_damage_states']];x=np.load(a.candidate/'guess.npy');state=model.evaluate(x,tangent=True)
 geometry=triangle_geometry(design,points,pairs,float(points[pairs[:,0],2].max())-s['depth_mm']/1000);C,b=geometry['matrix'],geometry['bounds'];used=np.flatnonzero(geometry['active']);active=used[np.array(s['optimizer_active_rows'],dtype=int)];fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));_,T=affine_space(C[active],b[active],fixed,points.size)
 h=T.T@state['tangent_n_m']@T;pre=diags(1/np.sqrt(np.maximum(np.abs(h.diagonal()),1e-6)));scaled=pre@h@pre;values,vectors=eigsh(scaled,k=1,which='SA',return_eigenvectors=True,tol=1e-5,maxiter=1600,ncv=80);least=float(values[0]);assert least<0,'No negative search curvature; use another diagnostic'
 direction=np.asarray(T@(pre@vectors[:,0])).reshape(-1,3);direction/=np.linalg.norm(direction,axis=1).max();tri=np.array([t for piece in design['pieces'] for t in piece['triangles']]);rest=points[tri];rn=np.cross(rest[:,1]-rest[:,0],rest[:,2]-rest[:,0]);tries=[];candidates=[]
 for micrometres in [.1,.5,1.,2.,5.,10.,20.,50.,100.]:
  for sign in [-1.,1.]:
   guess=x+sign*micrometres*1e-6*direction;gap=float((C@guess.ravel()-b).min());support_error=float(np.max(np.abs(guess.ravel()[ids]-np.array([fixed[i] for i in ids]))));q=guess[tri];normal=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);orientation=bool(np.all(np.einsum('ni,ni->n',normal,rn)>0))
   try:
    v=model.evaluate(guess);eligible=gap>=-1e-10 and support_error<=1e-12 and orientation and v['min_length_ratio']>=.1 and v['energy_j']<state['energy_j']
    rec={'amplitude_um':micrometres,'sign':sign,'energy_change_j':v['energy_j']-state['energy_j'],'minimum_contact_gap_m':gap,'support_error_m':support_error,'surface_orientation_valid':orientation,'min_J':v['min_cell_ratio'],'screen_passed':eligible}
    if eligible:candidates.append((v['energy_j'],guess,rec))
   except InfeasibleVolume:rec={'amplitude_um':micrometres,'sign':sign,'screen_passed':False,'volume_rejected':True}
   tries.append(rec)
 selected=None
 for energy,guess,rec in sorted(candidates,key=lambda v:v[0]):
  intersections=proper_surface_intersections(design,guess)[0];rec['proper_surface_intersections']=intersections
  if not intersections:selected=(guess,rec);break
 a.output.mkdir(parents=True,exist_ok=False)
 diagnostics={'optimization_only':True,'physical_endpoint_accepted':False,'source_candidate_sha256':digest(a.candidate/'candidate.json'),'search_eigenvalue':least,'eigen_residual_norm':float(np.linalg.norm(scaled@vectors[:,0]-least*vectors[:,0])),'trials':tries,'selected':selected[1] if selected else None}
 (a.output/'restart_diagnostic.json').write_text(json.dumps(diagnostics,indent=2)+'\n');assert selected,'No admissible lower-energy curvature restart'
 guess,rec=selected;np.save(a.output/'guess.npy',guess)
 report={'passed':False,'optimization_only':True,'reason':'negative_curvature_candidate_restart','depth_mm':s['depth_mm'],'previous_summary_sha256':s['previous_summary_sha256'],'guess_sha256':digest(a.output/'guess.npy'),'trial_damage_states':s['trial_damage_states'],'optimizer_active_rows':s['optimizer_active_rows'],'source_hashes':s['source_hashes'],'prediction_source_hashes':{str(Path(__file__).relative_to(R)):digest(Path(__file__))},'source_candidate_sha256':digest(a.candidate/'candidate.json'),'physical_trajectory_advanced':False,'damage_modified':False,'work_modified':False,'runtime_s':time.monotonic()-start,'simulator':False,'training':False}
 (a.output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print({'selected':rec,'runtime_s':report['runtime_s'],'optimization_only':True})
