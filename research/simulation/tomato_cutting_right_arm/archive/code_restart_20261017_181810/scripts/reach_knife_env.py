import argparse
from isaacsim import SimulationApp

# Initialize SimulationApp BEFORE importing other Isaac Sim modules
simulation_app = SimulationApp({"headless": False})

from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage

# Load custom scene USD
usd_path = "/home/omen/teamwork_projects/tomato_cutting_right_arm/assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd"
add_reference_to_stage(usd_path, "/World/Robot")

# Standard World initialization
world = World()

# Basic physics loop
world.reset()
while simulation_app.is_running():
    world.step(render=True)
    
simulation_app.close()
