"""Synchronized actual parked robot and qualified prestressed intact target hold.

Constitutive rest geometry is built from the ORIGINAL source before assigning
the prepared pose to state only. This is not the old floating-target drop.
"""
import argparse,gzip,json,signal,time,traceback,faulthandler
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 faulthandler.enable()
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);phase=p.add_mutually_exclusive_group();phase.add_argument('--preview',action='store_true');phase.add_argument('--screen',action='store_true');p.add_argument('--preparation',type=Path,default=ROOT/'runs/native/static_preparation_cached_20261102_01');p.add_argument('--refinement',type=int,choices=[1,2,4,8,16,32,64],default=1);args=p.parse_args();out=args.output;preview=args.preview;screen=args.screen;app=None;parked=None;passed=False;steps=0;episodes=[];robot_reference=[];robot_replay_q=0.;robot_replay_qd=0.;robot_replay_pose=0.
 def stop(*a):raise InterruptedError('Global duration diagnostic stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  prep=args.preparation.resolve();parent=json.loads((prep/'supervisor_result.json').read_text());parent_closure=json.loads((prep/'source_closure.json').read_text());prepared=prep/'prepared_equilibrium.npz'
  if parent.get('passed') is not True or parent.get('worker',{}).get('load_stages_completed')!=6 or not prepared.is_file():raise ValueError('Prepared hold requires qualified six-stage parent equilibrium, not debug optimizer output')
  if not sources_unchanged(parent_closure['source_sha256']):raise ValueError('Parent equilibrium source/input closure changed')
  plan_path=ROOT/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json';plan=json.loads(plan_path.read_text());plan_sources=[Path(x)for x in plan['source_sha256']]
  if not sources_unchanged(plan['source_sha256']):raise ValueError('Frozen fixed-mount scene sources changed')
  contracts=[ROOT/'work/integration_20261102/support_ledger_contract.json',ROOT/'work/integration_20261102/local_residual_contract.json',ROOT/'runs/offline/integration_contract_20261102_08/contract.json',ROOT/'runs/offline/integration_contract_20261102_20/contract.json'];pins=capture_sources(out,[Path(__file__)],inputs=contracts+[plan_path,Path(plan['scene'])]+plan_sources+[prepared,prep/'supervisor_result.json',prep/'static_preparation_measurements.json',prep/'source_closure.json'])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_parked_robot import ParkedRobot
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_board_support import nodal_plane_stiffness
  from tomato_failed_safe_global import FailedSafeFractionCandidate as GlobalImplicitCandidate
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_failed_safe_ledger import FailedSafeLocalLedger as LocalFrameSupportLedger
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');world_data=registry();world_data['x']+=[0,0,.002];origin=np.array([world_data['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world_data,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world_data);refinement=args.refinement;dt=1/(2400*refinement);n=(24 if screen else 600 if preview else 24000)*refinement;duration=n*dt;episode_count=1 if preview else 2;g=json.loads(contracts[0].read_text());local=json.loads(contracts[1].read_text());model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(holder,world_data,source_rest);e=holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;s=GlobalImplicitCandidate(holder,data,fixed,maximum_outer=256,velocity_defect_budget_m_s=1e-6);states=[s.state(),s.state()]
  z=np.load(prepared);initial_pose=z['x_sim'].copy()
  if initial_pose.shape!=data['x'].shape or not np.isfinite(initial_pose).all() or not np.array_equal(z['reference_world'],world_data['x']) or not np.array_equal(z['fixture'],fixed) or not np.array_equal(z['world_from_sim_translation_m'],origin) or not np.array_equal(z['x'],initial_pose+origin) or not np.array_equal(initial_pose[fixed],data['x'][fixed]) or np.any(z['v']) or np.any(z['history']) or np.any(z['mirror']) or np.any(z['eligible']):raise ValueError('Prepared initial state/rest/fixture/history provenance failed')
  from tomato_static_gravity import StaticGravityCandidate
  probe=StaticGravityCandidate(holder,data,fixed,regularizer_s=.02);probe.set_load(1.);fresh_residual=probe.force(wp.array(initial_pose,dtype=wp.vec3d),.02);fresh_acceleration=float(probe.maximum_acceleration_defect.numpy()[0]);initial_ratios=np.linalg.det(initial_pose[data['cells'][:,1:]]-initial_pose[data['cells'][:,:1]])/(6*data['volumes'])
  if fresh_residual>1e-6 or fresh_acceleration>1e-5 or initial_ratios.min()<=.1 or np.linalg.norm(initial_pose-data['x'],axis=1).max()>.02 or -(initial_pose[:,2]+origin[2]).min()>.0001:raise ValueError('Fresh prepared-state force/acceleration/geometry gate failed before physical stepping')
  write(out,'prepared_state_provenance.json',dict(parent=str(prep),fresh_original_force_l1_n=fresh_residual,fresh_maximum_force_acceleration_m_s2=fresh_acceleration,initial_minimum_volume_ratio=float(initial_ratios.min()),physical_time_used_by_preparation_s=0.,constitutive_rest_source='original source, before prepared state assignment',prepared_pose_is_new_initial_condition=True,original_floating_drop_qualified=False))
  ledger=LocalFrameSupportLedger(s,data,fixed,k,origin);write(out,'input_manifest.json',dict(duration_s=duration,dt_s=dt,world_from_sim_translation_m=origin.tolist(),world_board_height_m=0.,simulation_board_height_m=-origin[2],episodes=episode_count,deformable_steps=episode_count*n,refinement=refinement,preview=preview,screen=screen,native_vbd_steps=0,controlled_steps=episode_count*n+3,robot_setup_steps=3,backend='Failed-safe translated-frame float64 coupled Fraction-to-volume-boundary positive tensile-curvature block-Jacobi GN-preconditioned L-BFGS/PCG candidate using unchanged source forces, Newton registry and complete collision backend',lbfgs_memory_pairs=8,positive_curvature_relative_threshold=1e-10,maximum_outer_iterations=256,maximum_cg_iterations=1000,cg_relative_tolerance=1e-9,cg_absolute_tolerance=1e-16,solver_declared_duration_s=.1,solver_total_velocity_defect_budget_m_s=1e-6,board_penetration_budget_m=.0001,maximum_displacement_m=.02,replay_position_budget_m=1e-10,replay_velocity_budget_m_s=1e-8,global_contract=g,local_contract=local,scope='NEW PRESTRESSED INITIAL CONDITION. Actual parked robot and deformable target at the same episode dt and number of steps. Separate three-step rigid-monitor setup. No blade contact or feedback in these clear episodes. Streamed 10 ms accuracy/replay screen, quarter-second preview or ten-second undamaged support hold; no actual robot work, load challenge, fracture or cut claim. Preview has one episode and makes no replay/settling qualification. Full hold requires two episodes and final one-second maximum speed <=1 mm/s. Original fixed remainder fixture and free cap.'))
  parked=ParkedRobot(out,plan,dt);write(out,'rigid_monitor_positive_control.json',parked.positive_control());write(out,'engine_device_boundary.json',dict(default_after_physx_setup=str(wp.get_device()),target_device=str(states[0].particle_q.device),physics_robot_device='cpu',target_device_selected_explicitly='cuda:0',sdk_cause='SimulationContext sets global wp device to cfg.device'));wp.set_device('cuda:0')
  finals=[]
  for episode in range(episode_count):
   parked.reset();wp.set_device('cuda:0')
   for state in states:
    s.reset(state);state.particle_q.assign(initial_pose)
    if not np.array_equal(state.particle_q.numpy(),initial_pose) or np.any(state.particle_qd.numpy()) or np.any(holder.objective_history.numpy()) or np.any(holder.history.numpy()) or np.any(holder.eligible.numpy()):raise ValueError('Prepared initial-state reset failed')
   e.reference=states[0].particle_q;e.invalid.zero_();e.detect(s.zero);e.evaluate(s.zero,dt)
   ledger.reset();initial=ledger.measurements(states[0])['energy']['total_j'];start=time.monotonic();summary=dict(initial_energy_j=initial,steps=0,minimum_volume_ratio=1.,maximum_speed_m_s=0.,maximum_displacement_m=0.,maximum_board_penetration_m=0.,maximum_energy_increase_j=0.,maximum_linear_impulse_residual_ns=0.,maximum_angular_impulse_residual_nms=0.,maximum_cumulative_nodal_impulse_residual_ns=0.,final_one_second_maximum_speed_m_s=None if preview or screen else 0.,nonlinear_residual_evaluations=0,logged_cg_iterations=0)
   with gzip.open(out/f'episode{episode}_audit.jsonl.gz','wt',compresslevel=1) as stream:
    for i in range(n):
     if (out/'stop.request').exists():raise InterruptedError('Hold checkpoint stop')
     try:s.step(states[i%2],states[1-i%2],None,None,dt)
     except BaseException:
      np.savez(out/'nonlinear_failure_state.npz',x_sim=s.x.numpy(),target_sim=s.target.numpy(),previous_sim=s.previous.numpy(),force=s.rhs.numpy(),matrix_values=s.assembly.matrix.values.numpy(),matrix_columns=s.assembly.matrix.columns.numpy(),matrix_offsets=s.assembly.matrix.offsets.numpy(),world_from_sim_translation_m=origin,dt=np.array([dt]))
      write(out,'nonlinear_failure_trace.json',dict(episode=episode,step=i,iterations=s.last_trace));raise
     state=states[1-i%2];steps+=1;x=state.particle_q.numpy();v=state.particle_qd.numpy()
     try:robot_row=parked.step(x+origin)
     except BaseException:
      np.savez(out/'synchronized_robot_failure_target.npz',x_sim=x,v=v,world_from_sim_translation_m=origin,episode=episode,step=i);raise
     wp.set_device('cuda:0')
     if robot_row['episode_physx_steps']!=i+1 or parked.steps!=steps:raise ValueError('Robot and target episode clocks diverged')
     actual_robot=np.r_[robot_row['q'],robot_row['qd'],robot_row['tool_pose']]
     if episode==0:robot_reference.append(actual_robot)
     else:
      delta=abs(actual_robot-robot_reference[i]);robot_replay_q=max(robot_replay_q,float(delta[:36].max()));robot_replay_qd=max(robot_replay_qd,float(delta[36:72].max()));robot_replay_pose=max(robot_replay_pose,float(delta[72:].max()))
      if robot_replay_q>1e-5 or robot_replay_qd>2e-5 or robot_replay_pose>2e-6:raise ValueError('Actual parked robot reset/replay gate failed')
     ledger.step(state,dt);ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);audit=ledger.measurements(state);audit.update(time_s=(i+1)*dt,matched_robot_time_s=robot_row['episode_physx_steps']*dt,parked_robot=robot_row,minimum_volume_ratio=float(ratios.min()),energy_increase_j=audit['energy']['total_j']-initial,board_penetration_m=float(max(0.,-(x[:,2]+origin[2]).min())),maximum_displacement_m=float(np.linalg.norm(x-data['x'],axis=1).max()),displacement_from_prepared_initial_m=float(np.linalg.norm(x-initial_pose,axis=1).max()),maximum_speed_m_s=float(np.linalg.norm(v,axis=1).max()),nonlinear_trace=s.last_trace)
     invalid=(not np.isfinite(x).all() or not np.isfinite(v).all() or ratios.min()<=.1 or holder.history.numpy().max() or holder.eligible.numpy().max() or not np.array_equal(x[fixed],data['x'][fixed]) or e.invalid.numpy()[0] or holder.volume_invalid.numpy()[0]);budget=(audit['linear_impulse_residual_ns']>g['linear_impulse_error_ns'] or audit['angular_impulse_residual_nms']>g['angular_impulse_error_nms'] or audit['energy_increase_j']>g['maximum_energy_increase_above_initial_j'] or audit['cumulative_absolute_nodal_impulse_residual_ns']>local['cumulative_absolute_nodal_impulse_residual_ns'] or audit['board_penetration_m']>.0001 or audit['maximum_displacement_m']>.02)
     stream.write(json.dumps(audit,separators=(',',':'))+'\n');summary['steps']=i+1;summary['minimum_volume_ratio']=min(summary['minimum_volume_ratio'],audit['minimum_volume_ratio']);summary['nonlinear_residual_evaluations']+=len(s.last_trace);summary['logged_cg_iterations']+=sum(row.get('cg_iterations',0)for row in s.last_trace)
     for key,value in [('maximum_speed_m_s',audit['maximum_speed_m_s']),('maximum_displacement_m',audit['maximum_displacement_m']),('maximum_board_penetration_m',audit['board_penetration_m']),('maximum_energy_increase_j',audit['energy_increase_j']),('maximum_linear_impulse_residual_ns',audit['linear_impulse_residual_ns']),('maximum_angular_impulse_residual_nms',audit['angular_impulse_residual_nms']),('maximum_cumulative_nodal_impulse_residual_ns',audit['cumulative_absolute_nodal_impulse_residual_ns'])]:summary[key]=max(summary[key],value)
     if not preview and not screen and i>=n-round(1/dt):summary['final_one_second_maximum_speed_m_s']=max(summary['final_one_second_maximum_speed_m_s'],audit['maximum_speed_m_s'])
     if invalid or budget:
      np.savez(out/'first_bad_state.npz',x=x+origin,x_sim=x,v=v,world_from_sim_translation_m=origin,previous_velocity=states[i%2].particle_qd.numpy(),reference_sim=data['x'],mass=data['mass'],fixture=fixed,cells=data['cells'],dt=np.array([dt]));write(out,'hold_failure.json',dict(audit=audit,invalid=bool(invalid),budget_exceeded=bool(budget)));raise ValueError('Hold exceeded an unchanged numerical/geometry gate')
     if i%24==0 or i==n-1:
      stream.flush();write(out,'hold_partial.json',dict(episodes=episodes,episode=episode,summary=summary,deformable_steps=steps,accepted_time_s=(i+1)*dt))
   summary['wall_s']=time.monotonic()-start
   if not preview and not screen and summary['final_one_second_maximum_speed_m_s']>.001:write(out,'settling_failure.json',summary);raise ValueError('Original final one-second settling-speed gate failed')
   finals.append((x.copy(),v.copy()));episodes.append(summary);np.savez(out/f'episode{episode}_final.npz',x=x+origin,x_sim=x,v=v,world_from_sim_translation_m=origin)
  pe=None;ve=None
  if not preview:
   pe=float(abs(finals[0][0]-finals[1][0]).max());ve=float(abs(finals[0][1]-finals[1][1]).max());write(out,'hold_replay_audit.json',dict(position_error_m=pe,velocity_error_m_s=ve,position_budget_m=1e-10,velocity_budget_m_s=1e-8))
   if pe>1e-10 or ve>1e-8:raise ValueError('Hold strict reset/replay failed')
  if steps!=episode_count*n or parked.steps!=steps or parked.setup_steps!=3 or not sources_unchanged(pins):raise ValueError('Hold step count/source gate failed')
  write(out,'parked_robot_replay_audit.json',dict(maximum_joint_error_rad=robot_replay_q,maximum_joint_velocity_error_rad_s=robot_replay_qd,maximum_tool_pose_component_error=robot_replay_pose,setup_physx_steps=parked.setup_steps,matched_physx_steps=parked.steps,matched_deformable_steps=steps,scope='Actual parked robot and prepared target synchronized unloaded support only; no loaded contact or cutting reset.'))
  write(out,'hold_measurements.json',dict(episodes=episodes,duration_s=duration,refinement=refinement,preview=preview,screen=screen,deformable_steps=steps,replay_position_error_m=pe,replay_velocity_error_m_s=ve,scope='NEW PRESTRESSED INITIAL CONDITION. Actual parked-robot and target synchronized unloaded screen/support hold only; 10 ms screen makes no sustained-settling claim; preview is one quarter-second episode and makes no sustained-settling/replay claim. No bounded-load, actual mounted whole-target work, coupled fracture, loaded cutting reset or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,prepared_scene_preview_passed=passed if preview else False,prepared_scene_sustained_passed=passed if not preview and not screen else False,prepared_scene_screen_passed=passed if screen else False,refinement=args.refinement,duration_s=.01 if screen else .25 if preview else 10.,newton_steps=0,deformable_steps=steps,controlled_steps=0 if parked is None else parked.steps+parked.setup_steps,matched_physx_steps=0 if parked is None else parked.steps,setup_physx_steps=0 if parked is None else parked.setup_steps,episodes_completed=len(episodes)))
  if parked is not None:parked.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
