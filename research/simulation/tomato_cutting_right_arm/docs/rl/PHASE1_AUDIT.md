# Phase 1 robot interface and software audit

Date: 19 October 2026. Scope: simulation/software inventory and physical-interface requirements. No physical robot was connected or commanded.

## Outcome

The model has 36 revolute coordinates in total. The right side has 7 arm actuators and 6 independent hand actuators, plus 5 passive mimic followers. The installed CUDA build successfully executed a matrix operation on the RTX 5060 Laptop GPU. No package installation or environment upgrade was performed.

This completes the accessible model/software audit. Physical feedback, calibrated command conversion, real torque/speed limits, firmware, and tactile configuration remain open deployment requirements. The user's confirmation that the physical robot uses the same models does not verify those interfaces.

## Installed stack

- isaacsim: 6.1.0.0
- isaacsim-core: 6.1.0.0
- isaaclab: 19.0.0
- isaaclab-rl: 1.0.0
- torch: 2.12.0+cu130
- torchvision: 0.27.0+cu130
- numpy: 2.3.1
- gymnasium: 1.3.0
- rsl-rl-lib: 5.5.1
- rl-games: 1.6.1
- skrl: 2.1.0
- stable-baselines3: 2.9.0
- python: 3.12.14 | packaged by Anaconda, Inc. | (main, Aug 27 2026, 14:46:43) [GCC 14.3.0]
- cuda_build: 13.0
- cuda_available: True
- gpu: NVIDIA GeForce RTX 5060 Laptop GPU
- torch_architectures: ['sm_75', 'sm_80', 'sm_86', 'sm_90', 'sm_100', 'sm_120']
- isaaclab_source_VERSION: 3.0.0
- isaaclab_source_commit: 75e9c8ce12b27ecc5dc17a3de822e39cc6506d80

The Python distribution reports Isaac Lab 19.0.0 while the editable source VERSION file reports 3.0.0. Both are recorded with the exact source commit. Do not infer compatibility from either label alone. Phase 2 exercises Isaac Sim Core, PhysX, PyTorch and camera APIs; a future native Isaac Lab DirectRLEnv remains a distinct integration check.

## Dependency consistency findings

`dependency_check.txt` records the read-only package check. It reports missing torchaudio and version mismatches involving torch, torchvision, psutil, click, llvmlite, mujoco, mujoco-warp and newton. The installed Core/PhysX/PyTorch probe has run successfully, but these mismatches prevent claiming complete supported-stack compatibility. No packages were installed, removed or upgraded. Native Isaac Lab and its selected RL adapter require a targeted integration check before full training; unused-backend dependency conflicts must be assessed separately rather than repaired blindly.

## Joint inventory

Limits below are authored simulation limits in radians, not certified hardware limits. The full left/right inventory, body paths, drives, URDF declarations and mimic attributes are in `phase1_inventory.json`.

| Joint | Simulation limits in radians | Role |
| --- | --- | --- |
| right_AR5_5_07R_W4C4A2_joint_1 | -3.106700 to 3.106700 | Independent target |
| right_AR5_5_07R_W4C4A2_joint_2 | -2.094400 to 2.094400 | Independent target |
| right_AR5_5_07R_W4C4A2_joint_3 | -3.106700 to 3.106700 | Independent target |
| right_AR5_5_07R_W4C4A2_joint_4 | -1.047200 to 2.530700 | Independent target |
| right_AR5_5_07R_W4C4A2_joint_5 | -3.106700 to 3.106700 | Independent target |
| right_AR5_5_07R_W4C4A2_joint_6 | -1.047200 to 1.047200 | Independent target |
| right_AR5_5_07R_W4C4A2_joint_7 | -1.047200 to 1.047200 | Independent target |
| right_rh_thumb_cmc_yaw | 0.000000 to 1.360000 | Independent target |
| right_rh_thumb_cmc_pitch | 0.000000 to 0.580000 | Independent target |
| right_rh_thumb_ip | 0.000000 to 1.080000 | Passive follower |
| right_rh_index_mcp_pitch | 0.000000 to 1.600000 | Independent target |
| right_rh_index_dip | 0.000000 to 1.430000 | Passive follower |
| right_rh_middle_mcp_pitch | 0.000000 to 1.600000 | Independent target |
| right_rh_middle_dip | 0.000000 to 1.430000 | Passive follower |
| right_rh_ring_mcp_pitch | 0.000000 to 1.600000 | Independent target |
| right_rh_ring_dip | 0.000000 to 1.430000 | Passive follower |
| right_rh_pinky_mcp_pitch | 0.000000 to 1.600000 | Independent target |
| right_rh_pinky_dip | 0.000000 to 1.430000 | Passive follower |

