import argparse
import torch
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Interactive Viewer for AR5-L6")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import isaaclab.sim as sim_utils
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab.assets import AssetBaseCfg, ArticulationCfg
from isaaclab_assets.robots.ar5_l6 import AR5_O6_LEFT_COMBINED_CFG

@configclass
class ViewerSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(),
    )
    light = AssetBaseCfg(
        prim_path="/World/defaultLight",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.9, 0.9, 0.9)),
    )
    robot: ArticulationCfg = AR5_O6_LEFT_COMBINED_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

def main():
    sim_cfg = sim_utils.SimulationCfg(device="cuda:0" if torch.cuda.is_available() else "cpu", dt=0.01)
    sim = sim_utils.SimulationContext(sim_cfg)
    scene_cfg = ViewerSceneCfg(num_envs=1, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)

    sim.reset()
    scene.reset()

    print("=" * 60)
    print("ROBOT SPAWNED WITH MOTOR CONTROLS ACTIVE!")
    print("You can now safely inspect the robot. The articulation root is fixed.")
    print("Close the Isaac Sim window to exit.")
    print("=" * 60)

    # Keep the simulator running indefinitely
    while simulation_app.is_running():
        sim.step()

    simulation_app.close()

if __name__ == "__main__":
    main()
