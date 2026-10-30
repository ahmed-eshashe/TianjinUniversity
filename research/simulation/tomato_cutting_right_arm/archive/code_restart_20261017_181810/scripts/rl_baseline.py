import argparse
import sys
import os
import numpy as np

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

from omni.isaac.core import World
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.types import ArticulationAction
import omni.isaac.core.utils.stage as stage_utils
from omni.isaac.core.utils.prims import define_prim

def main():
    print("Initializing World...")
    world = World(stage_units_in_meters=1.0)
    world.scene.add_default_ground_plane()

    usd_path = "/home/omen/teamwork_projects/tomato_cutting_right_arm/assets/robots/dual_ar5_o6/dual_ar5_o6.usd"
    robot_prim_path = "/World/Robot"
    
    print(f"Adding reference to {usd_path} at {robot_prim_path}...")
    # define_prim(robot_prim_path, "Xform")
    stage_utils.add_reference_to_stage(usd_path, robot_prim_path)
    
    print("Setting up Articulation...")
    # Usually URDF imports root at the referenced prim or inside it. Let's assume the root is at the prim path.
    robot = world.scene.add(
        Articulation(
            prim_path=f"{robot_prim_path}/base_link",
            name="dual_ar5_o6"
        )
    )

    print("Resetting world (starts physics)...")
    world.reset()
    
    print("Starting simulation loop...")
    for i in range(100):
        # Setup dummy continuous control MDP actions
        num_dofs = robot.num_dof
        if num_dofs > 0:
            # dummy action: slight random targets
            random_actions = np.random.uniform(-0.1, 0.1, size=(num_dofs,))
            robot.apply_action(ArticulationAction(joint_positions=random_actions))
        
        # Step simulation
        world.step(render=False)
        
        # Dummy observation
        if num_dofs > 0:
            obs = robot.get_joint_positions()
        # Dummy reward
        reward = 0.0
        
        if i % 10 == 0:
            print(f"Step {i}: executed random actions. Num DOFs: {num_dofs}")

    print("Successfully completed 100 steps.")
    simulation_app.close()

if __name__ == "__main__":
    main()
