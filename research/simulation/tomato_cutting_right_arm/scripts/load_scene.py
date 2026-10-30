"""Load the complete authored scene in a disposable Isaac Lab stage.

Default: paused preview. --simulate explicitly enables physics.
The original USD and all referenced assets remain read-only.
"""
import argparse
import json
from pathlib import Path
from isaaclab.app import AppLauncher

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENE = ROOT / 'assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--scene', type=Path, default=DEFAULT_SCENE)
parser.add_argument('--steps', type=int, default=0, help='Exit after this many updates; 0 keeps the window open.')
parser.add_argument('--simulate', action='store_true')
parser.add_argument('--keep-open', action='store_true', help='Keep preview open after finite updates and capture.')
parser.add_argument('--capture', type=Path, help='Save a viewport image after the preview updates.')
AppLauncher.add_app_launcher_args(parser)
parser.set_defaults(visualizer=["kit"])
args = parser.parse_args()
if not args.scene.is_file():
    parser.error(f'Scene not found: {args.scene}')
launcher = AppLauncher(args)
app = launcher.app

try:
    import omni.usd
    from scene_stage import compose
    # Start with a disposable root layer; never edit/save the source scene.
    context = omni.usd.get_context()
    context.new_stage()
    stage = context.get_stage()
    report = compose(stage, args.scene)
    report['physics_enabled'] = args.simulate
    sim = None
    if not args.simulate:
        # Preview-only overrides in the disposable layer avoid costly mesh cooking.
        from pxr import UsdPhysics
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.CollisionAPI):
                UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Set(False)
        import omni.timeline
        omni.timeline.get_timeline_interface().stop()
    if args.simulate:
        from isaaclab.sim import SimulationCfg, SimulationContext
        from isaaclab.sim.utils import use_stage
        stage.OverridePrim('/PhysicsScene').SetActive(False)
        with use_stage(stage):
            sim = SimulationContext(SimulationCfg(device=args.device, dt=1/60))
    (ROOT/'logs').mkdir(exist_ok=True)
    (ROOT/'logs/scene_report.json').write_text(json.dumps(report, indent=2))
    print('FULL_SCENE_LOADED', json.dumps(report), flush=True)
    from pxr import Gf, UsdGeom
    from omni.kit.viewport.utility import get_active_viewport
    camera = UsdGeom.Camera.Define(stage, '/PreviewCamera')
    camera.CreateClippingRangeAttr((0.01, 10000.0))
    camera.CreateFocalLengthAttr(24.0)
    transform = Gf.Matrix4d().SetLookAt(Gf.Vec3d(-4.15, -3.39, 1.96), Gf.Vec3d(-1.8, -1.3, 1.0), Gf.Vec3d(0, 0, 1)).GetInverse()
    UsdGeom.Xformable(camera).AddTransformOp().Set(transform)
    get_active_viewport().camera_path = '/PreviewCamera' 
    if args.simulate:
        sim.reset()
    count = 0
    while app.is_running() and (args.steps == 0 or count < args.steps):
        if args.simulate:
            sim.step()
        else:
            app.update()
        count += 1
    if args.capture:
        import asyncio
        from omni.kit.viewport.utility import get_active_viewport, capture_viewport_to_file
        args.capture.parent.mkdir(parents=True, exist_ok=True)
        capture = capture_viewport_to_file(get_active_viewport(), str(args.capture.resolve()))
        future = asyncio.ensure_future(capture.wait_for_result())
        for _ in range(600):
            if future.done():
                break
            app.update()
        if not future.done():
            raise RuntimeError('Viewport capture timed out')
        future.result()
        print(f'VIEWPORT_CAPTURED {args.capture}', flush=True)
    print(f'SCENE_RUN_COMPLETE updates={count}', flush=True)
    if args.keep_open:
        while app.is_running():
            if args.simulate:
                sim.step()
            else:
                app.update()
except BaseException:
    import traceback
    traceback.print_exc()
    raise
finally:
    app.close()
