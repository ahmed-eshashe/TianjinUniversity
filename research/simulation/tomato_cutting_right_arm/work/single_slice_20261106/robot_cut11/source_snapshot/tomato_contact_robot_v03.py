"""Short actual-robot force-feedback diagnostic, explicit gravity effort only.

The candidate contact configuration is an assigned initial condition, not an
executed approach. All implicit gains are zero in this new experiment, so
the known effort is gravity feedforward, checked against its existing limits.
No trajectory tracking, grasp or cutting claim is made.
"""
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from tomato_parked_robot import ParkedRobot
from tomato_robot_energy_link_reference import body_sum_reference,kinetic_energy

class ContactRobotV03(ParkedRobot):
 def __init__(self,out,plan,dt,q_right):
  super().__init__(out,plan,dt);self.contact_home=self.home.clone();self.contact_home[:,self.ids]=torch.tensor([q_right],dtype=torch.float32);self.force_steps=0
  zero=torch.zeros_like(self.home);self.robot.write_joint_stiffness_to_sim_index(stiffness=zero);self.robot.write_joint_damping_to_sim_index(damping=zero)
 def reset_contact(self):
  r=self.robot;r.reset();r.write_joint_state_to_sim_index(position=self.contact_home,velocity=torch.zeros_like(self.contact_home));r.set_joint_effort_target_index(target=torch.zeros_like(self.contact_home));r.write_data_to_sim();r.update(self.dt);self.episode_steps=0
  if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active or float(r.data.joint_vel.torch.abs().max())!=0:raise ValueError('Contact robot reset/queue failed')
 def read(self):
  r=self.robot
  def get(name):return getattr(r.data,name).torch[0].cpu().numpy().astype(float).copy()
  mass=get('body_mass');inertia=get('body_inertia').reshape(-1,3,3);pose=get('body_com_pose_w');link=get('body_link_pose_w');R=Rotation.from_quat(link[:,3:]).as_matrix();jac=get('body_com_jacobian_w');J=np.zeros((len(mass),6,r.num_joints));J[1:]=jac;armature=get('joint_armature');ref=body_sum_reference(mass,inertia,R,J,armature);v=get('body_com_vel_w');qd=get('joint_vel');link=get('body_link_pose_w');g=get('gravity_compensation_forces');M=get('mass_matrix');energy=kinetic_energy(mass,ref['inertia_world'],v,armature,qd)
  if np.max(abs(g-ref['gravity_compensation']))>1e-4+2e-5*np.max(abs(g))or np.max(abs(M-ref['body_mass_matrix']))>1e-5+2e-5*np.max(abs(M)):raise ValueError('Actual robot mass/gravity reference mismatch')
  return dict(q=get('joint_pos'),qd=qd,tool_pose=link[self.tool],tool_velocity=v[self.tool],body_com_velocity=v,body_com_pose=pose,body_link_pose=link,mass=mass,gravity=g,mass_matrix=M,tool_jacobian=J[self.tool],kinetic_energy_j=energy,kinetic_energy_mass_matrix_j=float(.5*qd@(M+np.diag(armature))@qd),native_mass_query_scope='body only; unchanged rotor inertia separately included in kinetic energy')
 def advance_contact(self,wrench,feedback,before):
  r=self.robot;wrench=np.asarray(wrench,dtype=float);tau=before['gravity'];limit=r.data.joint_effort_limits.torch[0].cpu().numpy()
  if np.any(abs(tau)>limit+1e-6):raise ValueError('Gravity effort exceeds existing joint effort limit')
  if feedback:r.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor(wrench[:3][None,None],dtype=torch.float32),torques=torch.tensor(wrench[3:][None,None],dtype=torch.float32),positions=None,body_ids=[self.tool],is_global=True)
  r.set_joint_effort_target_index(target=torch.tensor(tau[None],dtype=torch.float32));r.write_data_to_sim();self.sim.step(render=False);r.update(self.dt);self.steps+=1;self.episode_steps+=1;self.force_steps+=int(feedback)
  if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError('Contact wrench queue not consumed exactly once')
  after=self.read();midqd=.5*(before['qd']+after['qd']);midv=.5*(before['body_com_velocity']+after['body_com_velocity']);gravity_work=float(self.dt*np.sum(-9.81*before['mass']*midv[:,2]));effort_work=float(self.dt*tau@midqd);contact_work=float(self.dt*wrench@(.5*(before['tool_velocity']+after['tool_velocity'])))if feedback else 0.;contact=float(np.linalg.norm(self.contacts(),axis=-1).max(initial=0.))
  if contact>.1 or np.max(abs(after['qd']))>3. or not np.isfinite(after['body_link_pose']).all():raise ValueError('Actual contact robot exceeded inherited rigid contact/speed gate')
  if int(self.sim._physics_step_count)!=self.initial_count+self.steps:raise ValueError('Actual contact robot clock mismatch')
  return after,dict(commanded_effort_nm=tau.tolist(),gravity_work_j=gravity_work,actuator_work_j=effort_work,actual_applied_contact_work_velocity_midpoint_j=contact_work,robot_energy_work_residual_j=after['kinetic_energy_j']-before['kinetic_energy_j']-gravity_work-effort_work-contact_work,maximum_forbidden_rigid_force_n=contact,episode_physx_steps=self.episode_steps,total_physx_steps=self.steps)
