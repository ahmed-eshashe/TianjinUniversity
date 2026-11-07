"""Separate PGS numerical experiment; original physical robot stays intact."""
import torch
from tomato_parked_robot_pgs import ParkedRobotPGS
from tomato_moving_contact_robot import MovingContactRobot
from tomato_joint_state_contact_robot import JointStateContactRobot
from tomato_exported_robot import ExportedRobot

class MovingContactRobotPGS(MovingContactRobot):
    def __init__(self,out,plan,dt,q_right):
        ParkedRobotPGS.__init__(self,out,plan,dt)
        self.contact_home=self.home.clone();self.contact_home[:,self.ids]=torch.tensor([q_right],dtype=torch.float32);self.force_steps=0
        zero=torch.zeros_like(self.home);self.robot.write_joint_stiffness_to_sim_index(stiffness=zero);self.robot.write_joint_damping_to_sim_index(damping=zero)

class JointStateContactRobotPGS(JointStateContactRobot):
    def __init__(self,out,plan,dt,q_right):
        self.precision_kinematics=None
        MovingContactRobotPGS.__init__(self,out,plan,dt,q_right)
        self.precision_kinematics=ExportedRobot(plan['actual_q_kinematic_snapshot'])
