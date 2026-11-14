"""Live clear end-to-end regression through the new accepted-force handoff; no loaded contact."""
import argparse,json,signal,time,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=parked=None;passed=False;target_steps=0;rows=[];robot_rows=[]
 def stop(*_):raise InterruptedError('Owned live-clear assembly stop')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  prep=ROOT/'runs/native/static_preparation_cached_20261102_01';hold=ROOT/'runs/native/prepared_scene_device_hold_20261102_01';near=ROOT/'runs/native/near_approach_20261102_01';plan_path=ROOT/'runs/offline/near_approach_plan_20261102_02/near_approach_plan.json';contract=ROOT/'work/nonfracturing_contact_plan_20261102/contact_test_contract.json';support_contract=ROOT/'work/integration_20261102/support_ledger_contract.json';local_contract=ROOT/'work/integration_20261102/local_residual_contract.json'
  for base,flag in [(prep,'diagnostic_passed'),(hold,'prepared_scene_device_sustained_passed'),(near,'near_approach_passed')]:
   result=json.loads((base/'supervisor_result.json').read_text())
   if not result['passed']or not result['worker'].get(flag):raise ValueError('Missing parent qualification: '+str(base))
  for base in [prep,hold]:
   closure=json.loads((base/'source_closure.json').read_text())['source_sha256']
   if not sources_unchanged(closure):raise ValueError('Parent frozen source changed')
  original_plan=json.loads(plan_path.read_text());plan=dict(original_plan);plan['home_rad']=dict(original_plan['home_rad']);plan['home_rad'].update(dict(zip(plan['right_joint_names'],plan['right_joint_route_rad'][240])))
  pins=capture_sources(out,[Path(__file__)],inputs=[plan_path,Path(plan['scene']),contract,support_contract,local_contract,prep/'prepared_equilibrium.npz',prep/'supervisor_result.json',hold/'supervisor_result.json',near/'supervisor_result.json',ROOT/'work/near_approach_20261102/independent_readback01/measurements.json']+[Path(x)for x in plan['source_sha256']])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=False,device='cpu',visualizer=['kit']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from pxr import UsdGeom,UsdPhysics,UsdLux,Gf,Vt
  from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
  from tomato_parked_robot import ParkedRobot
  from tomato_corrected_contact_exchange import AcceptedContactExchange,CorrectedRobotContactQueue
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_board_support import nodal_plane_stiffness
  from tomato_failed_safe_global import FailedSafeFractionCandidate
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_failed_safe_ledger import FailedSafeLocalLedger
  from tomato_static_gravity import StaticGravityCandidate
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world);model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(holder,world,source_rest);e=holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;solver=FailedSafeFractionCandidate(holder,data,fixed,maximum_outer=256,velocity_defect_budget_m_s=1e-6);states=[solver.state(),solver.state()];z=np.load(prep/'prepared_equilibrium.npz');initial=z['x_sim'].copy();target_dt=1/2400;robot_dt=1/240
  if not np.array_equal(z['reference_world'],world['x'])or not np.array_equal(z['fixture'],fixed)or not np.array_equal(z['world_from_sim_translation_m'],origin)or not np.array_equal(z['x'],initial+origin)or np.any(z['v'])or np.any(z['history'])or np.any(z['eligible']):raise ValueError('Prepared/rest/history provenance')
  for state in states:solver.reset(state);state.particle_q.assign(initial)
  e.reference=states[0].particle_q;e.detect(solver.zero);e.evaluate(solver.zero,target_dt);probe=StaticGravityCandidate(holder,data,fixed,regularizer_s=.02);probe.set_load(1.);fresh=probe.force(wp.array(initial,dtype=wp.vec3d),.02)
  if fresh>1e-6 or probe.maximum_acceleration_defect.numpy()[0]>1e-5:raise ValueError('Fresh supported equilibrium failed')
  ledger=FailedSafeLocalLedger(solver,data,fixed,k,origin);ledger.reset();initial_energy=ledger.measurements(states[0])['energy']['total_j'];g=json.loads(support_contract.read_text());local=json.loads(local_contract.read_text())
  parked=ParkedRobot(out,plan,robot_dt);r=parked.robot;sim=parked.sim;queue_binding=CorrectedRobotContactQueue(r,parked.tool);exchange_records=[];write(out,'rigid_monitor_positive_control.json',parked.positive_control());wp.set_device('cuda:0')
  old=sim.stage.GetPrimAtPath('/CuttingTargetVisual')
  if not old:raise ValueError('Expected original visual missing')
  old.SetActive(False)
  triangles=np.array([tri for piece in data['design']['pieces']for tri in piece['triangles']],dtype=np.int32);mesh=UsdGeom.Mesh.Define(sim.stage,'/LiveNewtonTomato');mesh.CreateFaceVertexCountsAttr([3]*len(triangles));mesh.CreateFaceVertexIndicesAttr(triangles.ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True);mesh.CreateDisplayColorAttr([Gf.Vec3f(.75,.05,.025)]);mesh.GetPrim().SetCustomDataByKey('simulationOwner','Newton solver particle_q; display only, no duplicate PhysX collider');mesh.GetPrim().SetCustomDataByKey('sourceNodeCount',len(initial));mesh.GetPrim().SetCustomDataByKey('scope','Supported whole-target clear hold; no blade contact or fracture')
  if mesh.GetPrim().HasAPI(UsdPhysics.CollisionAPI)or mesh.GetPrim().HasAPI(UsdPhysics.RigidBodyAPI):raise ValueError('Duplicate target collider')
  light=UsdLux.DomeLight.Define(sim.stage,'/LiveAssemblyInspectionLight');light.CreateIntensityAttr(700.);sim.set_camera_view(eye=(-.4,.65,.5),target=(.13,.12,.22));viewport=get_active_viewport();UsdGeom.Camera(sim.stage.GetPrimAtPath(viewport.camera_path)).GetClippingRangeAttr().Set(Gf.Vec2f(.01,100.))
  display_error=0.;display_trace=[];xtrace=[];vtrace=[];held_pose_trace=[]
  def display(xworld):
   nonlocal display_error
   mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(xworld.astype(np.float32)));mesh.GetExtentAttr().Set([Gf.Vec3f(*map(float,xworld.min(0))),Gf.Vec3f(*map(float,xworld.max(0)))]);actual=np.asarray(mesh.GetPointsAttr().Get(),float);error=float(abs(actual-xworld).max());display_error=max(display_error,error)
   if error>1e-7:raise ValueError('Display differs from actual Newton positions')
   return actual
  display(initial+origin)
  def capture(label):
   for _ in range(8):sim.render()
   path=out/(label+'.png');handle=capture_viewport_to_file(viewport,str(path));until=time.monotonic()+15
   while time.monotonic()<until and(not path.exists()or path.stat().st_size<1000):sim.render();time.sleep(.01)
   if not path.exists()or path.stat().st_size<1000:raise ValueError('Viewport capture failed')
  capture('00_live_initial')
  write(out,'input_manifest.json',dict(source_sha256=pins,robot_dt_s=robot_dt,target_dt_s=target_dt,target_subcycles=10,matched_duration_s=.1,target_steps=240,robot_steps=24,setup_physx_steps=3,controlled_physx_steps=27,initial_state='Explicit supported-target and robot near-stop initialization; NOT an executed live approach from home.',target_solver='Existing failed-safe float64 implicit custom solver on Newton registry;0stockVBD steps',contact='Actual full CAD/target convex-bound separation proves empty blade contact; new interval accumulator and once-only Native queue path wired between actual target steps and corrected robot step; only zero-contact branch, no loaded robot work qualification.',display_mesh='/LiveNewtonTomato',hidden_static_mesh='/CuttingTargetVisual',surface_triangles=len(triangles),target_nodes=len(initial),damage_enabled=False,training=False,video=False))
  minimum_gap=float('inf');minimumJ=float('inf');max_board=0.;max_speed=0.;stream=(out/'assembly_trace.jsonl').open('w',buffering=1)
  def cad_gap(pose,x):
   rot=Rotation.from_quat(pose[3:]).as_matrix();vertices=parked.blade@rot.T+pose[:3];return float(np.maximum(x.min(0)-vertices.max(0),vertices.min(0)-x.max(0)).max())
  for block in range(24):
   held_pose=r.data.body_link_pose_w.torch[0,parked.tool].cpu().numpy().copy()
   native_com=r.data.body_com_pose_w.torch[0,parked.tool,:3].cpu().numpy().astype(float)
   exchange=AcceptedContactExchange(block_id='clear_'+str(block),time_start_s=block*robot_dt,robot_dt_s=robot_dt,target_dt_s=target_dt,body_id=parked.tool,geometry_com_world=native_com,native_com_world=native_com)
   for sub in range(10):
    if(out/'stop.request').exists():raise InterruptedError('Owned assembly stop')
    i=block*10+sub;wp.set_device('cuda:0');solver.step(states[i%2],states[1-i%2],None,None,target_dt);target_steps+=1;state=states[1-i%2];x=state.particle_q.numpy();v=state.particle_qd.numpy();xworld=x+origin;ledger.step(state,target_dt);audit=ledger.measurements(state);ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);gap=cad_gap(held_pose,xworld);board=float(max(0.,-xworld[:,2].min()));speed=float(np.linalg.norm(v,axis=1).max());energy_increase=audit['energy']['total_j']-initial_energy
    invalid=(not np.isfinite(x).all()or not np.isfinite(v).all()or ratios.min()<=.1 or np.any(holder.history.numpy())or np.any(holder.objective_history.numpy())or np.any(holder.eligible.numpy())or not np.array_equal(x[fixed],data['x'][fixed])or e.invalid.numpy()[0]or holder.volume_invalid.numpy()[0]);budget=(audit['linear_impulse_residual_ns']>g['linear_impulse_error_ns']or audit['angular_impulse_residual_nms']>g['angular_impulse_error_nms']or audit['cumulative_absolute_nodal_impulse_residual_ns']>local['cumulative_absolute_nodal_impulse_residual_ns']or energy_increase>g['maximum_energy_increase_above_initial_j']or board>.0001 or np.linalg.norm(x-data['x'],axis=1).max()>.02 or gap<=.015)
    if invalid or budget:write(out,'first_bad_audit.json',dict(step=i,audit=audit,gap=gap,invalid=bool(invalid),budget=bool(budget)));raise ValueError('Live clear target/geometry gate')
    if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError('Unexpected nonempty tool wrench queue')
    exchange.accept(time_start_s=i*target_dt,time_end_s=(i+1)*target_dt,points_world=xworld,target_nodal_force=np.zeros_like(xworld),pressure_reaction_at_geometry_com=np.zeros(6),maximum_penetration_m=0.)
    shown=display(xworld);xtrace.append(xworld.copy());vtrace.append(v.copy());display_trace.append(shown.copy());held_pose_trace.append(held_pose.copy());row=dict(target_step=target_steps,target_time_s=target_steps*target_dt,robot_completed_time_s=block*robot_dt,held_robot_pose=held_pose.tolist(),CAD_convex_bound_gap_m=gap,generated_blade_contact_count=0,returned_tool_wrench=[0.]*6,empty_contact_proof='Strict positive AABB separation of all actual CAD vertices and all actual target nodes; complete triangle surfaces are contained in these bounds.',minimum_volume_ratio=float(ratios.min()),board_penetration_m=board,maximum_speed_m_s=speed,displacement_from_prepared_m=float(np.linalg.norm(x-initial,axis=1).max()),energy_increase_j=energy_increase,target_audit=audit,nonlinear_trace=solver.last_trace);rows.append(row);stream.write(json.dumps(row)+'\n');minimum_gap=min(minimum_gap,gap);minimumJ=min(minimumJ,float(ratios.min()));max_board=max(max_board,board);max_speed=max(max_speed,speed)
   request=exchange.finish();exchange.queue_once(queue_binding);queued_before_write=bool(r.instantaneous_wrench_composer.active)
   gravity=r.data.gravity_compensation_forces.torch.clone();arm_ids=[j for j,n in enumerate(r.joint_names)if '_AR5_'in n];effort=torch.zeros_like(parked.home);effort[:,arm_ids]=gravity[:,arm_ids];limits=r.data.joint_effort_limits.torch;effort=torch.clamp(effort,min=-limits,max=limits);r.set_joint_velocity_target_index(target=torch.zeros_like(parked.home));r.set_joint_effort_target_index(target=effort);rr=parked.step(xworld)
   if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError('Exchange queue survived its one write/step')
   exchange_records.append(dict(request=request.__dict__,target_steps_accepted=exchange.count,queued_before_write=queued_before_write,cleared_after_step=True))
   after_gap=cad_gap(np.array(rr['tool_pose']),xworld)
   if after_gap<=.015 or abs((block+1)*robot_dt-target_steps*target_dt)>1e-15:raise ValueError('Matched-clock/post-robot clearance gate')
   rr.update(robot_step=block+1,matched_target_steps=target_steps,matched_robot_time_s=(block+1)*robot_dt,matched_target_time_s=target_steps*target_dt,post_robot_CAD_gap_m=after_gap,gravity_feedforward_nm=effort.cpu().numpy()[0].tolist());robot_rows.append(rr);minimum_gap=min(minimum_gap,after_gap);sim.render();wp.set_device('cuda:0')
  write(out,'exchange_trace.json',exchange_records)
  stream.close();capture('01_live_final');np.savez_compressed(out/'live_target_trace.npz',x_world=np.array(xtrace),velocity=np.array(vtrace),display_points=np.array(display_trace),held_tool_poses=np.array(held_pose_trace),initial_x_world=initial+origin,reference_x_world=world['x'],mass=data['mass'],fixed=fixed,cells=data['cells'],volumes=data['volumes'],triangles=triangles,blade_vertices=parked.blade,origin=origin);write(out,'robot_trace.json',robot_rows)
  target_final=state.particle_q.numpy()+origin;final_display=np.array(mesh.GetPointsAttr().Get(),float);history_zero=not np.any(holder.history.numpy())and not np.any(holder.objective_history.numpy())and not np.any(holder.eligible.numpy());checks=dict(exchange_blocks_consumed_once=len(exchange_records)==24 and all(z['queued_before_write']and z['cleared_after_step']for z in exchange_records),target_stepped=target_steps==240,robot_stepped=parked.steps==24,setup_separate=parked.setup_steps==3,clocks_matched=all(abs(row['matched_robot_time_s']-row['matched_target_time_s'])<1e-15 for row in robot_rows),live_display_bound=display_error<=1e-7,old_static_hidden=not old.IsActive(),no_duplicate_target_collider=not mesh.GetPrim().HasAPI(UsdPhysics.CollisionAPI),positive_actual_CAD_separation=minimum_gap>.015,damage_history_unchanged=history_zero,fixture_fixed=np.array_equal(state.particle_q.numpy()[fixed],data['x'][fixed]),cap_unpinned=not any(data['design']['nodes'][int(i)]['side']=='slice'for i in fixed),sources_unchanged=sources_unchanged(pins),exact_physx_counter=int(sim._physics_step_count)==parked.initial_count+27)
  # Position/rotation command consistency check for this hold configuration.
  from tomato_exported_robot import ExportedRobot
  expected=ExportedRobot(ROOT/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json').knife_pose(plan['home_rad']);actual=np.array(robot_rows[-1]['tool_pose']);track=float(np.linalg.norm(actual[:3]-expected[:3,3]));checks['final_tool_tracking']=track<=.00025;checks['left_arm_hold']=max(abs(row['q'][j]-float(parked.home[0,j]))for row in robot_rows for j,n in enumerate(r.joint_names)if n.startswith('left_AR5'))<=.002
  write(out,'measurements.json',dict(checks=checks,matched_duration_s=.1,target_steps=target_steps,matched_robot_steps=parked.steps,setup_physx_steps=parked.setup_steps,controlled_physx_steps=parked.steps+parked.setup_steps,native_vbd_steps=0,minimum_CAD_axis_gap_m=minimum_gap,minimum_volume_ratio=minimumJ,maximum_board_penetration_m=max_board,maximum_target_speed_m_s=max_speed,maximum_display_coordinate_error_m=display_error,maximum_target_displacement_from_prepared_m=max(row['displacement_from_prepared_m']for row in rows),maximum_energy_increase_j=max(row['energy_increase_j']for row in rows),final_tool_position_tracking_m=track,empty_blade_contact=True,scope='Live clear regression through accepted-subcycle exchange and Native queue-consumption path. Zero forces proven by geometry. No positive physical force transfer qualification. Positive separating-axis proof of empty blade contact. No populated pressure/feedback adapter, loaded-contact/work qualification, actual approach, replay, fracture, video or training.'))
  sim.stage.GetRootLayer().Export(str(out/'live_clear_inspection_scene.usda'));sim.pause()
  if not all(checks.values()):raise ValueError(('Live assembly result checks failed',checks))
  passed=True;print('LIVE_CLEAR_ASSEMBLY_PASS',flush=True);end=time.monotonic()+20
  while app.is_running()and time.monotonic()<end and not(out/'stop.request').exists():app.update();time.sleep(.02)
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(diagnostic_passed=passed,corrected_exchange_clear_passed=passed,controlled_steps=0 if parked is None else parked.steps+parked.setup_steps,deformable_steps=target_steps,matched_physx_steps=0 if parked is None else parked.steps,setup_physx_steps=0 if parked is None else parked.setup_steps,newton_steps=0,exchange_blocks=len(exchange_records)if parked is not None else 0,shutdown_requested=app is not None,training=False))
  if parked is not None:parked.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
