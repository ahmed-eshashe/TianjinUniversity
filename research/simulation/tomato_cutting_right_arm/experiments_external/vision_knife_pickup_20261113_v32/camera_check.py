"""Bounded native free-knife settling and real head RGB-D sensor check; no training."""
from pathlib import Path
import argparse,json,sys,time,traceback
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);args=a.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True);app=sim=None
try:
 import numpy as np,torch
 from scipy.spatial.transform import Rotation
 from isaaclab.app import AppLauncher
 app=AppLauncher(headless=True,enable_cameras=True,device='cpu',visualizer=['none']).app
 import isaaclab.sim as su
 from isaaclab_physx.physics import PhysxCfg,PhysxManager
 from isaaclab_physx.renderers import IsaacRtxRendererCfg
 from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
 from isaaclab.actuators import ImplicitActuatorCfg
 from isaaclab.sensors.camera import Camera,CameraCfg
 from isaaclab.app.settings_manager import get_settings_manager
 from pxr import Usd,UsdGeom,UsdPhysics,PhysxSchema
 from PIL import Image
 c=json.loads((W/'scene_config.json').read_text());assert not c['unsupported_board_samples']
 sim=su.SimulationContext(su.SimulationCfg(device='cpu',dt=1/960,gravity=(0,0,-9.81),use_fabric=False,use_newton_actuators=False,physics=PhysxCfg(solver_type=1),log_dir=str(out)))
 sim.stage.GetRootLayer().subLayerPaths.append(c['scene'])
 for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/KitchenEnvironment')):
  if prim.HasAPI(UsdPhysics.CollisionAPI):UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Set(False)
  if prim.HasAPI(UsdPhysics.RigidBodyAPI):UsdPhysics.RigidBodyAPI(prim).GetRigidBodyEnabledAttr().Set(False)
  if prim.IsA(UsdPhysics.Joint):prim.SetActive(False)
 for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/dual_ar5_o6')):
  if prim.HasAPI(UsdPhysics.RigidBodyAPI):PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.)
  if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
   api=PhysxSchema.PhysxArticulationAPI.Apply(prim);api.CreateSolverPositionIterationCountAttr(64);api.CreateSolverVelocityIterationCountAttr(16)
 root=np.array(c['robot_root_world_matrix'])
 r=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,init_state=ArticulationCfg.InitialStateCfg(pos=tuple(root[:3,3]),rot=tuple(Rotation.from_matrix(root[:3,:3]).as_quat()),joint_pos=c['home_rad']),actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),'hand':ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
 pose=c['knife_pose_xyzw'];knife=RigidObject(RigidObjectCfg(prim_path=c['knife_path'],spawn=None,init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(pose[:3]),rot=tuple(pose[3:]))))
 camera=Camera(CameraCfg(prim_path=c['camera_path'],spawn=None,width=320,height=240,data_types=['rgb','distance_to_image_plane'],update_period=0.,update_latest_camera_pose=True,renderer_cfg=IsaacRtxRendererCfg()))
 sim.reset();r.update(sim.cfg.dt);knife.update(sim.cfg.dt);get_settings_manager().set_bool('/physics/disableContactProcessing',False)
 home=torch.tensor([[c['home_rad'][n] for n in r.joint_names]],dtype=torch.float32);r.write_joint_state_to_sim_index(position=home,velocity=torch.zeros_like(home));r.set_joint_position_target_index(target=home);arms=[i for i,n in enumerate(r.joint_names) if '_AR5_' in n]
 assert not any(p.IsA(UsdPhysics.Joint) and c['knife_path'] in [str(x) for rel in [UsdPhysics.Joint(p).GetBody0Rel(),UsdPhysics.Joint(p).GetBody1Rel()] for x in rel.GetTargets()] for p in sim.stage.Traverse()),'Knife is still attached'
 body=sim.stage.GetPrimAtPath(c['knife_path']);assert not UsdPhysics.RigidBodyAPI(body).GetKinematicEnabledAttr().Get()
 filters=[c['board_path'],c['counter_path']];contact=PhysxManager.get_physics_sim_view().create_rigid_contact_view([c['knife_path']],[filters],max_contact_data_count=256)
 trace=[];start=time.monotonic()
 for k in range(1920):
  effort=torch.zeros_like(home);effort[:,arms]=r.data.gravity_compensation_forces.torch[:,arms];r.set_joint_position_target_index(target=home);r.set_joint_effort_target_index(target=effort);r.write_data_to_sim();knife.write_data_to_sim();sim.step(render=False);r.update(sim.cfg.dt);knife.update(sim.cfg.dt)
  if k%96==0:
   row=dict(step=k,pose=knife.data.root_pose_w.torch[0].tolist(),velocity=knife.data.root_vel_w.torch[0].tolist());trace.append(row);(out/'progress.json').write_text(json.dumps(row))
  if not torch.isfinite(knife.data.root_pose_w.torch).all():raise ValueError('Nonfinite knife state')
  if k%192==0:sim.render()
 for _ in range(20):sim.render();camera.update(sim.cfg.dt,force_recompute=True)
 def arr(x):return x.numpy() if not hasattr(x,'torch') else x.torch.cpu().numpy()
 rgb=arr(camera.data.output['rgb'])[0,:,:,:3];depth=arr(camera.data.output['distance_to_image_plane'])[0].squeeze();Image.fromarray(rgb.astype(np.uint8)).save(out/'head_rgb.png');np.save(out/'head_depth_m.npy',depth);Image.fromarray((255*np.clip(np.nan_to_num(depth,nan=0.,posinf=3.)/3.,0,1)).astype('uint8')).save(out/'head_depth_preview.png')
 matrix=contact.get_contact_force_matrix(dt=sim.cfg.dt);matrix=matrix.numpy() if hasattr(matrix,'numpy') else matrix
 K=arr(camera.data.intrinsic_matrices)[0];pos=arr(camera.data.pos_w)[0];quat=arr(camera.data.quat_w_ros)[0];rot=Rotation.from_quat(quat).as_matrix();lo,hi=np.array(c['board_world_bounds']);corners=np.array([[x,y,hi[2]] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]]]);view=(corners-pos)@rot;pix=view@K.T;pix=pix[:,:2]/pix[:,2,None]
 report=dict(scope='Head RGB-D and centered-board free settling only; no pickup or learned policy.',pass_camera=bool(np.all(view[:,2]>0) and np.all((pix[:,0]>=0)&(pix[:,0]<320)&(pix[:,1]>=0)&(pix[:,1]<240)) and np.isfinite(depth).mean()>.8 and rgb.std()>5),camera_position_world_m=pos.tolist(),camera_quaternion_xyzw_ros=quat.tolist(),intrinsics=K.tolist(),board_corner_pixels=pix.tolist(),depth_finite_fraction=float(np.isfinite(depth).mean()),rgb_std=float(rgb.std()),board_centre_world_m=c['board_centre_world_m'],board_lateral_offset_m=c['board_lateral_offset_m'],unsupported_board_samples=0,knife_pose=knife.data.root_pose_w.torch[0].tolist(),knife_velocity=knife.data.root_vel_w.torch[0].tolist(),knife_support_forces_N=np.linalg.norm(matrix,axis=-1).tolist(),knife_free_rigid_body=True,attachments=False,trace=trace,wall_s=time.monotonic()-start)
 (out/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='trace'},indent=2))
except BaseException:
 (out/'failure.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:
 if sim is not None:sim.stop();sim.clear_instance()
 if app is not None:app.close()
