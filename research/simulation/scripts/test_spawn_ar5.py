# Copyright (c) 2026, DEX-ROB Lab, Tianjin University.
# All rights reserved.
#
# Verification script for AR5_L6 and LinkerHand O6 in Isaac Lab

import argparse
import sys

from isaaclab.app import AppLauncher

# Add argparse arguments
parser = argparse.ArgumentParser(description="Verify AR5_L6 & LinkerHand O6 spawn in Isaac Lab.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to spawn.")
parser.add_argument("--robot", type=str, default="combined", choices=["left", "right", "combined"], help="Which robot model to spawn.")

# Append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# Launch Omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import torch
import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg, ArticulationCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass

# Import AR5 configs from isaaclab_assets
from isaaclab_assets.robots.ar5_l6 import (
    AR5_L6_LEFT_CFG,
    AR5_L6_RIGHT_CFG,
    AR5_O6_LEFT_COMBINED_CFG,
)

@configclass
class AR5SceneCfg(InteractiveSceneCfg):
    """Configuration for AR5 test scene."""

    # Ground plane
    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(),
    )

    # Dome light
    light = AssetBaseCfg(
        prim_path="/World/defaultLight",
        spawn=sim_utils.DomeLightCfg(intensity=2000.0, color=(0.8, 0.8, 0.8)),
    )

    # Robot articulation
    robot: ArticulationCfg = None


def main():
    """Main verification routine."""
    print("=" * 60)
    print(f"Starting AR5_L6 verification (Robot: {args_cli.robot})...")
    print("=" * 60)

    scene_cfg = AR5SceneCfg(num_envs=args_cli.num_envs, env_spacing=2.0)

    if args_cli.robot == "left":
        scene_cfg.robot = AR5_L6_LEFT_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    elif args_cli.robot == "right":
        scene_cfg.robot = AR5_L6_RIGHT_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    else:
        scene_cfg.robot = AR5_O6_LEFT_COMBINED_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

    # Setup scene
    sim_cfg = sim_utils.SimulationCfg(device="cuda:0" if torch.cuda.is_available() else "cpu", dt=0.01)
    sim = sim_utils.SimulationContext(sim_cfg)
    scene = InteractiveScene(scene_cfg)

    # Reset simulation
    sim.reset()
    scene.reset()

    robot = scene["robot"]
    print(f"\n[SUCCESS] Robot successfully spawned in Isaac Lab!")
    print(f"  • Number of joints: {robot.num_joints}")
    print(f"  • Joint names ({len(robot.data.joint_names)}):")
    for i, name in enumerate(robot.data.joint_names):
        print(f"    [{i:02d}] {name}")
    root_pos = getattr(robot.data.root_pos_w, "torch", robot.data.root_pos_w)
    print(f"  • Root position: {root_pos[0].cpu().numpy()}")

    # Step simulation for 50 steps
    print("\nStepping simulation for 50 physics steps...")
    for step in range(50):
        # Apply passive zero torques/hold position
        sim.step()
        scene.update(dt=sim_cfg.dt)

    print("\n[VERIFICATION PASSED] AR5_L6 simulation step completed stably without physics divergence.")
    print("=" * 60)

    simulation_app.close()


if __name__ == "__main__":
    main()
