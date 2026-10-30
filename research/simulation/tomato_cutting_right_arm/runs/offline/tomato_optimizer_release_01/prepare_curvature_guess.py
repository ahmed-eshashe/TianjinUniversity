"""Uncommitted positions-only negative-curvature start; not a physical push."""
import argparse,fcntl,resource,signal,sys,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--amplitude-um',type=float,default=10.);a=p.parse_args();assert 0<a.amplitude_um<=100.
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
with (R/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import numpy as np
 sys.path.insert(0,str(R/'rl'))
 from tomato_coupled_contact import assemble_model,cut_pairs,supports
 from tomato_blade_damage import EvolvingCohesion
 from tomato_bonds import DamageState
 from tomato_triangle_contact import triangle_geometry
 def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 rejected=F/'search_batch03/attempt000_00';s=json.loads((rejected/'summary.json').read_text());assert not s['passed'] and s['flags']==['softening_stability']
 for n,h in s['source_hashes'].items():assert digest(R/n)==h
 for n,h in s['state_hashes'].items():assert digest(rejected/n)==h
 audit=json.loads((F/'rejected875_mode_audit.json').read_text());assert not audit['passed'] and audit['flags']==['softening_stability']
 previous=F/'search_batch04/attempt005_05';old=json.loads((previous/'summary.json').read_text());assert old['passed'] and old['source_hashes']==s['source_hashes']
 for n,h in old['state_hashes'].items():assert digest(previous/n)==h
 data=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((data/'surface_design.json').read_text());assign=json.loads((data/'mass_stiffness_assignments.json').read_text());points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs);model.cohesion.states=[DamageState(**v) for v in s['damage_states']]
 x=np.load(rejected/'positions.npy');direction=np.load(F/'rejected875_mode_direction.npy');assert np.isfinite(direction).all();direction/=np.linalg.norm(direction,axis=1).max()
 state=model.evaluate(x,tangent=True);d=direction.ravel();curvature=float(d@state['tangent_n_m']@d);gradient=float(state['gradient_n'].ravel()@d)
 checks=[]
 for h in [1e-5,1e-6,1e-7,1e-8,3e-9]:
  plus=model.evaluate(x+h*direction);minus=model.evaluate(x-h*direction)
  gradient_curvature=float((plus['gradient_n']-minus['gradient_n']).ravel()@d/(2*h))
  checks.append({'amplitude_m':h,'gradient_difference_curvature_n_m':gradient_curvature,'energy_difference_curvature_n_m':float((plus['energy_j']+minus['energy_j']-2*state['energy_j'])/h**2),'relative_gradient_curvature_error':abs(gradient_curvature-curvature)/max(abs(curvature),1e-12)})
 geometry=triangle_geometry(design,points,pairs,s['tip_z_m']);C,b=geometry['matrix'],geometry['bounds'];fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));tries=[]
 for sign in [-1.,1.]:
  guess=x+sign*a.amplitude_um*1e-6*direction;v=model.evaluate(guess)
  gap=float((C@guess.ravel()-b).min());support_error=float(np.max(np.abs(guess.ravel()[ids]-np.array([fixed[i] for i in ids]))))
  tries.append({'sign':sign,'energy_j':v['energy_j'],'energy_change_j':v['energy_j']-state['energy_j'],'minimum_contact_gap_m':gap,'support_error_m':support_error,'min_J':v['min_cell_ratio'],'admissible':gap>=-1e-9 and support_error<=1e-12})
 (F/('curvature_diagnostic_'+str(a.amplitude_um)+'.json')).write_text(json.dumps({'curvature_n_m':curvature,'directional_gradient_n':gradient,'derivative_checks':checks,'position_guess_checks':tries,'physical_endpoint_accepted':False},indent=2)+'\n')
 valid=[v for v in tries if v['admissible'] and v['energy_j']<state['energy_j']];assert valid,'No admissible lower-energy numerical start'
 chosen=min(valid,key=lambda v:v['energy_j']);guess=x+chosen['sign']*a.amplitude_um*1e-6*direction
 a.output.mkdir(parents=True,exist_ok=False);np.save(a.output/'guess.npy',guess)
 report={'passed':False,'optimization_only':True,'reason':'negative_curvature_positions_only_guess','depth_mm':s['depth_mm'],'previous_summary_sha256':digest(previous/'summary.json'),'guess_sha256':digest(a.output/'guess.npy'),'trial_damage_states':s['damage_states'],'trial_damage_seed_is_uncommitted':True,'trial_damage_seed_checkpoint':str(rejected.relative_to(R)),'optimizer_active_rows':None,'source_hashes':s['source_hashes'],'prediction_source_hashes':{str(Path(__file__).relative_to(R)):digest(Path(__file__))},'rejected_state_sha256':digest(rejected/'summary.json'),'mode_sha256':digest(F/'rejected875_mode_direction.npy'),'amplitude_m':a.amplitude_um*1e-6,'chosen_sign':chosen['sign'],'curvature_n_m':curvature,'directional_gradient_n':gradient,'derivative_checks':checks,'position_guess_checks':tries,'damage_predicted':False,'work_predicted':False,'physical_trajectory_advanced':False,'runtime_s':time.monotonic()-start,'simulator':False,'training':False}
 (a.output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['source_hashes','trial_damage_states']})
