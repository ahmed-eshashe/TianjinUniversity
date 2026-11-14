"""Actual-native-joint-state precision interface for mounted contact.

PhysX owns every joint state and receives one transported COM wrench. The
contact surface uses float64 FK of measured native q, never a target pose.
Raw native link/COM poses and velocities remain available and bounded against
the reconstructed geometry. Import only after AppLauncher.
"""
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_moving_contact_robot import MovingContactRobot
from tomato_contact_robot_v04 import ContactRobotV04
from tomato_exported_robot import ExportedRobot
from tomato_wrench_frame_reference import shift_wrench,shift_twist

class JointStateContactRobot(MovingContactRobot):
    def __init__(self,out,plan,dt,q_right):
        self.precision_kinematics=None
        super().__init__(out,plan,dt,q_right)
        self.precision_kinematics=ExportedRobot(plan['actual_q_kinematic_snapshot'])

    def read(self):
        state=super().read()
        if self.precision_kinematics is None:return state
        fk=self.precision_kinematics
        K=fk.forward(dict(zip(self.robot.joint_names,state['q'])))[fk.tool]
        native_pose=state['tool_pose'].copy();native_velocity=state['tool_velocity'].copy();native_jacobian=state['tool_jacobian'].copy()
        com=self.robot.data.body_com_pose_b.torch[0,self.tool,:3].cpu().numpy().astype(float)
        cp=K[:3,3]+K[:3,:3]@com;cn=state['body_com_pose'][self.tool,:3].copy()
        position_gap=float(np.linalg.norm(K[:3,3]-native_pose[:3]));rotation_gap=float(Rotation.from_matrix(K[:3,:3]@Rotation.from_quat(native_pose[3:]).as_matrix().T).magnitude())
        if position_gap>1e-6 or rotation_gap>1e-5:raise ValueError(('Actual-q kinematics exceeded registered native geometry discrepancy bound',position_gap,rotation_gap))
        pose=np.r_[K[:3,3],Rotation.from_matrix(K[:3,:3]).as_quat()]
        J=native_jacobian.copy();J[:3]+=np.cross(native_jacobian[3:].T,cp-cn).T
        state.update(tool_pose=pose,tool_velocity=shift_twist(native_velocity,cn,cp),tool_jacobian=J,native_tool_pose=native_pose,native_tool_velocity=native_velocity,native_tool_jacobian=native_jacobian,native_tool_com_world=cn,kinematic_tool_com_world=cp,kinematic_tool_matrix=K,native_kinematic_position_gap_m=position_gap,native_kinematic_rotation_gap_rad=rotation_gap,tool_pose_source='Float64 authored-frame FK of all measured ACTUAL native joint positions, with recentered right-joint coordinates. No prescribed/commanded pose.')
        return state

    def advance_contact(self,wrench,feedback,before):
        requested=np.asarray(wrench,dtype=float)
        native=shift_wrench(requested,before['kinematic_tool_com_world'],before['native_tool_com_world'])
        if np.linalg.norm(native[:3])>.01 or np.linalg.norm(native[3:])>.0002:raise ValueError('Transported native contact wrench exceeds original physical force/moment ceiling')
        after,audit=ContactRobotV04.advance_contact(self,native,feedback,before)
        applied=native.astype(np.float32).astype(float)if feedback else np.zeros(6)
        work=float(self.dt*applied@(.5*(before['native_tool_velocity']+after['native_tool_velocity'])))
        equivalent_proxy=shift_wrench(applied,before['native_tool_com_world'],before['kinematic_tool_com_world'])
        virtual_power_error=float(abs(native@before['native_tool_velocity']-requested@before['tool_velocity']))
        generalized_error=float(abs(before['native_tool_jacobian'].T@native-before['tool_jacobian'].T@requested).max())
        if max(virtual_power_error,generalized_error)>1e-12:raise ValueError('Wrench/twist/Jacobian origin transport breaks virtual work')
        audit.update(requested_kinematic_COM_wrench_n_nm=requested.tolist(),requested_native_COM_wrench_n_nm=native.tolist(),actual_float32_applied_wrench=applied.tolist(),actual_applied_wrench_at_kinematic_COM=equivalent_proxy.tolist(),kinematic_to_native_COM_offset_world_m=(before['kinematic_tool_com_world']-before['native_tool_com_world']).tolist(),instantaneous_origin_virtual_power_error_w=virtual_power_error,generalized_origin_transport_error_nm=generalized_error,actual_applied_contact_work_velocity_midpoint_j=work,robot_energy_work_residual_j=after['kinetic_energy_j']-before['kinetic_energy_j']-audit['gravity_work_j']-audit['actuator_work_j']-work)
        return after,audit
