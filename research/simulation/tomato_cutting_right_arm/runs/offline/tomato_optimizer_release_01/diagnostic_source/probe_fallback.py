"""Uncommitted optimizer diagnostic; cannot create accepted physical states."""
import argparse,fcntl,resource,signal,sys,json,hashlib,time,os
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['fallback'],required=True);a=p.parse_args();out=F/a.mode;out.mkdir(exist_ok=False)
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
with (R/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import numpy as np
 sys.path.insert(0,str(R/'rl'))
 from tomato_coupled_contact import assemble_model,cut_pairs,supports
 from tomato_blade_damage import EvolvingCohesion
 from tomato_bonds import DamageState
 from tomato_triangle_contact import triangle_geometry
 from tomato_contact_search import solve_triangle_continuation
 os.environ['TOMATO_DIAGNOSTIC_OUTPUT']=str(out);os.environ['TOMATO_SINGLE_RELEASE']='1' if a.mode=='single' else '0'
 previous=R/'runs/offline/tomato_triangle_withdrawal_01/insertion_batch02/attempt001_01';s=json.loads((previous/'summary.json').read_text())
 for n,h in s['source_hashes'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
 for n,h in s['state_hashes'].items():assert hashlib.sha256((previous/n).read_bytes()).hexdigest()==h
 data=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((data/'surface_design.json').read_text());assign=json.loads((data/'mass_stiffness_assignments.json').read_text());points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs);model.cohesion.states=[DamageState(**v) for v in s['damage_states']]
 prediction=R/'runs/offline/tomato_triangle_withdrawal_01/insertion_batch02/prediction002';v=json.loads((prediction/'candidate.json').read_text());assert v['previous_summary_sha256']==hashlib.sha256((previous/'summary.json').read_bytes()).hexdigest();assert hashlib.sha256((prediction/'guess.npy').read_bytes()).hexdigest()==v['guess_sha256'];x=np.load(prediction/'guess.npy')
 geometry=triangle_geometry(design,points,pairs,float(points[pairs[:,0],2].max())-.008375);fixed,_=supports(design,points,'indentation',0.)
 try:
  result=solve_triangle_continuation(model,x,fixed,geometry,max_iterations=6);x,lam,state,trace,ok,*_=result;np.save(out/'guess.npy',x)
  report={'search_converged':ok,'trace':trace,'exception':None}
 except ValueError as e:report={'search_converged':False,'exception':str(e)}
 report.update({'mode':a.mode,'optimization_only':True,'physical_endpoint_accepted':False,'runtime_s':time.monotonic()-start,'forbidden_imports':[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]})
 (out/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
