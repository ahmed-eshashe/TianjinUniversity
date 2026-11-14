"""Short whole-fruit contact/motion qualification before long support runs."""
import argparse,hashlib,json,signal,time,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--steps',type=int,default=24);p.add_argument('--objective',action='store_true');p.add_argument('--iterations',type=int,default=16);args=p.parse_args();out=args.output;app=None;passed=False;steps=0;episodes=[]
 def stop(*a):raise InterruptedError('Contact motion diagnostic stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp,newton
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_board_support import nodal_plane_stiffness
  from tomato_objective_full_model import configure_objective
  from tomato_contact_full_model import ContactObjectiveTomatoVBD,ContactFixedFrameTomatoVBD
  from tomato_mollified_self_contact import MollifiedEmbeddedSelfContact
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=np.array([0.,0.,.002]);fixed=np.asarray(data['design']['fixture']['node_ids']);model=build_model(data,fixed_nodes=fixed);model.set_gravity((0.,0.,-9.81))
  solver=configure_solver(model,data,iterations=args.iterations,solver_class=ContactObjectiveTomatoVBD if args.objective else ContactFixedFrameTomatoVBD);k=nodal_plane_stiffness(data)
  configure_objective(solver,data,board_stiffness=k) # also allocates shared checked-volume buffers
  engine=solver.surface_contact=MollifiedEmbeddedSelfContact(data,margin=.0001)
  states=[model.state(),model.state()];rest=model.particle_q.numpy().copy();dt=1/2400
  files=[Path(__file__)]+[ROOT/'rl'/name for name in ['tomato_contact_full_model.py','tomato_mollified_self_contact.py','tomato_embedded_self_contact.py','tomato_collision_embedding.py','tomato_collision_local_filters.py','tomato_canonical_self_contact.py','tomato_objective_full_model.py','tomato_native_objective_reference.py','tomato_board_support.py','tomato_checked_volume_steps.py']];pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};snapshot=out/'source_snapshot';snapshot.mkdir(exist_ok=True,parents=True)
  for p in files:(snapshot/p.name).write_bytes(p.read_bytes())
  write(out,'input_manifest.json',dict(source_sha256=pins,dt_s=dt,steps_per_episode=args.steps,iterations=args.iterations,objective_material=args.objective,contact_margin_m=engine.margin,collision_self_contact_enabled=engine.solver.particle_enable_self_contact,mechanical_self_contact_delegated_to_collision_model=True,scope='Gravity and initially closed surface, no blade or fracture. Numerical component diagnostic.'))
  def reset():
   for state in states:solver.reset(state,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD);state.particle_q.assign(rest);state.particle_qd.zero_();state.clear_forces()
   solver.particle_q_prev.assign(rest);solver.reset_material();engine.invalid.zero_()
  for episode in range(2):
   reset();trace=[]
   for i in range(args.steps):
    if (out/'stop.request').exists():raise InterruptedError('Guard stop during contact motion')
    start=time.monotonic();sin,sout=states[i%2],states[1-i%2];solver.step(sin,sout,None,None,dt);wp.synchronize();steps+=1;solver.commit_cohesion(sout);x=sout.particle_q.numpy().astype(float);v=sout.particle_qd.numpy().astype(float);ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);force=engine.physical_force.numpy();row=dict(step=i+1,wall_s=time.monotonic()-start,minimum_volume_ratio=float(ratios.min()),maximum_speed_m_s=float(np.linalg.norm(v,axis=1).max()),board_penetration_m=float(max(0.,-x[:,2].min())),maximum_displacement_m=float(np.linalg.norm(x-rest,axis=1).max()),maximum_damage=float(solver.history.numpy()[:,1].max()),fixture_error_m=float(np.max(abs(x[fixed]-rest[fixed]))),contact_candidates=int(engine.stencil_count.numpy()[0]),contact_invalid=int(engine.invalid.numpy()[0]),contact_energy_j=float(engine.contact_energy.numpy()[0]),contact_peak_n=float(np.linalg.norm(force,axis=1).max()))
    trace.append(row);write(out,'contact_dynamics_partial.json',dict(episodes=episodes,current_episode=episode,trace=trace,newton_steps=steps))
    if not np.isfinite(x).all() or ratios.min()<=.1 or row['board_penetration_m']>.0001 or row['fixture_error_m']!=0 or row['contact_invalid'] or row['maximum_damage']!=0:raise ValueError('Prefracture contact dynamic gate failed '+str(row))
   np.savez(out/f'final_{episode}.npz',x=x,v=v);episodes.append(dict(trace=trace))
  a=np.load(out/'final_0.npz');b=np.load(out/'final_1.npz');pe=float(abs(a['x']-b['x']).max());ve=float(abs(a['v']-b['v']).max())
  if pe>1e-7 or ve>2e-5:raise ValueError('Contact loaded replay failed')
  write(out,'contact_dynamics_measurements.json',dict(episodes=episodes,position_replay_error_m=pe,velocity_replay_error_m_s=ve,newton_steps=steps,source_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items()),scope='Initially closed full surface under short gravity loading. No sustained support, blade coupling or fracture qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,contact_dynamics_passed=passed,newton_steps=steps,controlled_steps=0,episodes_completed=len(episodes),steps_per_episode=args.steps,objective_material=args.objective))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
