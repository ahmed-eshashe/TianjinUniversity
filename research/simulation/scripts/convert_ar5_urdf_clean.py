# Copyright (c) 2026, DEX-ROB Lab, Tianjin University.
# Convert AR5_O6 combined URDF to a clean, selectable, non-instanceable USD
# with ArticulationRootAPI precisely on /ar5_o6_left.

import os
import shutil
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import omni.kit.app
from pxr import Usd, UsdPhysics, UsdGeom

# Ensure required extensions are active
ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_manager.set_extension_enabled_immediate("isaacsim.asset.importer.urdf", True)
ext_manager.set_extension_enabled_immediate("isaacsim.robot.schema", True)

from isaacsim.asset.importer.urdf.impl import URDFImporter, URDFImporterConfig


def main():
    urdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/assets/robots/ar5_l6/urdf/left/ar5_o6_left_combined.urdf"
    usd_root = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/assets/robots/ar5_l6/usd_clean"
    target_dir = os.path.join(usd_root, "ar5_o6_left")

    # Clean previous output directory if it exists to ensure fresh generation
    if os.path.exists(target_dir):
        print(f"[INFO] Removing previous build at: {target_dir}")
        shutil.rmtree(target_dir)

    os.makedirs(usd_root, exist_ok=True)

    print(f"[INFO] Source URDF: {urdf_path}")
    print(f"[INFO] Target Directory: {usd_root}")

    # Configure importer
    config = URDFImporterConfig()
    config.urdf_path = urdf_path
    config.usd_path = usd_root
    config.fix_base = True
    config.merge_fixed_joints = False
    config.self_collision = False
    config.run_asset_transformer = False  # CRITICAL: Keeps flat stage, NO instanced prototypes!
    config.run_multi_physics_conversion = True

    importer = URDFImporter(config)
    output_usd = importer.import_urdf()
    print(f"[SUCCESS] Raw conversion output: {output_usd}")

    if not output_usd or not os.path.exists(output_usd):
        raise RuntimeError(f"Output USD does not exist: {output_usd}")

    # Now open and standardize the USD stage
    stage = Usd.Stage.Open(output_usd)
    default_prim = stage.GetDefaultPrim()
    print(f"[INFO] Default Prim: {default_prim.GetPath()}")

    # Find and fix ArticulationRootAPI placement
    art_roots = []
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            art_roots.append(prim)

    print(f"[INFO] Initial Articulation Roots detected: {[str(p.GetPath()) for p in art_roots]}")

    # Remove ArticulationRootAPI from all non-root prims (e.g. fix_base_joint or base link)
    for prim in art_roots:
        if prim.GetPath() != default_prim.GetPath():
            print(f"[INFO] Removing ArticulationRootAPI from child prim: {prim.GetPath()}")
            prim.RemoveAPI(UsdPhysics.ArticulationRootAPI)

    # Ensure ArticulationRootAPI is applied to the default root prim (/ar5_o6_left)
    if not default_prim.HasAPI(UsdPhysics.ArticulationRootAPI):
        print(f"[INFO] Applying ArticulationRootAPI to root prim: {default_prim.GetPath()}")
        UsdPhysics.ArticulationRootAPI.Apply(default_prim)

    # Verify instancing: ensure NO prims are marked instanceable
    instanceable_count = 0
    for prim in stage.Traverse():
        if prim.IsInstanceable() or prim.IsInstance():
            prim.SetInstanceable(False)
            instanceable_count += 1

    print(f"[INFO] Verified instanceability: {instanceable_count} instanced prims made direct selectable.")

    # Save stage
    stage.GetRootLayer().Save()
    print(f"[SUCCESS] Clean USD stage saved to: {output_usd}")

    # Final Verification Traverse
    verified_roots = [p.GetPath() for p in stage.Traverse() if p.HasAPI(UsdPhysics.ArticulationRootAPI)]
    rigid_bodies = [p.GetPath() for p in stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)]
    joints = [p.GetPath() for p in stage.Traverse() if p.IsA(UsdPhysics.Joint)]

    print("\n" + "=" * 50)
    print("           USD STAGE FINAL AUDIT REPORT")
    print("=" * 50)
    print(f"Asset File:           {output_usd}")
    print(f"Default Prim:         {default_prim.GetPath()}")
    print(f"Articulation Roots:   {verified_roots}")
    print(f"Total Rigid Bodies:   {len(rigid_bodies)}")
    print(f"Total Physics Joints: {len(joints)}")
    print(f"Is Root Instanced:    {default_prim.IsInstanceable()}")
    print("=" * 50)

    assert len(verified_roots) == 1 and verified_roots[0] == default_prim.GetPath(), \
        f"Expected exactly 1 root on {default_prim.GetPath()}, got {verified_roots}"

    simulation_app.close()
    print("[SUCCESS] Pipeline completed cleanly.")


if __name__ == "__main__":
    main()
