"""Controlled tensile loading of all actual patch registries with native bulk motion."""
import argparse,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;records=[]
 def stop(*args):raise InterruptedError('Actual-mesh material loading stopped')
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
  wp.init();wp.set_device('cuda:0');data=registry();pairs=data['pairs'];fixed=np.unique(pairs);model=build_model(data,fixed_nodes=fixed);solver=configure_solver(model,data,iterations=512);sin=model.state();sout=model.state();x=sin.particle_q.numpy();original=x.copy();right=np.array([n['side']=='remainder' for n in data['design']['nodes']]);x[right,0]+=.00095/2;x[~right,0]-=.00095/2;velocity=np.zeros_like(x)
  for state in (sin,sout):state.particle_q.assign(wp.array(x,dtype=wp.vec3));state.particle_qd.zero_();state.clear_forces()
  mass=model.particle_mass.numpy().astype(float);rest=np.asarray(data['cohesion'].reference_gaps,dtype=np.float32);patches=data['cohesion'].patches;solver.eligible.fill_(1)
  def expected_history(positions,old):
   gaps=positions[pairs[:,1]]-positions[pairs[:,0]]-rest;result=[]
   for patch,previous in zip(patches,old):
    u=patch_response(gaps[patch['indices']],patch['weights'],patch['stiffness'],0.)['energy_j'];q=(2*u/patch['law'].stiffness_n_m)**.5;state=update_damage(patch['law'],DamageState(*previous),q,eligible=True);result.append([state.kappa_m,state.damage])
   return np.asarray(result)
  bulk=ProtectedModel(data['x'],model.spring_indices.numpy().reshape(-1,2),model.spring_rest_length.numpy().astype(float),model.spring_stiffness.numpy().astype(float),data['cells'],data['volumes'])
  def energy(positions,vel,history):
   gaps=positions[pairs[:,1]]-positions[pairs[:,0]]-rest;potential=bulk.evaluate(positions.astype(float))['energy_j'];fracture=0.
   for patch,state in zip(patches,history):potential+=patch_response(gaps[patch['indices']],patch['weights'],patch['stiffness'],float(state[1]))['energy_j'];fracture+=fracture_loss(patch['law'],DamageState(*state))
   kinetic=float(.5*np.sum(mass[:,None]*vel.astype(float)**2));return dict(kinetic_j=kinetic,potential_j=potential,fracture_dissipation_j=fracture,total_j=kinetic+potential+fracture)
  initial_history=expected_history(x,np.zeros((47,2)));solver.history.assign(wp.array(initial_history,dtype=wp.vec2));initial_history=solver.history.numpy();initial_energy=energy(x,velocity,initial_history)
  for color in range(len(data['colors'])):solver._gather_blocks(color,sin,DT)
  wp.synchronize();previous_force=solver.particle_forces.numpy().astype(float);previous_fixed=x[fixed].astype(float);work=0.;support_impulse=np.zeros(3)
  for i in range(8):
   if (out/'stop.request').exists():raise InterruptedError('Stopped between loading intervals')
   opening=.00095+(i+1)*.00005;positions=sin.particle_q.numpy();positions[fixed]=original[fixed];positions[fixed,0]+=np.where(right[fixed],opening/2,-opening/2);sin.particle_q.assign(wp.array(positions,dtype=wp.vec3));old=solver.history.numpy().copy();solver.invalid.zero_();solver.volume_invalid.zero_();solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1;x=sout.particle_q.numpy();v=sout.particle_qd.numpy();expected=expected_history(x,old);solver.commit_cohesion(sout);wp.synchronize();actual=solver.history.numpy();qerror=float(np.max(abs(actual[:,0]-expected[:,0])));derror=float(np.max(abs(actual[:,1]-expected[:,1])))
   for color in range(len(data['colors'])):solver._gather_blocks(color,sout,DT)
   wp.synchronize();forces=solver.particle_forces.numpy().astype(float);current_fixed=x[fixed].astype(float);increment=-.5*np.sum((forces[fixed]+previous_force[fixed])*(current_fixed-previous_fixed));work+=float(increment);support_impulse-=DT*forces[fixed].sum(axis=0);me=float(np.linalg.norm((mass[:,None]*v).sum(axis=0)-support_impulse));e=energy(x,v,actual);gain=e['total_j']-initial_energy['total_j']-work;ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
   record=dict(interval=i,controlled_opening_m=opening,max_history_error_m=qerror,max_damage_error=derror,min_damage=float(min(actual[:,1])),max_damage=float(max(actual[:,1])),patches_increased=int(sum(actual[:,1]>old[:,1])),energy=e,cumulative_driver_work_j=work,energy_gain_above_driver_work_j=gain,support_impulse_error_ns=me,min_volume_ratio=float(min(ratios)));records.append(record);write(out,'full_damage_partial.json',dict(initial_energy=initial_energy,records=records))
   if qerror>1e-7 or derror>1e-6 or np.any(actual<old):raise ValueError('Actual loaded patch history differs from independent law')
   if gain>.01*max(abs(initial_energy['total_j']),abs(e['total_j']),abs(work),1e-12)+1e-12:raise ValueError('Actual controlled loading creates excess energy')
   if me>2e-7 or min(ratios)<=.1 or not np.isfinite(x).all():raise ValueError(f'Actual loading mechanical gate {me=}')
   previous_force=forces;previous_fixed=current_fixed;sin,sout=sout,sin
  final=solver.history.numpy();increased=int(sum(final[:,1]>initial_history[:,1]))
  if increased!=47 or steps!=8:raise ValueError('All actual patches must exercise damage evolution')
  write(out,'full_damage_measurements.json',dict(records=records,initial_energy=initial_energy,initial_history=initial_history.tolist(),final_history=final.tolist(),patches_increased=increased,newton_steps=steps,nodes=model.particle_count,patches=47,controlled_surface_nodes=len(fixed),free_bulk_nodes=int(sum(mass>0)),dt_s=DT,volume_trial_clips=int(solver.volume_clip_count.numpy()[0]),scope='Actual full mesh in a disclosed displacement-controlled tensile fixture: paired interface nodes prescribed, other bulk nodes retain actual masses and evolve natively. Explicit all-patch eligibility. No knife eligibility detector, free-fragment reclosure, rotating-frame or experimental material qualification.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,full_damage_passed=passed,newton_steps=steps,controlled_steps=steps,full_damage_intervals=len(records)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
