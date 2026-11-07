"""One rendered, half-speed version of the verified offset dry route. No target mechanics."""
import argparse,hashlib,json,signal,time,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output
 app=None;passed=False;steps=0;rows=[]
 def stop(*_): raise InterruptedError('Owned visible dry-motion stop')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  plan_path=ROOT/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json';plan=json.loads(plan_path.read_text())
  prior=ROOT/'runs/native/fixed_mount_20261101_06/fixed_mount_measurements.json'
  if not all(json.loads(prior.read_text())['checks'].values()):raise ValueError('Prior dry-route evidence missing')
  snapshot_path=ROOT/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json'
  pins={**plan['source_sha256'],**{str(q):hashlib.sha256(q.read_bytes()).hexdigest()for q in [plan_path,Path(plan['scene']),prior,snapshot_path,Path(__file__),ROOT/'rl/tomato_parked_robot.py',ROOT/'rl/tomato_exported_robot.py']}}
  if not all(hashlib.sha256(Path(q).read_bytes()).hexdigest()==h for q,h in pins.items()):raise ValueError('Source pin mismatch')
  write(out,'input_manifest.json',dict(source_sha256=pins,base_scene=plan['scene'],base_plan=str(plan_path),substeps_per_sample=8,original_substeps_per_sample=4,route_samples=len(plan['right_joint_route_rad']),route_duration_s=len(plan['right_joint_route_rad'])*8*plan['dt_s'],settle_steps=240,physical_step_cap=4091,controller='Unchanged implicit joint-position drives: arms2500/150, hands3/.15; follower gains0.',scope='GUI rendered dry motion. Original 90mm-offset route, half speed, scripted joint targets. No contact/deformation/fracture/video/training. Initial-state writes only before executed route.',limits=dict(joint_tracking_rad=.03,joint_speed_rad_s=3.,mount_position_m=2e-5,mount_angle_rad=2e-4,target_aabb_gap_m=.015,blade_board_height_m=.004,forbidden_contact_n=.1,left_arm_tracking_rad=.03,final_joint_speed_rad_s=.002,arm_limit_margin_rad=-1e-5)))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=False,device='cpu',visualizer=['kit']).app
  import numpy as np,torch
  from scipy.spatial.transform import Rotation
  from pxr import UsdGeom,UsdPhysics,UsdLux
  from tomato_parked_robot import ParkedRobot
  from tomato_exported_robot import ExportedRobot
  from isaaclab.app.settings_manager import get_settings_manager
  from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
  parked=ParkedRobot(out,plan,plan['dt_s']);sim=parked.sim;r=parked.robot;dt=parked.dt
  control=parked.positive_control();steps=parked.setup_steps
  write(out,'collision_positive_control.json',control)
  # Lighting is display-only; original physical scene and asset files remain unchanged.
  light=UsdLux.DomeLight.Define(sim.stage,'/DryMotionInspectionLight');light.CreateIntensityAttr(700.)
  sim.set_camera_view(eye=(1.05,-1.25,.75),target=(.22,0.,.05))
  for _ in range(15):sim.render()
  fk=ExportedRobot(snapshot_path)
  if not np.allclose(fk.mount,parked.mount,atol=1e-12):raise ValueError('Snapshot fixed mount differs')
  left=[i for i,n in enumerate(r.joint_names)if n.startswith('left_AR5')];arms=left+parked.ids
  arm_limits=r.data.joint_pos_limits.torch[0].cpu().numpy()[arms]
  target_json=json.loads((ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());target=np.array([n['position_m']for n in target_json['nodes']])+[0.,0.,.002]
  audit=json.loads((ROOT/'runs/offline/robot_scene_20261101_01/scene_audit.json').read_text());flo,fhi=np.array(audit['fixture_bounds_m'])
  bodyrecords={b['name']:b for b in fk.bodies};contacts=[];shots=[];q0=r.data.joint_pos.torch[0].cpu().numpy().copy()
  def transform(pose):
   t=np.eye(4);t[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();t[:3,3]=pose[:3];return t
  def capture(label,close=False):
   if close:sim.set_camera_view(eye=(.32,-.52,.38),target=(.02,0.,.085))
   for _ in range(8):sim.render()
   viewport=get_active_viewport()
   if viewport is None:raise ValueError('GUI viewport missing')
   path=out/(label+'.png');handle=capture_viewport_to_file(viewport,str(path))
   deadline=time.monotonic()+15
   while time.monotonic()<deadline and(not path.exists()or path.stat().st_size<1000):
    sim.render();time.sleep(.01)
   if not path.exists()or path.stat().st_size<1000:raise ValueError('Viewport capture incomplete: '+label)
   shots.append(str(path));print('INSPECTION_FRAME',label,flush=True)
   if close:
    sim.set_camera_view(eye=(1.05,-1.25,.75),target=(.22,0.,.05));sim.render()
  capture('00_start_overview');capture('01_start_detail',True)
  pose0=r.data.body_link_pose_w.torch[0].cpu().numpy().copy()
  joint_write_count_at_start=1
  stream=(out/'motion_trace.jsonl').open('w',buffering=1)
  min_link_gaps={};min_target_body_gaps={};command_tool=[];actual_tool=[];rawposes=[];rawq=[];rawqd=[];rawgoal=[]
  def measure(goal,sample,substep,phase):
   poses=r.data.body_link_pose_w.torch[0].cpu().numpy();q=r.data.joint_pos.torch[0].cpu().numpy();qd=r.data.joint_vel.torch[0].cpu().numpy();T=transform(poses[parked.tool]);expected=transform(poses[parked.hand])@parked.mount
   vertices=parked.blade@T[:3,:3].T+T[:3,3];lo=vertices.min(0);hi=vertices.max(0)
   gap=float(np.maximum(target.min(0)-hi,lo-target.max(0)).max());board=float(lo[2]);fixture=float(np.maximum(flo-hi,lo-fhi).max())
   mount=float(np.linalg.norm(T[:3,3]-expected[:3,3]));angle=float(Rotation.from_matrix(T[:3,:3]@expected[:3,:3].T).magnitude())
   qgoal=goal.cpu().numpy()[0];track=float(abs(q[parked.ids]-qgoal[parked.ids]).max());left_error=float(abs(q[left]-parked.home.cpu().numpy()[0,left]).max());speed=float(abs(qd).max())
   margin=float(np.minimum(q[arms]-arm_limits[:,0],arm_limits[:,1]-q[arms]).min())
   norm=np.linalg.norm(parked.contacts(),axis=-1);peak=float(norm.max(initial=0.))
   C=fk.knife_pose(dict(zip(r.joint_names,map(float,qgoal))))
   tool_error=float(np.linalg.norm(T[:3,3]-C[:3,3]));tool_angle=float(Rotation.from_matrix(T[:3,:3]@C[:3,:3].T).magnitude())
   # Authored per-link geometry bounds transformed with actual measured Native poses.
   for bi,name in enumerate(r.body_names):
    b=bodyrecords[name]
    if 'geometry_body_local_min_m'not in b or b['unbounded_geometry_paths']:raise ValueError('Missing geometry bounds '+name)
    low=np.array(b['geometry_body_local_min_m']);high=np.array(b['geometry_body_local_max_m']);corners=np.array([[x,y,z]for x in [low[0],high[0]]for y in [low[1],high[1]]for z in [low[2],high[2]]]);BT=transform(poses[bi]);world=corners@BT[:3,:3].T+BT[:3,3];bl=world.min(0);bh=world.max(0)
    tg=float(np.maximum(target.min(0)-bh,bl-target.max(0)).max());min_target_body_gaps[name]=min(min_target_body_gaps.get(name,float('inf')),tg)
    if bi not in (parked.tool,parked.hand):
     separation=float(np.maximum(bl-hi,lo-bh).max());min_link_gaps[name]=min(min_link_gaps.get(name,float('inf')),separation)
   row=dict(step=steps,time_s=(steps-parked.setup_steps)*dt,sample=sample,substep=substep,phase=phase,right_tracking_rad=track,left_arm_tracking_rad=left_error,joint_speed_rad_s=speed,arm_limit_margin_rad=margin,tool_tracking_position_m=tool_error,tool_tracking_angle_rad=tool_angle,mount_position_error_m=mount,mount_angle_error_rad=angle,target_aabb_gap_m=gap,blade_board_height_m=board,fixture_aabb_gap_m=fixture,maximum_rigid_contact_force_n=peak,tool_pose=poses[parked.tool].tolist())
   rows.append(row);stream.write(json.dumps(row)+'\n');rawposes.append(poses.copy());rawq.append(q.copy());rawqd.append(qd.copy());rawgoal.append(qgoal.copy());command_tool.append(C);actual_tool.append(T)
   if not np.isfinite(poses).all()or not np.isfinite(qd).all()or track>.03 or left_error>.03 or speed>3. or gap<=.015 or board<=.004 or mount>2e-5 or angle>2e-4 or peak>.1 or margin< -1e-5:raise ValueError(('Dry-motion gate failed',row))
   if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError('Unexpected external wrench')
  physical_start=time.monotonic()
  for i,right in enumerate(plan['right_joint_route_rad']):
   goal=parked.home.clone();goal[:,parked.ids]=torch.tensor([right],dtype=torch.float32)
   for sub in range(8):
    if (out/'stop.request').exists():raise InterruptedError('Owned guard stop')
    r.set_joint_position_target_index(target=goal);r.write_data_to_sim();parked.probe.write_data_to_sim();sim.step(render=False);steps+=1;r.update(dt);parked.probe.update(dt);measure(goal,i,sub,'route')
   sim.render()
   if i%120==0:print('ROUTE_SAMPLE',i,'of480',flush=True)
   if i in (120,240,360):capture(f'{i:03}_route_detail',True)
   # Pace the visible trajectory no faster than simulated time. No extra physics updates.
   delay=(i+1)*8*dt-(time.monotonic()-physical_start)
   if delay>0:time.sleep(min(delay,.04))
  for i in range(240):
   r.set_joint_position_target_index(target=parked.home);r.write_data_to_sim();parked.probe.write_data_to_sim();sim.step(render=False);steps+=1;r.update(dt);parked.probe.update(dt);measure(parked.home,480,i,'settle')
   if i%8==0:sim.render()
  stream.close()
  np.savez_compressed(out/'measured_motion.npz',body_link_poses=np.array(rawposes),joint_positions=np.array(rawq),joint_velocities=np.array(rawqd),joint_position_commands=np.array(rawgoal),commanded_tool_matrices=np.array(command_tool),actual_tool_matrices=np.array(actual_tool),body_names=np.array(r.body_names),joint_names=np.array(r.joint_names),initial_q=q0,initial_body_poses=pose0,arm_ids=np.array(arms),arm_limits=arm_limits)
  final_speed=float(abs(rawqd[-1]).max());right_ranges=np.ptp(np.array(rawq)[:,parked.ids],axis=0)
  checks=dict(original_route_half_speed=True,one_initial_joint_state_write_only=True,tracking_bounded=max(x['right_tracking_rad']for x in rows)<.03,left_arm_bounded=max(x['left_arm_tracking_rad']for x in rows)<.03,mount_fixed=max(x['mount_position_error_m']for x in rows)<2e-5 and max(x['mount_angle_error_rad']for x in rows)<2e-4,no_target_contact=min(x['target_aabb_gap_m']for x in rows)>.015,board_clear=min(x['blade_board_height_m']for x in rows)>.004,no_monitored_forbidden_contact=max(x['maximum_rigid_contact_force_n']for x in rows)<=.1,arm_limits=min(x['arm_limit_margin_rad']for x in rows)>=-1e-5,right_arm_moves=bool(np.all(right_ranges>.01)),stroke_executed=max(x['tool_pose'][2]for x in rows)-min(x['tool_pose'][2]for x in rows)>.13,stationary_at_end=final_speed<.002,sources_unchanged=all(hashlib.sha256(Path(q).read_bytes()).hexdigest()==h for q,h in pins.items()),expected_physics_count=steps==4091)
  r.reset();r.set_joint_velocity_target_index(target=torch.zeros_like(parked.home));r.set_joint_effort_target_index(target=torch.zeros_like(parked.home));r.set_joint_position_target_index(target=parked.home);r.write_data_to_sim()
  capture('500_final_overview');capture('501_final_detail',True)
  sim.stage.GetRootLayer().Export(str(out/'inspection_scene.usda'))
  sim.pause()
  write(out,'measurements.json',dict(checks=checks,controlled_steps=steps,route_steps=3848,settle_steps=240,setup_steps=parked.setup_steps,physical_route_duration_s=3848*dt,final_joint_speed_rad_s=final_speed,right_joint_ranges_rad=right_ranges.tolist(),maximum_right_tracking_rad=max(x['right_tracking_rad']for x in rows),maximum_left_arm_tracking_rad=max(x['left_arm_tracking_rad']for x in rows),maximum_tool_tracking_position_m=max(x['tool_tracking_position_m']for x in rows),maximum_tool_tracking_angle_rad=max(x['tool_tracking_angle_rad']for x in rows),minimum_target_aabb_gap_m=min(x['target_aabb_gap_m']for x in rows),minimum_board_height_m=min(x['blade_board_height_m']for x in rows),minimum_fixture_aabb_gap_m=min(x['fixture_aabb_gap_m']for x in rows),maximum_mount_position_error_m=max(x['mount_position_error_m']for x in rows),maximum_mount_angle_error_rad=max(x['mount_angle_error_rad']for x in rows),maximum_joint_speed_rad_s=max(x['joint_speed_rad_s']for x in rows),maximum_contact_force_n=max(x['maximum_rigid_contact_force_n']for x in rows),minimum_blade_link_aabb_gaps_m=min_link_gaps,minimum_target_body_aabb_gaps_m=min_target_body_gaps,screenshots=shots,scope='One slow scripted dry route; stationary visual tomato; no Newton target stepping/contact/cutting/training. Authored AABB disjointness is a coarse certificate only; overlap is unresolved, not a collision verdict. Final scene paused; 30-second bounded inspection window then owned cleanup.'))
  if not all(checks.values()):raise ValueError(('Dry-motion result checks failed',checks))
  passed=True;print('DRY_MOTION_CHECKS_PASS — scene paused for30seconds',flush=True)
  until=time.monotonic()+30
  while app.is_running()and time.monotonic()<until and not(out/'stop.request').exists():app.update();time.sleep(.02)
 except BaseException as exc:
  write(out,'worker_error.json',dict(error=repr(exc),traceback=traceback.format_exc()))
 finally:
  write(out,'worker_result.json',dict(diagnostic_passed=passed,visible_dry_motion_passed=passed,controlled_steps=steps,newton_steps=0,episodes_completed=int(passed),shutdown_requested=app is not None,training=False))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
