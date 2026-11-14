"""Full-model gravity/plane-contact duration challenge, with CUDA graph profiling."""
import argparse,hashlib,json,signal,time,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--step-audit',action='store_true');p.add_argument('--checked-bounds',action='store_true');args=p.parse_args();out=args.output
 app=None;passed=False;steps=0;episodes=[]
 def stop(*args):raise InterruptedError('Sustained support diagnostic stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  cp=ROOT/'runs/offline/integration_contract_20261102_01/contract.json';config=json.loads(cp.read_text())['sustained_support'];dt=config['dt_s'];duration=config['minimum_duration_s'];n=int(round(duration/dt));assert n%100==0
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp,newton
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_board_support import BoardSupportVBD,AuditedBoardSupportVBD,DiagnosedBoardSupportVBD,ReplayDiagnosedBoardSupportVBD,CheckedBoardSupportVBD,nodal_plane_stiffness
  wp.init();wp.set_device('cuda:0');data=registry();data['x']=data['x']+np.array([0.,0.,.002]);fixed=np.asarray(data['design']['fixture']['node_ids']);model=build_model(data,fixed_nodes=fixed);model.set_gravity((0.,0.,-9.81))
  solver=configure_solver(model,data,iterations=32,solver_class=CheckedBoardSupportVBD if args.checked_bounds else ReplayDiagnosedBoardSupportVBD if args.step_audit else BoardSupportVBD);k=nodal_plane_stiffness(data);solver.board_stiffness=wp.array(k,dtype=float);solver.board_height=0.
  solver.volumes64=wp.array(data['volumes'],dtype=wp.float64);solver.candidate_active=wp.zeros(1,dtype=int);solver.candidate_bad=wp.zeros(1,dtype=int)
  solver.minimum_trial_ratio=wp.ones(1,dtype=float);solver.bad_info=wp.zeros(3,dtype=int);solver.bad_snapshot=wp.zeros(4,dtype=wp.vec3);solver.before_color=wp.zeros(model.particle_count,dtype=wp.vec3);solver.before_displacements=wp.zeros(model.particle_count,dtype=wp.vec3)
  colors=model.particle_colors.numpy()
  if any(len(set(colors[t]))!=4 for t in data['cells']):raise ValueError('Volume clique coloring failed')
  states=[model.state(),model.state()];rest=model.particle_q.numpy().copy()
  sources=[Path(__file__),cp,ROOT/'rl/tomato_board_support.py',ROOT/'rl/tomato_native_full_model.py',ROOT/'rl/tomato_native_full_gather.py',ROOT/'rl/tomato_native_volume_steps.py',ROOT/'rl/tomato_native_group_cohesion.py',ROOT/'rl/tomato_checked_volume_steps.py']
  write(out,'input_manifest.json',dict(source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},config=config,solver_iterations=32,contact='unilateral area-lumped node/plane potential, no friction or damping; board takes weight only when contacted',self_contact=False))
  # Independent contact-law check against exact plane potential derivatives.
  from tomato_board_support import plane_blocks
  test=rest.copy();bottom=int(np.argmin(test[:,2]));test[bottom,2]=-.00005
  x=wp.array(test,dtype=wp.vec3);f=wp.zeros(len(rest),dtype=wp.vec3);h=wp.zeros(len(rest),dtype=wp.mat33)
  for color in range(len(data['colors'])):wp.launch(plane_blocks,dim=len(rest),inputs=[color,model.particle_colors,x,solver.board_stiffness,0.],outputs=[f,h])
  fn=f.numpy();hn=h.numpy();expected=np.maximum(-test[:,2],0)*k
  error=float(np.max(np.abs(fn[:,2]-expected)));herr=float(np.max(np.abs(hn[bottom,2,2]-k[bottom])))
  if error>1e-5 or herr>1e-2 or expected[bottom]<=0:raise ValueError('Board force/potential positive control mismatch')
  write(out,'board_positive_control.json',dict(force_error_n=error,stiffness_error_n_m=herr,positive_force_n=float(fn[bottom,2]),node=bottom))
  def reset():
   for s in states:solver.reset(s,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD);s.particle_q.assign(rest);s.particle_qd.zero_();s.clear_forces()
   solver.particle_q_prev.assign(rest);solver.history.zero_();solver.eligible.zero_();solver.invalid.zero_();solver.volume_invalid.zero_();solver.volume_step_fraction.fill_(1.);solver.volume_clip_count.zero_()
  reset();start=time.monotonic()
  solver.step(states[0],states[1],None,None,dt);solver.step(states[1],states[0],None,None,dt);wp.synchronize();steps+=2
  warm_wall=time.monotonic()-start;reset()
  with wp.ScopedCapture() as capture:
   solver.step(states[0],states[1],None,None,dt);solver.step(states[1],states[0],None,None,dt)
  write(out,'profile.json',dict(warm_two_steps_wall_s=warm_wall,graph_captured=True))
  for episode in range(2):
   reset();trace=[];start=time.monotonic()
   for batch in range(n if args.step_audit else n//100):
    if (out/'stop.request').exists():raise InterruptedError('Guard stop during support batch')
    if args.step_audit:
     solver.step(states[batch%2],states[1-batch%2],None,None,dt)
    else:
     for _ in range(50):wp.capture_launch(capture.graph)
    increment=1 if args.step_audit else 100
    wp.synchronize();steps+=increment;current=states[1-batch%2] if args.step_audit else states[0];x=current.particle_q.numpy().astype(float);v=current.particle_qd.numpy().astype(float)
    ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);penetration=float(max(0.,-x[:,2].min()));speed=float(np.linalg.norm(v,axis=1).max());fixture_error=float(np.max(np.abs(x[fixed]-rest[fixed])));board_force=float(np.sum(k*np.maximum(-x[:,2],0.)))
    if int(solver.bad_info.numpy()[0]):np.savez(out/'first_bad_update.npz',before=solver.before_color.numpy(),displacement=solver.before_displacements.numpy(),baseline=solver.pos_prev_collision_detection.numpy(),colors=colors,cells=data['cells'],volumes=data['volumes'],bad_info=solver.bad_info.numpy(),bad_snapshot=solver.bad_snapshot.numpy())
    row=dict(bad_info=solver.bad_info.numpy().tolist(),bad_snapshot=solver.bad_snapshot.numpy().tolist(),minimum_gather_ratio=float(solver.minimum_trial_ratio.numpy()[0]),volume_invalid_trials=int(solver.volume_invalid.numpy()[0]),time_s=(batch+1)*(1 if args.step_audit else 100)*dt,minimum_volume_ratio=float(ratios.min()),maximum_speed_m_s=speed,maximum_board_penetration_m=penetration,fixture_error_m=fixture_error,board_reaction_n=board_force,kinetic_energy_j=float(np.sum(.5*data['mass']*np.sum(v*v,axis=1))),maximum_displacement_m=float(np.linalg.norm(x-rest,axis=1).max()))
    trace.append(row);write(out,'support_partial.json',dict(episodes=episodes,current_episode=episode,trace=trace,newton_steps=steps,elapsed_wall_s=time.monotonic()-start))
    if int(solver.volume_invalid.numpy()[0]) or ratios.min()<=.1 or not np.isfinite(x).all() or fixture_error!=0 or penetration>config['board_max_penetration_m']:raise ValueError('Sustained target exceeded predeclared support/volume/board gate: '+str(row))
   tail=[r for r in trace if r['time_s']>duration-config['settling_window_s']];settled=max(r['maximum_speed_m_s'] for r in tail)<config['settling_speed_m_s']
   episodes.append(dict(trace=trace,elapsed_wall_s=time.monotonic()-start,settled=settled,final_x_sha256=hashlib.sha256(states[0].particle_q.numpy().tobytes()).hexdigest(),final_v_sha256=hashlib.sha256(states[0].particle_qd.numpy().tobytes()).hexdigest()))
   np.savez(out/f'support_final_{episode}.npz',x=x,v=v)
   if not settled:raise ValueError('Target did not settle within fixed final-window speed criterion')
  replay=episodes[0]['final_x_sha256']==episodes[1]['final_x_sha256'] and episodes[0]['final_v_sha256']==episodes[1]['final_v_sha256']
  if not replay:raise ValueError('Sustained support replay differs')
  write(out,'support_measurements.json',dict(episodes=episodes,newton_steps=steps,duration_per_episode_s=duration,exact_replay=replay,scope='Full saved model with fixed fixture, gravity and frictionless nodal board contact. No robot contact, self-contact, cutting-load or fracture qualification.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,sustained_support_passed=passed,newton_steps=steps,controlled_steps=0,episodes_completed=len(episodes)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
