import argparse
import sys
import os

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import omni.kit.commands
import omni.usd
import omni.isaac.core.utils.stage as stage_utils
from omni.isaac.urdf import _urdf

def main():
    urdf_path = "/home/omen/teamwork_projects/tomato_cutting_right_arm/ros2_ws/src/ar5_o6_right_description/urdf/dual_ar5_o6.urdf"
    usd_path = "/home/omen/teamwork_projects/tomato_cutting_right_arm/assets/robots/dual_ar5_o6/dual_ar5_o6.usd"
    
    os.makedirs(os.path.dirname(usd_path), exist_ok=True)
    
    urdf_interface = _urdf.acquire_urdf_interface()
    
    import_config = _urdf.ImportConfig()
    import_config.merge_fixed_joints = False
    import_config.convex_decomp = True
    import_config.import_inertia_tensor = True
    import_config.fix_base = True
    import_config.create_physics_scene = False
    
    print(f"Importing URDF from {urdf_path} to {usd_path}...")
    omni.kit.commands.execute(
        "URDFParseAndImportFile",
        urdf_path=urdf_path,
        import_config=import_config,
        dest_path=usd_path,
    )
    
    print("Done!")
    simulation_app.close()

if __name__ == "__main__":
    main()