Finger DIP followers use q_DIP = 0.89 q_MCP. Thumb IP uses q_IP = 1.86 q_CMC_pitch. These are authored mimic coefficients; Phase 2 records their physical simulation residuals. Followers must not become independent policy outputs.

The USD simulation drives include max-force values of 1000 for arms and 10 for hand joints in the prepared reference. The URDF contains other effort declarations, such as 108 for an arm joint and 100 for hand joints. These are model/control configuration values and are not interchangeable with measured available motor torque. The benchmark explicitly uses provisional lower simulation drive caps and does not claim hardware calibration.

## Observation and action contract

`interface_contract.json` defines units, frames, proposed rates, action ordering, limits and exclusions. The task proposal is 6 bounded palm increments plus 6 hand commands at 20 Hz, with 240 Hz physics initially. The resource benchmark instead uses 13 small independent-joint offsets around a fixed ready posture. That benchmark action space does not implement a grasp planner or the final RL task.

The initial actor uses RGB-D perception, joint position/velocity and controller history. Joint-state inputs are available in simulation and conditional on verified physical feedback for deployment. Ground-truth knife pose and simulated contact identities/forces may be used by a teacher, reward, evaluator or privileged critic, but are excluded from the deployed actor. Tactile, wrench, motor-current and torque signals are excluded until confirmed and calibrated.

## Physical interface findings and open items

No sensor prims were found in the authored robot subtree. This describes the USD, not the real hardware. No evidence confirms the installed robot's tactile option or a live tactile data stream.

The [vendor Python SDK](https://github.com/linker-bot/linkerhand-python-sdk) documents the O6 six-channel order as thumb flexion, thumb opposition, index, middle, ring and pinky. The authored USD lists yaw before pitch, so index-based copying would swap thumb channels. Use named mapping and verify signs, ranges and physical zero before deployment.

The [vendor ROS 2 SDK](https://github.com/linker-bot/linkerhand-ros2-sdk) exposes an O6 tactile configuration option. Its existence does not establish that this user's hand has that option. No driver installation, CAN setup, sensor probing or hardware movement was attempted.

A neighbouring ROS configuration, `/home/omen/rokae_ws/src/rokae_moveit_config/config/ros2_controllers.yaml`, declares position commands and position/velocity state for seven **left-arm** joints at 100 Hz, plus a single left index joint as a gripper. That is configuration evidence only, not a verified live interface, and it does not provide the required right-arm/six-channel-hand mapping. The project's URDF also contains legacy effort-interface declarations. These cannot be treated as proof of available torque control or tactile feedback.

Before hardware operation, confirm:

- Arm controller/API model, firmware and joint-feedback interface.
- Hand serial/firmware, communication transport and configured sensor variant.
- Encoder/velocity signal ordering, units, timestamps and calibrated zero.
- Thumb channel order and mimic/physical coupling.
- Actual torque/speed/position limits and meaning of any current or torque estimates.
- Camera mount, intrinsics and robot-to-camera calibration.
- Stop behaviour and stale/missing input handling.

## Baseline preservation

The original robot USD and accepted baseline launcher/configuration/reports are hashed in `phase1_inventory.json`. RL benchmark files are separate. Recheck those hashes at the end of Phase 2. Recent closer-grip experiments remain unvalidated and are not training evidence.
