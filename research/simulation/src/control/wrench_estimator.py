#!/usr/bin/env python3
"""
1 kHz Proprioceptive Contact Wrench Estimator & Anti-Crush Monitor
DEX-ROB Lab | School of Electrical & Automation Engineering, Tianjin University
Author: Ahmed (Holding Arm & Sim-to-Real Control) | Research Lead Agent

Reconstructs external Cartesian contact forces F_ext from measured joint torques tau_ext
via the pseudo-inverse of the manipulator Jacobian transpose:
    F_ext = (J^T(q))^\dagger \tau_ext

Includes:
- Online 1st-order Butterworth low-pass filtering (fc = 50 Hz @ 1 kHz).
- Soft food safety regime classification (Under-grasp slip, Safe hold, Crush barrier, E-stop).
- Integration test with synthetic interaction torques.
"""

from enum import Enum
from typing import Tuple, Optional, Union
import numpy as np
import torch
import os
import sys
from pathlib import Path

# Add project root to sys.path for standalone execution
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from research.simulation.src.kinematics.ar5_kinematics import AR5Kinematics


class GraspRegime(Enum):
    UNDER_GRASP_SLIP = "UNDER_GRASP_SLIP"      # F < 1.5 N: Risk of tomato sliding
    NOMINAL_SAFE_HOLD = "NOMINAL_SAFE_HOLD"    # 1.5 N <= F <= 5.0 N: Optimal non-destructive hold
    CRUSH_BARRIER_VIOLATION = "CRUSH_BARRIER"  # 5.0 N < F <= 15.0 N: Flesh bruising / pulp rupture
    EMERGENCY_OVERLOAD = "EMERGENCY_STOP"      # F > 15.0 N: Hardware damage threshold


class ProprioceptiveWrenchEstimator:
    """
    High-rate (1 kHz) contact wrench estimator leveraging ARX AR5-L6 joint torques.
    Eliminates fragile custom tactile sensor fabrication per Prof. Shan An's directive.
    """

    # Physical thresholds for standard commercial tomatoes (Newtons)
    F_MIN_SLIP = 1.5      # Minimum holding force to resist lateral sawing shear
    F_MAX_CRUSH = 5.0     # Maximum allowable compressive force before irreversible cell damage
    F_ESTOP = 15.0        # Emergency hardware trip limit

    def __init__(
        self,
        cutoff_freq_hz: float = 50.0,
        sample_rate_hz: float = 1000.0,
        lambda_damping: float = 1e-4,
        device: str = "cpu"
    ):
        self.kin = AR5Kinematics(device=device)
        self.lambda_damping = lambda_damping
        self.device = torch.device(device)

        # 1st-order Low-Pass Butterworth Filter Coefficients
        # H(s) = omega_c / (s + omega_c), discretized via Tustin (bilinear) transform
        omega_c = 2.0 * np.pi * cutoff_freq_hz
        T = 1.0 / sample_rate_hz
        alpha = (2.0 - omega_c * T) / (2.0 + omega_c * T)
        beta = (omega_c * T) / (2.0 + omega_c * T)

        self.alpha = float(alpha)
        self.beta = float(beta)

        # Filter states for 3D force and 3D torque
        self.prev_raw = torch.zeros(6, dtype=torch.float32, device=self.device)
        self.prev_filtered = torch.zeros(6, dtype=torch.float32, device=self.device)
        self._is_initialized = False

    def reset(self):
        """Resets digital filter internal states."""
        self.prev_raw.zero_()
        self.prev_filtered.zero_()
        self._is_initialized = False

    def estimate_wrench(
        self,
        q: Union[np.ndarray, torch.Tensor],
        tau_ext: Union[np.ndarray, torch.Tensor],
        filter_output: bool = True,
        target_frame: str = "hand_base"
    ) -> Tuple[torch.Tensor, GraspRegime]:
        """
        Estimates the 6D external contact wrench W_ext = [Fx, Fy, Fz, Tx, Ty, Tz]^T.
        
        Args:
            q: Current 7-DoF joint angles (rad), shape (7,).
            tau_ext: Measured external joint torques (N*m) after gravity/Coriolis compensation, shape (7,).
            filter_output: Whether to apply the 50 Hz low-pass filter.
            target_frame: "hand_base" (LinkerHand palm) or "tcp".
            
        Returns:
            wrench_ext: 6D contact wrench vector (Fx, Fy, Fz in N, Tx, Ty, Tz in N*m).
            regime: GraspRegime classification for tomato safety monitoring.
        """
        if isinstance(q, np.ndarray):
            q_t = torch.tensor(q, dtype=torch.float32, device=self.device)
        else:
            q_t = q.to(self.device).float()

        if isinstance(tau_ext, np.ndarray):
            tau_t = torch.tensor(tau_ext, dtype=torch.float32, device=self.device)
        else:
            tau_t = tau_ext.to(self.device).float()

        # Compute geometric Jacobian J(q) in R^{6x7}
        J = self.kin.compute_jacobian(q_t, target_frame=target_frame)

        # Wrench reconstruction via transpose pseudo-inverse:
        # tau_ext = J^T * W_ext  =>  W_ext = (J^T)^\dagger * tau_ext
        JT = J.T  # Shape: (7, 6)
        JT_pinv = self.kin.damped_pinv(JT, lambda_damping=self.lambda_damping)  # Shape: (6, 7)
        wrench_raw = JT_pinv @ tau_t  # Shape: (6,)

        if not filter_output:
            wrench = wrench_raw
        else:
            if not self._is_initialized:
                self.prev_raw = wrench_raw.clone()
                self.prev_filtered = wrench_raw.clone()
                self._is_initialized = True
                wrench = wrench_raw
            else:
                # 1st-order bilinear filter: y[k] = alpha * y[k-1] + beta * (u[k] + u[k-1])
                wrench = self.alpha * self.prev_filtered + self.beta * (wrench_raw + self.prev_raw)
                self.prev_raw = wrench_raw.clone()
                self.prev_filtered = wrench.clone()

        # Classify normal contact force magnitude
        f_norm = torch.norm(wrench[0:3]).item()

        if f_norm < self.F_MIN_SLIP:
            regime = GraspRegime.UNDER_GRASP_SLIP
        elif f_norm <= self.F_MAX_CRUSH:
            regime = GraspRegime.NOMINAL_SAFE_HOLD
        elif f_norm <= self.F_ESTOP:
            regime = GraspRegime.CRUSH_BARRIER_VIOLATION
        else:
            regime = GraspRegime.EMERGENCY_OVERLOAD

        return wrench, regime


