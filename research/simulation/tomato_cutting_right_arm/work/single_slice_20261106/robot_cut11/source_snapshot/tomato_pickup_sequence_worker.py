"""Scripted close-before-lift demo. Fixture clamp transfers to ideal hand mount.
No friction-only grasp claim; no cutting, training, or video recording.
"""
import argparse,json,time,traceback,signal
from pathlib import Path
from tomato_isaac_startup_worker import write
R=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--interactive',action='store_true');args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True);app=sim=None;steps=0;passed=False;rows=[]
 def stop(*_):raise InterruptedError('Stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  import numpy as np,torch
  from scipy.spatial.transform import Rotation
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=False,device='cpu',visualizer=['kit']).app
  import isaaclab.sim as su
  from isaaclab_physx.physics import PhysxCfg,PhysxManager
  from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
  from isaaclab.actuators import ImplicitActuatorCfg
  from isaaclab.app.settings_manager import get_settings_manager
  from pxr import UsdPhysics,Gf
  from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
  p=json.loads((R/'work/pickup_demo_20261104/pickup_plan.json').read_text());write(out,'scope.json',dict(scripted=True,ideal_fixture_clamp=True,ideal_hand_attachment=True,friction_retention=False,video_recorded=False))
  dt=1/240;get_settings_manager().set_bool('/physics/disableContactProcessing',False)
  sim=su.SimulationContext(su.SimulationCfg(device='cpu',dt=dt,gravity=(0,0,-9.81),use_fabric=False,use_newton_actuators=False,physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),log_dir=str(out)));sim.stage.GetRootLayer().subLayerPaths.append(p['scene']);root=np.array(p['robot_root_world_matrix'])
  r=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,init_state=ArticulationCfg.InitialStateCfg(pos=tuple(root[:3,3]),rot=tuple(Rotation.from_matrix(root[:3,:3]).as_quat()),joint_pos=p['home_rad']),actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),'hand':ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
  tool=RigidObject(RigidObjectCfg(prim_path=p['tool_path'],spawn=None,init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(p['knife_origin_route_m'][0]),rot=tuple(Rotation.from_matrix(p['knife_rotation']).as_quat()))));sim.reset();r.update(dt);tool.update(dt)
  assert 'MountedKnife' not in r.body_names,'Knife still part of articulation'
  home=torch.tensor([[p['home_rad'][n]for n in r.joint_names]],dtype=torch.float32);closed=torch.tensor([[p['closed_home_rad'][n]for n in r.joint_names]],dtype=torch.float32);r.write_joint_state_to_sim_index(position=home,velocity=torch.zeros_like(home));r.set_joint_position_target_index(target=home);r.write_data_to_sim();r.update(dt)
  tool.write_root_pose_to_sim_index(root_pose=tool.data.default_root_pose.torch.clone());tool.write_root_velocity_to_sim_index(velocity=torch.zeros((1,6)));tool.update(dt)
  arms=[i for i,n in enumerate(r.joint_names)if '_AR5_'in n];right=[r.joint_names.index(n)for n in p['right_joint_names']];fingers=[i for i,n in enumerate(r.joint_names)if 'right_rh_'in n];hand=r.body_names.index(p['hand_path'].rsplit('/',1)[-1]);bodies=[str(x.GetPath())for x in sim.stage.Traverse()if x.HasAPI(UsdPhysics.RigidBodyAPI)];filters=bodies+[p['board_path'],p['counter_path']]+p['fixture_paths'];contact=PhysxManager.get_physics_sim_view().create_rigid_contact_view(bodies,[filters for _ in bodies],max_contact_data_count=16384)
  mount=UsdPhysics.FixedJoint(sim.stage.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount'));clamp=UsdPhysics.FixedJoint(sim.stage.GetPrimAtPath('/PickupFixture/Clamp'));initial_tool=None;attached=False;attachment=None
  def trans(pose):
   t=np.eye(4);t[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();t[:3,3]=pose[:3];return t
  def capture(name,close=False):
   if close:
    center=np.array(p['knife_origin_route_m'][0])+np.array(p['knife_rotation'])@np.array([-.086,.0076,.0016]);sim.set_camera_view(eye=(center+np.array([.25,-.35,.22])).tolist(),target=center.tolist())
   else:sim.set_camera_view(eye=[1.5,1.2,1.0],target=[.45,-.15,-.05])
   for _ in range(15):sim.render()
   dest=out/(name+'.png');capture_viewport_to_file(get_active_viewport(),str(dest));end=time.monotonic()+15
   while not dest.exists()and time.monotonic()<end:sim.render();time.sleep(.01)
  def advance(target,phase):
   nonlocal steps,initial_tool
   start=time.monotonic();effort=torch.zeros_like(home);effort[:,arms]=r.data.gravity_compensation_forces.torch[:,arms];r.set_joint_position_target_index(target=target);r.set_joint_effort_target_index(target=effort);r.write_data_to_sim();tool.write_data_to_sim();sim.step(render=(steps%8==0));r.update(dt);tool.update(dt);steps+=1
   pose=tool.data.root_pose_w.torch[0].cpu().numpy();hp=r.data.body_link_pose_w.torch[0,hand].cpu().numpy();q=r.data.joint_pos.torch;v=r.data.joint_vel.torch;forces=contact.get_contact_force_matrix(dt=dt);forces=forces if isinstance(forces,np.ndarray)else forces.numpy();norm=np.linalg.norm(forces,axis=-1);bad=[]
   for i,j in np.argwhere(norm>.1):
    if bodies[i]==p['tool_path'] and filters[j]in p['fixture_paths']:continue
    bad.append((bodies[i],filters[j],float(norm[i,j])))
   if bad:write(out,'collision_pairs.json',bad);raise ValueError(('Unexpected collision',bad[:3]))
   if initial_tool is None:initial_tool=pose.copy()
   tracking=float((q[:,arms]-target[:,arms]).abs().max());speed=float(v.abs().max());hold_error=float(np.linalg.norm(pose[:3]-initial_tool[:3]));mount_error=0
   if attached:mount_error=float(np.linalg.norm((np.linalg.inv(trans(hp))@trans(pose)-attachment)[:3,3]))
   if not np.isfinite(pose).all()or tracking>.03 or speed>3 or (not attached and hold_error>2e-4)or(attached and mount_error>.0003):raise ValueError(('Tracking/hold/mount stop',phase,tracking,speed,hold_error,mount_error))
   row=dict(step=steps,phase=phase,tool_pose=pose.tolist(),tracking_rad=tracking,max_speed_rad_s=speed,pre_attach_displacement_m=hold_error,mount_error_m=mount_error,fixture_enabled=clamp.GetJointEnabledAttr().Get(),hand_mount_enabled=mount.GetJointEnabledAttr().Get(),finger_error_rad=float((q[:,fingers]-closed[:,fingers]).abs().max()))
   if steps%8==0:rows.append(row)
   if args.interactive:time.sleep(max(0,dt-(time.monotonic()-start)))
  for _ in range(120):advance(home,'supported_open')
  capture('01_supported_open');capture('01_open_closeup',True)
  for i in range(480):
   u=(i+1)/480;b=u*u*u*(10+u*(-15+6*u));advance(home+(closed-home)*b,'close_fingers')
  for _ in range(120):advance(closed,'closed_on_fixture')
  if float((r.data.joint_pos.torch[:,fingers]-closed[:,fingers]).abs().max())>.025:raise ValueError('Fingers did not close before attachment')
  capture('02_closed_before_lift');capture('02_closed_closeup',True)
  hp=r.data.body_link_pose_w.torch[0,hand].cpu().numpy();tp=tool.data.root_pose_w.torch[0].cpu().numpy();attachment=np.linalg.inv(trans(hp))@trans(tp);rot=Rotation.from_matrix(attachment[:3,:3]).as_quat();mount.CreateLocalPos0Attr(Gf.Vec3f(*attachment[:3,3]));mount.CreateLocalRot0Attr(Gf.Quatf(float(rot[3]),Gf.Vec3f(*rot[:3])));mount.GetJointEnabledAttr().Set(True);clamp.GetJointEnabledAttr().Set(False);attached=True;write(out,'attachment_event.json',dict(step=steps,finger_error_rad=float((r.data.joint_pos.torch[:,fingers]-closed[:,fingers]).abs().max()),tool_pose=tp.tolist(),attachment=attachment.tolist()))
  for _ in range(120):advance(closed,'attachment_hold')
  for route in p['lift_route']:
   target=closed.clone();target[:,right]=torch.tensor(route)
   for _ in range(4):advance(target,'lift')
  for _ in range(240):advance(target,'lifted_hold')
  capture('03_lifted');capture('03_lifted_closeup',True)
  rise=float(tool.data.root_pose_w.torch[0,2])-float(initial_tool[2]);assert rise>.06,('Insufficient lift',rise)
  write(out,'measurements.json',dict(rows=rows,lift_m=rise,initial_tool_pose=initial_tool.tolist(),friction_retention_validated=False));passed=True
  if args.interactive:
   sim.pause()
   while app.is_running():app.update();time.sleep(.01)
 except BaseException:
  write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
  if sim is not None:
   try:capture('failure')
   except Exception:pass
 finally:
  write(out,'worker_result.json',dict(demo_grip_passed=passed,controlled_steps=steps,shutdown_requested=app is not None,training=False))
  if sim is not None:sim.stop();sim.clear_instance()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
