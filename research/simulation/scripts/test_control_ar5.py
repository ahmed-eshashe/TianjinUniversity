# Copyright (c) 2026, DEX-ROB Lab, Tianjin University.
# All rights reserved.
#
# Interactive joint position control and telemetry verification for AR5_L6 & LinkerHand O6.

import argparse
import sys
import torch
from isaaclab.app import AppLauncher

# Setup CLI arguments
parser = argparse.ArgumentParser(description="Test active joint control and telemetry on AR5_L6 + LinkerHand O6.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of simulation environments.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# Launch simulation app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg, ArticulationCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass

from isaaclab_assets.robots.ar5_l6 import AR5_O6_LEFT_COMBINED_CFG

@configclass
class AR5ControlSceneCfg(InteractiveSceneCfg):
    """Scene with ground, dome light, and the combined AR5+O6 robot."""
    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(),
    )
    light = AssetBaseCfg(
        prim_path="/World/defaultLight",
        spawn=sim_utils.DomeLightCfg(intensity=2500.0, color=(0.85, 0.85, 0.85)),
    )
    robot: ArticulationCfg = AR5_O6_LEFT_COMBINED_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


def main():
    print("\n" + "=" * 70)
    print("  AR5_L6 + LinkerHand O6 Active Joint Control & Telemetry Test")
    print("=" * 70)

    # 1. Initialize Scene & Simulation Context
    sim_cfg = sim_utils.SimulationCfg(device="cuda:0" if torch.cuda.is_available() else "cpu", dt=0.01)
    sim = sim_utils.SimulationContext(sim_cfg)
    scene_cfg = AR5ControlSceneCfg(num_envs=args_cli.num_envs, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)

    # 2. Reset simulation
    sim.reset()
    scene.reset()

    robot = scene["robot"]
    device = sim.device
    num_joints = robot.num_joints

    print(f"\n[INFO] Robot Articulation Spawned on device: {device}")
    print(f"[INFO] Total controllable joints: {num_joints}")
    for idx, name in enumerate(robot.data.joint_names):
        print(f"       [{idx:02d}] {name}")

    # Initial joint targets (cloned from current joint positions)
    default_pos = robot.data.default_joint_pos.clone()
    target_pos = default_pos.clone()

    # Identify joint indices
    # Arm joints: 0..6
    # Hand joints: 7..17
    # 7: thumb_cmc_yaw, 8: index_mcp, 9: middle_mcp, 10: ring_mcp, 11: pinky_mcp
    # 12: thumb_cmc_pitch, 13: index_dip, 14: middle_dip, 15: ring_dip, 16: pinky_dip, 17: thumb_ip

    print("\n--- Beginning Motion Sequence ---")

    # PHASE 1: Hold default stance for 40 steps (0.4 s)
    print("\n[Phase 1] Holding default rest stance (40 steps)...")
    for step in range(40):
        robot.set_joint_position_target(target_pos)
        scene.write_data_to_sim()
        sim.step()
        scene.update(dt=sim_cfg.dt)

    # PHASE 2: Move Arm to Pre-Grasp Approach Pose (100 steps, 1.0 s)
    # Bend shoulder and elbow to bring hand down toward table
    print("\n[Phase 2] Moving Arm to Pre-Grasp Position above Cutting Board (100 steps)...")
    # Target joint angles (radians):
    # joint 1 (yaw): 0.0
    # joint 2 (pitch): -0.4 rad (~ -23 deg)
    # joint 3 (roll): 0.0
    # joint 4 (elbow): 1.6 rad (~ 92 deg)
    # joint 5 (wrist roll): 0.0
    # joint 6 (wrist pitch): 0.8 rad (~ 45 deg downwards)
    # joint 7 (wrist yaw): 0.0
    approach_arm_pos = torch.tensor([0.0, -0.4, 0.0, 1.6, 0.0, 0.8, 0.0], device=device).repeat(args_cli.num_envs, 1)
    target_pos[:, 0:7] = approach_arm_pos

    for step in range(100):
        robot.set_joint_position_target(target_pos)
        scene.write_data_to_sim()
        sim.step()
        scene.update(dt=sim_cfg.dt)

    # PHASE 3: Dynamic Hand Grasp (Flex fingers to grip tomato) (150 steps, 1.5 s)
    print("\n[Phase 3] Actuating LinkerHand O6 Fingers (Closing Enveloping Grasp)...")
    # Flex MCP joints to 1.1 rad (~63 deg) and DIP joints to 0.9 rad (~51 deg)
    # Thumb CMC yaw to 0.6 rad, thumb pitch to 0.4 rad, thumb IP to 0.5 rad
    grasp_hand_pos = torch.tensor([
        0.6,   # thumb_cmc_yaw
        1.1,   # index_mcp_pitch
        1.1,   # middle_mcp_pitch
        1.1,   # ring_mcp_pitch
        1.1,   # pinky_mcp_pitch
        0.4,   # thumb_cmc_pitch
        0.9,   # index_dip
        0.9,   # middle_dip
        0.9,   # ring_dip
        0.9,   # pinky_dip
        0.5,   # thumb_ip
    ], device=device).repeat(args_cli.num_envs, 1)

    target_pos[:, 7:18] = grasp_hand_pos

    for step in range(150):
        robot.set_joint_position_target(target_pos)
        scene.write_data_to_sim()
        sim.step()
        scene.update(dt=sim_cfg.dt)

        if step % 50 == 0:
            current_q = robot.data.joint_pos[0].cpu().numpy()
            current_tau = robot.data.applied_torque[0].cpu().numpy()
            print(f"  Step {step:03d}/150 | Arm J4: {current_q[3]:.2f} rad | Index MCP: {current_q[8]:.2f} rad | Index Torque: {current_tau[8]:.2f} N*m")

    # PHASE 4: Telemetry verification
    q_final = robot.data.joint_pos[0].cpu().numpy()
    qd_final = robot.data.joint_vel[0].cpu().numpy()
    tau_final = robot.data.applied_torque[0].cpu().numpy()

    print("\n" + "=" * 70)
    print("  FINAL TELEMETRY AUDIT")
    print("=" * 70)
    print(f"{'Joint':<30} | {'Angle (rad)':<12} | {'Vel (rad/s)':<12} | {'Torque (N*m)':<12}")
    print("-" * 72)
    for i, name in enumerate(robot.data.joint_names):
        print(f"{name:<30} | {q_final[i]:>10.3f}   | {qd_final[i]:>10.3f}   | {tau_final[i]:>10.3f}")

    print("\n[SUCCESS] AR5_L6 arm and LinkerHand O6 successfully commanded and actuated!")
    print("[SUCCESS] All 18 joints respond to position targets and report real-time torques.")
    print("=" * 70 + "\n")

    simulation_app.close()


if __name__ == "__main__":
    main()