def self_test_wrench_estimator():
    """Validates force reconstruction accuracy and regime monitoring."""
    print("=" * 60)
    print("1 kHz PROPRIOCEPTIVE CONTACT WRENCH ESTIMATOR SELF-TEST")
    print("=" * 60)

    estimator = ProprioceptiveWrenchEstimator(cutoff_freq_hz=50.0, sample_rate_hz=1000.0)
    q_test = np.array([0.0, 0.4, 0.0, 1.2, 0.0, 0.3, 0.0])

    # 1. Forward model: simulate known external normal contact force F_true = [0, 0, 3.5] N (Safe Hold)
    F_true = torch.tensor([0.0, 0.0, 3.5, 0.0, 0.0, 0.0], dtype=torch.float32)
    J = estimator.kin.compute_jacobian(q_test, target_frame="hand_base")
    tau_simulated = J.T @ F_true  # Ideal sensorless joint torque response

    wrench_est, regime = estimator.estimate_wrench(q_test, tau_simulated, filter_output=False)
    print(f"Applied Test Force:       {F_true[0:3].numpy()} N")
    print(f"Reconstructed Force:      {wrench_est[0:3].numpy().round(4)} N")
    print(f"Regime Classification:    {regime.value}")
    f_err = torch.norm(wrench_est[0:3] - F_true[0:3]).item()
    print(f"Force Reconstruction Error: {f_err:.4e} N")
    assert f_err < 1e-3, f"Force reconstruction error {f_err} too high!"
    assert regime == GraspRegime.NOMINAL_SAFE_HOLD, f"Expected SAFE_HOLD, got {regime}"
    print("Zero-Noise Reconstruction Check: PASSED")

    # 2. Over-grasp Crushing Barrier Test (F = 8.0 N)
    F_crush = torch.tensor([0.0, 0.0, 8.0, 0.0, 0.0, 0.0], dtype=torch.float32)
    tau_crush = J.T @ F_crush
    _, regime_crush = estimator.estimate_wrench(q_test, tau_crush, filter_output=False)
    print(f"\nApplied Crushing Force:   8.0 N")
    print(f"Regime Classification:    {regime_crush.value}")
    assert regime_crush == GraspRegime.CRUSH_BARRIER_VIOLATION
    print("Crushing Barrier Alarm Check: PASSED")

    # 3. Dynamic Filter Attenuation Test (Simulate 1 kHz signal + 200 Hz noise)
    estimator.reset()
    t_steps = 200
    noise_freq = 200.0
    dt = 0.001
    filtered_forces = []
    for step in range(t_steps):
        t = step * dt
        noise = 1.0 * np.sin(2 * np.pi * noise_freq * t)
        F_noisy = F_true.clone()
        F_noisy[2] += noise
        tau_step = J.T @ F_noisy
        w_filt, _ = estimator.estimate_wrench(q_test, tau_step, filter_output=True)
        filtered_forces.append(w_filt[2].item())

    # Check high-frequency noise variance reduction over last 50 steps
    steady_state_std = np.std(filtered_forces[-50:])
    print(f"\nFiltered Force Standard Deviation under 200 Hz Noise: {steady_state_std:.4f} N (Raw: ~0.707 N)")
    assert steady_state_std < 0.25, f"Filter did not sufficiently attenuate noise! std={steady_state_std}"
    print("50 Hz Butterworth Low-Pass Attenuation Check: PASSED")

    print("=" * 60)
    print("ALL PROPRIOCEPTIVE WRENCH ESTIMATION CHECKS PASSED.")
    print("=" * 60)


if __name__ == "__main__":
    self_test_wrench_estimator()
