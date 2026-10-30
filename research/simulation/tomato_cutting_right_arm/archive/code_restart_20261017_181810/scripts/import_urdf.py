import argparse
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": True})

import omni.kit.commands
from omni.importer.urdf import _urdf
import os

urdf_path = "/home/omen/teamwork_projects/tomato_cutting_right_arm/ros2_ws/src/ar5_o6_right_description/urdf/dual_ar5_o6.urdf"
dest_path = "/home/omen/teamwork_projects/tomato_cutting_right_arm/assets/robots/dual_ar5_o6/dual_ar5_o6.usd"

os.makedirs(os.path.dirname(dest_path), exist_ok=True)

# Set up the import config
urdf_interface = _urdf.acquire_urdf_interface()
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.convex_decomp = True
import_config.import_inertia_tensor = True
import_config.fix_base = True
import_config.make_default_prim = True

# Call the import command
success, result_path = omni.kit.commands.execute(
    "URDFParseAndImportFile", 
    urdf_path=urdf_path,
    import_config=import_config,
    dest_path=dest_path
)

if success:
    print(f"Successfully imported URDF to {dest_path}")
else:
    print("Failed to import URDF")

simulation_app.close()
