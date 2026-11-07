"""Full actual-mesh implicit loading with committed irreversible patch damage."""
import argparse,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/9600

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;records=[]
 def stop(*args):raise InterruptedError('Actual-mesh material evolution stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_bonds import DamageState,update_damage
  from tomato_surface_cohesion import patch_response
  from tomato_blade_damage import fracture_loss
  from tomato_volume_protection import ProtectedModel
  wp.init();wp.set_device('cuda:0');data=registry();model=build_model(data);solver=configure_solver(model,data,iterations=512);sin=model.state();sout=model.state();x=sin.particle_q.numpy();right=np.array([n['side']=='remainder' for n in data['design']['nodes']]);x[right,0]+=.00095;velocity=np.zeros_like(x);velocity[right,0]=1.;velocity[~right,0]=-1.
  for state in (sin,sout):state.particle_q.assign(wp.array(x,dtype=wp.vec3));state.particle_qd.assign(wp.array(velocity,dtype=wp.vec3));state.clear_forces()
  mass=model.particle_mass.numpy().astype(float);pairs=data['pairs'];rest=np.asarray(data['cohesion'].reference_gaps,dtype=np.float32);patches=data['cohesion'].patches
  def expected_history(positions,old):
   gaps=positions[pairs[:,1]]-positions[pairs[:,0]]-rest;result=[]
   for patch,previous in zip(patches,old):
    u=patch_response(gaps[patch['indices']],patch['weights'],patch['stiffness'],0.)['energy_j'];q=(2*u/patch['law'].stiffness_n_m)**.5;new=update_damage(patch['law'],DamageState(*previous),q,eligible=True);result.append([new.kappa_m,new.damage])
   return np.asarray(result)
  initial_history=expected_history(x,np.zeros((47,2)));solver.history.assign(wp.array(initial_history,dtype=wp.vec2));solver.eligible.fill_(1)
  bulk=ProtectedModel(data['x'],model.spring_indices.numpy().reshape(-1,2),model.spring_rest_length.numpy().astype(float),model.spring_stiffness.numpy().astype(float),data['cells'],data['volumes'])
  def energy(positions,vel,history):
   gaps=positions[pairs[:,1]]-positions[pairs[:,0]]-rest;potential=bulk.evaluate(positions.astype(float))['energy_j'];fracture=0.
   for patch,state in zip(patches,history):potential+=patch_response(gaps[patch['indices']],patch['weights'],patch['stiffness'],float(state[1]))['energy_j'];fracture+=fracture_loss(patch['law'],DamageState(*state))
   kinetic=float(.5*np.sum(mass[:,None]*vel.astype(float)**2));return dict(kinetic_j=kinetic,potential_j=potential,fracture_dissipation_j=fracture,total_j=kinetic+potential+fracture)
  initial_history=solver.history.numpy().astype(float);initial_energy=energy(x,velocity,initial_history);initial_momentum=(mass[:,None]*velocity).sum(axis=0)
  for i in range(8):
   if (out/'stop.request').exists():raise InterruptedError('Stopped between full damage intervals')
   old=solver.history.numpy().copy();solver.invalid.zero_();solver.volume_invalid.zero_();solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1;x=sout.particle_q.numpy();v=sout.particle_qd.numpy();expected=expected_history(x,old);gaps=x[pairs[:,1]]-x[pairs[:,0]]-rest;write(out,'precommit_geometry.json',dict(interval=i,min_normal_gap_m=float(min(gaps[:,0])),compressed_shearing_pairs=int(sum((gaps[:,0]<-1e-12)&(np.linalg.norm(gaps[:,1:],axis=1)>1e-12))),volume_trial_clips=int(solver.volume_clip_count.numpy()[0])));solver.commit_cohesion(sout);wp.synchronize();actual=solver.history.numpy();qerror=float(np.max(abs(actual[:,0]-expected[:,0])));derror=float(np.max(abs(actual[:,1]-expected[:,1])));e=energy(x,v,actual);gain=e['total_j']-initial_energy['total_j'];me=float(np.linalg.norm((mass[:,None]*v).sum(axis=0)-initial_momentum));ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
   record=dict(interval=i,max_history_error_m=qerror,max_damage_error=derror,min_damage=float(min(actual[:,1])),max_damage=float(max(actual[:,1])),patches_increased=int(sum(actual[:,1]>old[:,1])),energy=e,energy_gain_j=gain,momentum_error_ns=me,min_volume_ratio=float(min(ratios)));records.append(record);write(out,'full_damage_partial.json',dict(initial_energy=initial_energy,records=records))
   if qerror>1e-7 or derror>1e-6 or np.any(actual<old):raise ValueError('Actual-mesh history update differs from independent law')
   if gain>.01*max(abs(initial_energy['total_j']),abs(e['total_j']),1e-12)+1e-12:raise ValueError('Actual-mesh material evolution creates excess energy')
   if me>2e-7 or min(ratios)<=.1 or not np.isfinite(x).all():raise ValueError(f'Full damage mechanical gate {me=}')
   sin,sout=sout,sin
  final=solver.history.numpy();increased=int(sum(final[:,1]>initial_history[:,1]))
  if increased<1 or steps!=8:raise ValueError('No evolving damage exercised')
  write(out,'full_damage_measurements.json',dict(records=records,initial_energy=initial_energy,initial_history=initial_history.tolist(),final_history=final.tolist(),patches_increased=increased,newton_steps=steps,nodes=model.particle_count,patches=47,dt_s=DT,volume_trial_clips=int(solver.volume_clip_count.numpy()[0]),scope='Actual full mesh with explicit all-patch eligibility, a consistent preloaded history and prescribed initial outward velocities. No knife eligibility detector, robot, rotating-frame or experimental material qualification.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,full_damage_passed=passed,newton_steps=steps,controlled_steps=steps,full_damage_intervals=len(records)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
