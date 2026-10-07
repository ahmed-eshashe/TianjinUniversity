# Copyright (c) 2026, DEX-ROB Lab, Tianjin University.
# Convert AR5_O6 combined URDF to a clean, stable USD using Isaac Lab's official UrdfConverter.

import os
import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Convert AR5_O6 URDF to clean USD.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg

def main():
    urdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/assets/robots/ar5_l6/urdf/left/ar5_o6_left_combined.urdf"
    usd_dir = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/assets/robots/ar5_l6/usd_clean"
    os.makedirs(usd_dir, exist_ok=True)

    print(f"[INFO] Converting URDF: {urdf_path}")
    print(f"[INFO] Destination USD Directory: {usd_dir}")

    cfg = UrdfConverterCfg(
        asset_path=urdf_path,
        usd_dir=usd_dir,
        usd_file_name="ar5_o6_left_clean.usd",
        fix_base=True,
        merge_fixed_joints=False,
        self_collision=False,
        make_instanceable=False,
    )

    converter = UrdfConverter(cfg)
    print(f"\n[SUCCESS] Successfully generated clean USD asset at:")
    print(f"          {converter.usd_path}")

    simulation_app.close()

if __name__ == "__main__":
    main()
