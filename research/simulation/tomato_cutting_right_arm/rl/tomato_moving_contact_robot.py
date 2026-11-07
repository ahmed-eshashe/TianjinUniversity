"""Bounded initial-velocity contact fixture; actual PhysX owns every pose.

This is a coasting nonfracturing diagnostic, not a tracking controller or an
executed approach. Native gravity effort and all physical motor limits are
inherited unchanged. Import behind AppLauncher.
"""
import numpy as np
import torch
from tomato_contact_robot_v04 import ContactRobotV04


class MovingContactRobot(ContactRobotV04):
    def configure_initial_velocity(self, qd, expected_twist):
        self.initial_qd = np.asarray(qd, dtype=np.float32).astype(float)
        self.expected_initial_twist = np.asarray(expected_twist, dtype=float)
        if self.initial_qd.shape != (36,) or not np.isfinite(self.initial_qd).all() or abs(self.initial_qd).max() > .01:
            raise ValueError('Bounded native initial velocity required')
        if np.any(self.initial_qd[[i for i in range(36) if i not in self.ids]]):
            raise ValueError('Only the right seven arm joints may have initial velocity')

    def reset_moving_contact(self):
        self.reset_contact()
        r = self.robot
        r.write_joint_state_to_sim_index(position=self.contact_home, velocity=torch.tensor(self.initial_qd[None], dtype=torch.float32))
        r.write_data_to_sim()
        r.update(self.dt)
        state = self.read()
        expected = state['tool_jacobian'] @ self.initial_qd
        if not np.array_equal(state['qd'], self.initial_qd) or np.max(abs(expected-self.expected_initial_twist)) > 1e-7:
            raise ValueError('Initial native joint velocity/Jacobian provenance failed')
        if np.max(abs(state['tool_velocity']-expected)) > 1e-7:
            raise ValueError(('Native initial link velocity does not match written joints', state['tool_velocity'], expected))
        if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:
            raise ValueError('Moving fixture reset retained a wrench')
        return state

    def advance_contact(self, wrench, feedback, before):
        after, audit = super().advance_contact(wrench, feedback, before)
        applied = np.asarray(wrench, dtype=np.float32).astype(float) if feedback else np.zeros(6)
        work = float(self.dt * applied @ (.5 * (before['tool_velocity']+after['tool_velocity'])))
        audit['requested_double_wrench_contact_work_j'] = audit['actual_applied_contact_work_velocity_midpoint_j']
        audit['actual_applied_contact_work_velocity_midpoint_j'] = work
        audit['robot_energy_work_residual_j'] = after['kinetic_energy_j']-before['kinetic_energy_j']-audit['gravity_work_j']-audit['actuator_work_j']-work
        audit['actual_float32_applied_wrench'] = applied.tolist()
        return after, audit
