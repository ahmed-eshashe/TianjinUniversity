"""Actual fixed-mount robot, parked under gravity for synchronized support tests.

No target forces are exchanged here: every episode must keep the blade clear.
A separate probe/floor control tests the rigid contact monitor before episodes.
These are unloaded scene holds, not mounted tomato contact or cutting resets.
Import only after AppLauncher.
"""
import json
from pathlib import Path
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from pxr import UsdPhysics
import isaaclab.sim as sim_utils
from isaaclab_physx.physics import PhysxCfg,PhysxManager
from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.app.settings_manager import get_settings_manager

ROOT=Path(__file__).resolve().parents[1]
class ParkedRobotPGS:
 def __init__(self,out,plan,dt):
  self.dt=dt;self.plan=plan;self.steps=0;self.setup_steps=0;get_settings_manager().set_bool('/physics/disableContactProcessing',False)
  self.sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=dt,gravity=(0.,0.,-9.81),use_fabric=False,use_newton_actuators=False,physics=PhysxCfg(solver_type=0,enable_external_forces_every_iteration=True),log_dir=str(out)))
  self.sim.stage.GetRootLayer().subLayerPaths.append(plan['scene']);m=np.array(plan['robot_root_world_matrix']);self.robot=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,init_state=ArticulationCfg.InitialStateCfg(pos=tuple(m[:3,3]),rot=tuple(Rotation.from_matrix(m[:3,:3]).as_quat()),joint_pos=plan['home_rad']),actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),'hand':ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
  floor=sim_utils.CuboidCfg(size=(.2,.2,.02),collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=True));floor.func('/ContactControlFloor',floor,translation=(2.,0.,-.01));spawn=sim_utils.CuboidCfg(size=(.02,.02,.02),rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),PhysxRigidBodyCfg(disable_gravity=True,sleep_threshold=0.,stabilization_threshold=0.)],collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=True),mass_props=sim_utils.MassCfg(mass=.01,density=0.));self.probe=RigidObject(RigidObjectCfg(prim_path='/ContactControlProbe',spawn=spawn,init_state=RigidObjectCfg.InitialStateCfg(pos=(2.,0.,.3),rot=(0.,0.,0.,1.))));prim=self.sim.stage.GetPrimAtPath('/ContactControlProbe');prim.AddAppliedSchema('PhysxContactReportAPI');prim.CreateAttribute('physxContactReport:threshold',__import__('pxr').Sdf.ValueTypeNames.Float).Set(0.);self.sim.reset();get_settings_manager().set_bool('/physics/disableContactProcessing',False)
  r=self.robot;self.tool=r.body_names.index('MountedKnife');self.hand=r.body_names.index(plan['hand_path'].rsplit('/',1)[-1]);self.ids=[r.joint_names.index(n)for n in plan['right_joint_names']];self.home=torch.tensor([[plan['home_rad'][n]for n in r.joint_names]],dtype=torch.float32);self.mount=np.array(plan['mount_hand_from_knife']);self.blade=np.array(json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices'])
  if r.num_joints!=36:raise ValueError('Fixed mount unexpectedly added a DOF')
  self.bodies=[str(p.GetPath())for p in self.sim.stage.Traverse()if p.HasAPI(UsdPhysics.RigidBodyAPI)];self.filters=self.bodies+[plan['board_path'],plan['counter_path'],'/ContactControlFloor/geometry/mesh'];self.view=PhysxManager.get_physics_sim_view().create_rigid_contact_view(self.bodies,[self.filters for _ in self.bodies],max_contact_data_count=16384);self.initial_count=int(self.sim._physics_step_count);self.reset()
 def reset(self):
  self.episode_steps=0
  r=self.robot;r.reset();r.write_joint_state_to_sim_index(position=self.home,velocity=torch.zeros_like(self.home));r.set_joint_position_target_index(target=self.home);r.write_data_to_sim();r.update(self.dt)
  if float((r.data.joint_pos.torch-self.home).abs().max())>1e-7 or float(r.data.joint_vel.torch.abs().max())!=0 or r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError('Parked robot reset failed')
 def _advance(self):
  r=self.robot;r.set_joint_position_target_index(target=self.home);r.write_data_to_sim();self.probe.write_data_to_sim();self.sim.step(render=False);r.update(self.dt);self.probe.update(self.dt)
 def contacts(self):
  value=self.view.get_contact_force_matrix(dt=self.dt)
  return value if isinstance(value,np.ndarray)else value.numpy()if hasattr(value,'numpy')else value.detach().cpu().numpy()
 def positive_control(self):
  if get_settings_manager().get('/physics/disableContactProcessing'):raise ValueError('Rigid contact processing disabled')
  pose=self.probe.data.default_root_pose.torch.clone();overlap=pose.clone();overlap[:,2]=.009;self.probe.write_root_pose_to_sim_index(root_pose=overlap);velocity=torch.zeros((1,6));velocity[:,2]=-.1;self.probe.write_root_velocity_to_sim_index(root_velocity=velocity);self._advance();self.setup_steps+=1;positive=float(np.linalg.norm(self.contacts()[self.bodies.index('/ContactControlProbe'),self.filters.index('/ContactControlFloor/geometry/mesh')]))
  self.probe.reset();self.probe.write_root_pose_to_sim_index(root_pose=pose);self.probe.write_root_velocity_to_sim_index(root_velocity=torch.zeros((1,6)));clear=[]
  for _ in range(2):self._advance();self.setup_steps+=1;clear.append(float(np.linalg.norm(self.contacts()[self.bodies.index('/ContactControlProbe'),self.filters.index('/ContactControlFloor/geometry/mesh')])))
  self.reset()
  if positive<.01 or max(clear)>1e-6:raise ValueError('Rigid contact positive/clear controls failed')
  return dict(positive_force_n=positive,clear_forces_n=clear,setup_physx_steps=self.setup_steps,target_deformable_steps=0,scope='Separate monitor control before synchronized episodes; target is not advanced during setup.')
 def step(self,target_world):
  self._advance();self.steps+=1;self.episode_steps+=1;r=self.robot;poses=r.data.body_link_pose_w.torch[0].cpu().numpy();tool=poses[self.tool];hand=poses[self.hand]
  def transform(pose):
   t=np.eye(4);t[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();t[:3,3]=pose[:3];return t
  actual=transform(tool);expected=transform(hand)@self.mount;mount_error=float(np.linalg.norm(actual[:3,3]-expected[:3,3]));angle=float(Rotation.from_matrix(actual[:3,:3]@expected[:3,:3].T).magnitude());vertices=self.blade@actual[:3,:3].T+actual[:3,3];gap=float(np.maximum(target_world.min(0)-vertices.max(0),vertices.min(0)-target_world.max(0)).max());board=float(vertices[:,2].min());speed=float(r.data.joint_vel.torch.abs().max());tracking=float((r.data.joint_pos.torch[:,self.ids]-self.home[:,self.ids]).abs().max());contact=np.linalg.norm(self.contacts(),axis=-1);peak=float(contact.max(initial=0.));q=r.data.joint_pos.torch[0].cpu().numpy();qd=r.data.joint_vel.torch[0].cpu().numpy()
  row=dict(q=q.tolist(),qd=qd.tolist(),tool_pose=tool.tolist(),minimum_target_aabb_gap_m=gap,minimum_blade_board_height_m=board,mount_position_error_m=mount_error,mount_angle_error_rad=angle,maximum_joint_speed_rad_s=speed,right_tracking_error_rad=tracking,maximum_rigid_contact_force_n=peak,episode_physx_steps=self.episode_steps,total_matched_physx_steps=self.steps)
  if not np.isfinite(poses).all()or not np.isfinite(qd).all()or gap<=.015 or board<=.004 or mount_error>2e-5 or angle>2e-4 or speed>3. or tracking>.03 or peak>.1 or r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError(('Parked robot exceeded inherited scene gates',row))
  if int(self.sim._physics_step_count)!=self.initial_count+self.setup_steps+self.steps:raise ValueError('Actual PhysX clock count mismatch')
  return row
 def close(self):self.sim.stop();sim_utils.SimulationContext.clear_instance()
