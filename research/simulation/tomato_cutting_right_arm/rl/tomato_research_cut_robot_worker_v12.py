"""Scripted close-before-lift demo. Fixture clamp transfers to ideal hand mount.
Experimental original-research-model cutting extension. No training or video recording.
"""
import argparse,json,time,traceback,signal,os
from pathlib import Path
from tomato_isaac_startup_worker import write
R=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--interactive',action='store_true');parser.add_argument('--headless',action='store_true');parser.add_argument('--cut-steps',type=int,default=20000);parser.add_argument('--resume-checkpoint',type=Path);args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True);app=sim=None;steps=0;passed=False;rows=[]
 def stop(*_):raise InterruptedError('Stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  import numpy as np,torch
  from scipy.spatial.transform import Rotation
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=args.headless,device='cpu',visualizer=['none'] if args.headless else ['kit']).app
  import isaaclab.sim as su
  from isaaclab_physx.physics import PhysxCfg,PhysxManager
  from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
  from isaaclab.actuators import ImplicitActuatorCfg
  from isaaclab.app.settings_manager import get_settings_manager
  from pxr import UsdPhysics,UsdGeom,Gf,PhysxSchema,Usd,UsdShade,Vt
  if not args.headless:
   from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
  p=json.loads((R/'work/backward_elbow_20261105/plan.json').read_text());write(out,'scope.json',dict(scripted=True,ideal_fixture_clamp=True,ideal_hand_attachment=True,friction_retention=False,video_recorded=False))
  dt=1/240;get_settings_manager().set_bool('/physics/disableContactProcessing',False)
  sim=su.SimulationContext(su.SimulationCfg(device='cpu',dt=dt,gravity=(0,0,-9.81),use_fabric=False,use_newton_actuators=False,physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),log_dir=str(out)));sim.stage.GetRootLayer().subLayerPaths.append(p['scene']);root=np.array(p['robot_root_world_matrix'])
  cut_plan=json.loads((R/'work/single_slice_20261106/clear_entry_robot_plan_v8.json').read_text());cut_rotation=np.array(cut_plan['target_rotation']);cut_translation=np.array(cut_plan['target_translation']);prepared_target=np.load(R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz')['x'];cut_points=prepared_target@cut_rotation.T+cut_translation
  design=json.loads((R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());old_target=sim.stage.GetPrimAtPath('/CuttingTargetVisual');material=UsdShade.MaterialBindingAPI(old_target).ComputeBoundMaterial()[0];UsdGeom.Imageable(old_target).MakeInvisible()
  for piece in design['pieces']:
   mesh=UsdGeom.Mesh.Define(sim.stage,'/ResearchCut/'+piece['side']);faces=np.array(piece['triangles']);mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(cut_points.astype(np.float32)));mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr(faces.ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True)
   if material and material.GetPrim().IsValid():UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material)
  # Session-only physics cleanup: visual background remains visual, and
  # reflection of a symmetric cube becomes an equivalent proper transform.
  for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/KitchenEnvironment')):
   if prim.HasAPI(UsdPhysics.CollisionAPI):UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Set(False)
   if prim.HasAPI(UsdPhysics.RigidBodyAPI):UsdPhysics.RigidBodyAPI(prim).GetRigidBodyEnabledAttr().Set(False)
   if prim.IsA(UsdPhysics.Joint):UsdPhysics.Joint(prim).GetJointEnabledAttr().Set(False)
  for path in p['fixture_paths']:
   prim=sim.stage.GetPrimAtPath(path);xf=UsdGeom.Xformable(prim);matrix=np.array(xf.GetLocalTransformation())
   if np.linalg.det(matrix[:3,:3])<0:
    matrix[0,:3]*=-1;xf.ClearXformOpOrder();op=xf.AddTransformOp(opSuffix='properCube');op.Set(Gf.Matrix4d(matrix.tolist()))
  for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/dual_ar5_o6')):
   if prim.HasAPI(UsdPhysics.RigidBodyAPI) and UsdPhysics.RigidBodyAPI(prim).GetRigidBodyEnabledAttr().Get()!=False:PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.)
  for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/dual_ar5_o6')):
   if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
    api=PhysxSchema.PhysxArticulationAPI.Apply(prim);api.CreateSolverPositionIterationCountAttr(64);api.CreateSolverVelocityIterationCountAttr(16)
   if prim.HasAPI(UsdPhysics.RigidBodyAPI):
    api=PhysxSchema.PhysxRigidBodyAPI.Apply(prim);api.CreateSolverPositionIterationCountAttr(64);api.CreateSolverVelocityIterationCountAttr(16)
  refined=[]
  for row in json.loads((R/'work/single_slice_20261106/wrist_collision_shapes.json').read_text()):
   prim=sim.stage.GetPrimAtPath(row['path']);api=PhysxSchema.PhysxConvexDecompositionCollisionAPI.Apply(prim);api.CreateMaxConvexHullsAttr(128);api.CreateHullVertexLimitAttr(64);api.CreateVoxelResolutionAttr(1000000);api.CreateErrorPercentageAttr(1.);api.CreateShrinkWrapAttr(True);api.CreateMinThicknessAttr(.0001);refined.append(row['path'])
  write(out,'collision_refinement.json',dict(paths=refined,max_hulls=128,hull_vertices=64,voxel_resolution=1000000,error_percent=1.,shrink_wrap=True,min_thickness_m=.0001,original_mesh_unchanged=True,collision_enabled=True))
  board=sim.stage.GetPrimAtPath(p['board_path']);cache=UsdGeom.XformCache();world=np.array(cache.GetLocalToWorldTransform(board)).T;parent=np.array(cache.GetLocalToWorldTransform(board.GetParent())).T;world[:3,3]+=np.array([-.05,0.,0.]);local=np.linalg.inv(parent)@world;xf=UsdGeom.Xformable(board);xf.ClearXformOpOrder();xf.AddTransformOp(opSuffix='sliceBoardPlacement').Set(Gf.Matrix4d(local.T.tolist()))
  write(out,'board_placement.json',dict(world_translation_change_m=[-.05,0.,0.],visual_and_collision_together=True,material_support_plane_z_unchanged=True))
  r=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,init_state=ArticulationCfg.InitialStateCfg(pos=tuple(root[:3,3]),rot=tuple(Rotation.from_matrix(root[:3,:3]).as_quat()),joint_pos=p['home_rad']),actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),'hand':ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
  tool=RigidObject(RigidObjectCfg(prim_path=p['tool_path'],spawn=None,init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(p['knife_origin_route_m'][0]),rot=tuple(Rotation.from_matrix(p['knife_rotation']).as_quat()))));sim.reset();r.update(dt);tool.update(dt)
  get_settings_manager().set_bool('/physics/disableContactProcessing',False)
  import carb
  assert carb.settings.get_settings().get('/physics/disableContactProcessing') is False
  write(out,'contact_reporting_enabled.json',dict(enabled_after_simulation_initialization=True,actual_disabled_setting=carb.settings.get_settings().get('/physics/disableContactProcessing')))
  write(out,'runtime_joint_limits.json',dict(names=r.joint_names,limits=r.root_view.get_dof_limits().numpy().tolist()))
  assert 'MountedKnife' not in r.body_names,'Knife still part of articulation'
  home=torch.tensor([[p['home_rad'][n]for n in r.joint_names]],dtype=torch.float32);closed=torch.tensor([[p['closed_home_rad'][n]for n in r.joint_names]],dtype=torch.float32);r.write_joint_state_to_sim_index(position=home,velocity=torch.zeros_like(home));r.set_joint_position_target_index(target=home);r.write_data_to_sim();r.update(dt)
  tool.write_root_pose_to_sim_index(root_pose=tool.data.default_root_pose.torch.clone());tool.write_root_velocity_to_sim_index(root_velocity=torch.zeros((1,6)));tool.update(dt)
  arms=[i for i,n in enumerate(r.joint_names)if '_AR5_'in n];right=[r.joint_names.index(n)for n in p['right_joint_names']];fingers=[i for i,n in enumerate(r.joint_names)if 'right_rh_'in n];hand=r.body_names.index(p['hand_path'].rsplit('/',1)[-1]);bodies=[str(x.GetPath())for x in sim.stage.Traverse()if str(x.GetPath()).startswith('/dual_ar5_o6/') and x.HasAPI(UsdPhysics.RigidBodyAPI) and UsdPhysics.RigidBodyAPI(x).GetRigidBodyEnabledAttr().Get()!=False];filters=bodies+[p['board_path'],p['counter_path']]+p['fixture_paths'];contact=PhysxManager.get_physics_sim_view().create_rigid_contact_view(bodies,[filters for _ in bodies],max_contact_data_count=16384)
  if contact.sensor_count!=len(bodies) or contact.filter_count!=len(filters):raise ValueError('Incomplete contact observation view')
  mount=UsdPhysics.FixedJoint(sim.stage.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount'));clamp=UsdPhysics.FixedJoint(sim.stage.GetPrimAtPath('/PickupFixture/Clamp'));initial_tool=None;attached=False;attachment=None
  blade=np.array(json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices']);tomato=cut_points
  def trans(pose):
   t=np.eye(4);t[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();t[:3,3]=pose[:3];return t
  def capture(name,close=False):
   if args.headless:return
   if close:
    center=np.array(p['knife_origin_route_m'][0])+np.array(p['knife_rotation'])@np.array([-.086,.0076,.0016]);sim.set_camera_view(eye=(center+np.array([.25,-.35,.22])).tolist(),target=center.tolist())
   else:sim.set_camera_view(eye=[1.05,.8,.8],target=[.40,-.30,-.10])
   camera=UsdGeom.Camera(sim.stage.GetPrimAtPath(str(get_active_viewport().camera_path)));camera.GetFocalLengthAttr().Set(18. if close else 16.);camera.GetHorizontalApertureAttr().Set(20.955 if close else 36.)
   for _ in range(15):sim.render()
   dest=out/(name+'.png');capture_viewport_to_file(get_active_viewport(),str(dest));end=time.monotonic()+15
   while not dest.exists()and time.monotonic()<end:sim.render();time.sleep(.01)
  import omni.timeline
  timeline=omni.timeline.get_timeline_interface()
  smoke=os.environ.get('TOMATO_PICKUP_UI_SMOKE')=='1'
  def wait_for_play():
   deadline=time.monotonic()+.5
   while app.is_running() and not timeline.is_playing():
    app.update();time.sleep(.01)
    if smoke and time.monotonic()>deadline:timeline.play()
   if not app.is_running():raise InterruptedError('Window closed')
   # Kit's toolbar changes the timeline; explicitly resume the standalone controller.
   sim.play()
  def advance(target,phase,velocity_target=None):
   nonlocal steps,initial_tool
   if args.interactive:
    if not timeline.is_playing():sim.pause();wait_for_play()
    if not app.is_running():raise InterruptedError('Window closed')
   if carb.settings.get_settings().get('/physics/disableContactProcessing') is not False:raise ValueError('Contact reporting was disabled after initialization')
   start=time.monotonic();substeps=max(1,int(np.ceil(dt*960)));physics_dt=dt/substeps;sim.cfg.dt=physics_dt
   for sub in range(substeps):
    effort=torch.zeros_like(home);effort[:,arms]=r.data.gravity_compensation_forces.torch[:,arms];r.set_joint_position_target_index(target=target);r.set_joint_velocity_target_index(target=torch.zeros_like(target) if velocity_target is None else velocity_target);r.set_joint_effort_target_index(target=effort);r.write_data_to_sim();tool.write_data_to_sim();sim.step(render=(not args.headless and steps%8==0 and sub==substeps-1));r.update(physics_dt);tool.update(physics_dt)
   steps+=1
   pose=tool.data.root_pose_w.torch[0].cpu().numpy();hp=r.data.body_link_pose_w.torch[0,hand].cpu().numpy();q=r.data.joint_pos.torch;v=r.data.joint_vel.torch;forces=contact.get_contact_force_matrix(dt=physics_dt);forces=forces if isinstance(forces,np.ndarray)else forces.numpy();norm=np.linalg.norm(forces,axis=-1);bad=[]
   for i,j in np.argwhere(norm>.1):
    if bodies[i]==p['tool_path'] and filters[j]in p['fixture_paths'] and not phase.startswith('research_'):continue
    bad.append((bodies[i],filters[j],float(norm[i,j])))
   net=contact.get_net_contact_forces(dt=physics_dt);net=net if isinstance(net,np.ndarray)else net.numpy()
   for i in np.flatnonzero(np.linalg.norm(net,axis=-1)>.1):
    if bodies[i]==p['tool_path'] and not phase.startswith('research_'):continue
    if not any(row[0]==bodies[i]for row in bad):bad.append((bodies[i],'unfiltered_native_contact',float(np.linalg.norm(net[i]))))
   if bad:write(out,'collision_state.json',dict(phase=phase,q=r.data.joint_pos.torch[0].tolist(),joint_names=r.joint_names,body_names=r.body_names,body_poses=r.data.body_link_pose_w.torch[0].tolist(),tool_pose=tool.data.root_pose_w.torch[0].tolist()));write(out,'collision_pairs.json',bad);raise ValueError(('Unexpected collision',bad[:3]))
   if initial_tool is None:initial_tool=pose.copy()
   bt=trans(pose);bv=blade@bt[:3,:3].T+bt[:3,3];gap=float(np.maximum(tomato.min(0)-bv.max(0),bv.min(0)-tomato.max(0)).max())
   if not phase.startswith('research_') and gap<.02:raise ValueError(('Approach crossed noncontact margin',gap))
   if phase.startswith('research_') and float(bv[:,2].min())<.0005:raise ValueError('Actual blade entered board clearance')
   tracking=float((q[:,arms]-target[:,arms]).abs().max());speed=float(v.abs().max());hold_error=float(np.linalg.norm(pose[:3]-initial_tool[:3]));mount_error=0
   if attached:mount_error=float(np.linalg.norm((np.linalg.inv(trans(hp))@trans(pose)-attachment)[:3,3]))
   if not np.isfinite(pose).all()or tracking>.03 or speed>3 or (not attached and hold_error>2e-4)or(attached and mount_error>.0003):
    write(out,'tracking_stop.json',dict(phase=phase,joint_names=r.joint_names,q=q[0].tolist(),target=target[0].tolist(),velocity=v[0].tolist(),tool_pose=pose.tolist(),contact_max=float(norm.max()),contact_force_matrix=forces.tolist()))
    raise ValueError(('Tracking/hold/mount stop',phase,tracking,speed,hold_error,mount_error))
   row=dict(step=steps,phase=phase,target_gap_m=gap,tool_pose=pose.tolist(),tracking_rad=tracking,max_speed_rad_s=speed,pre_attach_displacement_m=hold_error,mount_error_m=mount_error,fixture_enabled=clamp.GetJointEnabledAttr().Get() if clamp.GetPrim().IsValid() else False,hand_mount_enabled=mount.GetJointEnabledAttr().Get(),finger_error_rad=float((q[:,fingers]-closed[:,fingers]).abs().max()))
   if steps%8==0:rows.append(row)
   if args.interactive:time.sleep(max(0,dt-(time.monotonic()-start)))
  if args.interactive:
   capture('ready')
   sim.pause()
   print('READY: press Play in Isaac Sim to close the hand and lift. Fixed attachment is used.',flush=True)
   wait_for_play()
   write(out,'interactive_start.json',dict(toolbar_play_received=True,controller_playing=sim.is_playing(),smoke_test=smoke))
  for _ in range(120):advance(home,'supported_open')
  if not args.interactive:capture('01_supported_open');capture('01_open_closeup',True)
  for i in range(480):
   u=(i+1)/480;b=u*u*u*(10+u*(-15+6*u));advance(home+(closed-home)*b,'close_fingers')
  for _ in range(120):advance(closed,'closed_on_fixture')
  if float((r.data.joint_pos.torch[:,fingers]-closed[:,fingers]).abs().max())>.025:raise ValueError('Fingers did not close before attachment')
  if not args.interactive:capture('02_closed_before_lift');capture('02_closed_closeup',True)
  hp=r.data.body_link_pose_w.torch[0,hand].cpu().numpy();tp=tool.data.root_pose_w.torch[0].cpu().numpy();attachment=np.linalg.inv(trans(hp))@trans(tp) if args.resume_checkpoint is None else np.array(json.loads((args.resume_checkpoint.parent.parent/'attachment_event.json').read_text())['attachment']);rot=Rotation.from_matrix(attachment[:3,:3]).as_quat();mount.CreateLocalPos0Attr(Gf.Vec3f(*attachment[:3,3]));mount.CreateLocalRot0Attr(Gf.Quatf(float(rot[3]),Gf.Vec3f(*rot[:3])));mount.GetJointEnabledAttr().Set(True);clamp.GetJointEnabledAttr().Set(False);attached=True;write(out,'attachment_event.json',dict(step=steps,finger_error_rad=float((r.data.joint_pos.torch[:,fingers]-closed[:,fingers]).abs().max()),tool_pose=tp.tolist(),attachment=attachment.tolist()))
  # Flush USD joint-enable notices in headless runs as well as GUI runs.
  clamp.GetPrim().SetActive(False);app.update();r.update(dt);tool.update(dt)
  for _ in range(120):advance(closed,'attachment_hold')
  for route in p['lift_route']:
   target=closed.clone();target[:,right]=torch.tensor(route)
   for _ in range(4):advance(target,'lift')
  if not args.interactive:capture('03_lifted')
  for route_index,route_set in enumerate(p['approach_routes']):
   for route in route_set:
    previous=target.clone();target=closed.clone();target[:,right]=torch.tensor(route)
    for substep in range(12):advance(previous+(target-previous)*((substep+1)/12),'approach_'+str(route_index))
  for _ in range(240):advance(target,'approach_hold')
  if not args.interactive:capture('04_above_tomato');capture('04_above_tomato_closeup',True)
  from tomato_robot_slice_extension_v12 import run as run_cut
  def set_dt(new_dt):
   nonlocal dt
   dt=new_dt;sim.cfg.dt=new_dt
   if abs(sim.get_physics_dt()-new_dt)>1e-15:raise ValueError('Physics timestep update failed')
  cut_result=run_cut(sim,r,tool,p,advance,set_dt,target,closed,right,out,maximum_steps=args.cut_steps,resume_checkpoint=args.resume_checkpoint)
  write(out,'cutting_extension_result.json',cut_result)
  rise=max(row['tool_pose'][2] for row in rows)-float(initial_tool[2]);assert rise>.06,('Insufficient lift',rise)
  write(out,'actual_pose.json',dict(joint_names=r.joint_names,q=r.data.joint_pos.torch[0].tolist(),body_names=r.body_names,poses=r.data.body_link_pose_w.torch[0].tolist(),tool_pose=tool.data.root_pose_w.torch[0].tolist()))
  write(out,'measurements.json',dict(rows=rows,lift_m=rise,initial_tool_pose=initial_tool.tolist(),friction_retention_validated=False));passed=bool(cut_result['full_slice_success'])
  if args.interactive:
   sim.pause()
   while app.is_running() and not smoke:
    if timeline.is_playing():sim.pause()
    app.update();time.sleep(.01)
 except BaseException:
  write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
  if sim is not None:
   try:capture('failure')
   except Exception:pass
 finally:
  write(out,'worker_result.json',dict(full_slice_success=passed,controlled_steps=steps,shutdown_requested=app is not None,training=False))
  if sim is not None:sim.stop();sim.clear_instance()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
