import argparse
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": True})

import torch
import omni.isaac.core.utils.stage as stage_utils
from omni.isaac.core import World
from omni.isaac.core.articulations import ArticulationView

class TomatoCuttingEnv:
    def __init__(self):
        self.world = World(stage_units_in_meters=1.0)
        
        # Load the dual arm robot
        self.usd_path = "/home/omen/teamwork_projects/tomato_cutting_right_arm/assets/robots/dual_ar5_o6/dual_ar5_o6.usd"
        stage_utils.add_reference_to_stage(self.usd_path, "/World/Robot")
        
        self.robot_view = ArticulationView(prim_paths_expr="/World/Robot*", name="robot_view")
        self.world.scene.add(self.robot_view)
        
        self.world.reset()
        
        # We need to initialize the view before applying gains
        if not self.robot_view.is_initialized:
            self.robot_view.initialize()
            
        # Set gains (stiffness/damping)
        num_dofs = self.robot_view.num_dof
        stiffness = 1e4 * torch.ones(num_dofs, dtype=torch.float32)
        damping = 1e3 * torch.ones(num_dofs, dtype=torch.float32)
        self.robot_view.set_gains(kps=stiffness, kds=damping)
        
        self.num_envs = 1
        self.num_actions = num_dofs
        self.num_observations = num_dofs * 2
        
    def reset(self):
        self.world.reset()
        return torch.zeros((self.num_envs, self.num_observations))
        
    def step(self, actions):
        # Apply actions
        self.robot_view.set_joint_position_targets(actions)
        self.world.step(render=False)
        
        # Dummy observations
        obs = torch.zeros((self.num_envs, self.num_observations))
        
        # Dummy reward
        rew = torch.ones(self.num_envs)
        
        # Dummy done
        done = torch.zeros(self.num_envs, dtype=torch.bool)
        info = {}
        
        return obs, rew, done, info

if __name__ == "__main__":
    env = TomatoCuttingEnv()
    obs = env.reset()
    
    print("Starting simulation loop...")
    for i in range(100):
        # Sample random actions
        actions = torch.randn((env.num_envs, env.num_actions)) * 0.1
        obs, rew, done, info = env.step(actions)
        if (i + 1) % 10 == 0:
            print(f"Step {i+1}/100 completed.")
            
    print("Simulation completed successfully.")
    simulation_app.close()
