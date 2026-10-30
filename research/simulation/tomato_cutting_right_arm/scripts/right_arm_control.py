"""Robot-only PhysX validation and right-arm joint control; never saves source assets."""
import argparse
import json
import math
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gui', action='store_true')
parser.add_argument('--interactive', action='store_true')
parser.add_argument('--capture', type=Path)
args = parser.parse_args()
if args.interactive and not args.gui:
    parser.error('--interactive requires --gui')
from isaacsim import SimulationApp
app = SimulationApp({'headless': not args.gui, 'width': 1000, 'height': 720,
                     'anti_aliasing': 0, 'renderer': 'RaytracedLighting'})
try:
    import numpy as np
    import omni.usd
    from pxr import Gf, Usd, UsdGeom, UsdPhysics, PhysxSchema, UsdLux
    from isaacsim.core.api import World
    from isaacsim.core.prims import SingleArticulation
    from isaacsim.core.utils.types import ArticulationAction

    context = omni.usd.get_context()
    context.new_stage()
    stage = context.get_stage()
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    source = ROOT/'assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd'
    robot_prim = stage.DefinePrim('/dual_ar5_o6', 'Xform')
    robot_prim.GetReferences().AddReference(str(source), '/dual_ar5_o6')
    # Expand instances only in this disposable stage so collider overrides reach meshes.
    while True:
        instances = [p for p in Usd.PrimRange(robot_prim) if p.IsInstance()]
        if not instances:
            break
        for p in instances:
            p.SetInstanceable(False)
    collisions = 0
    limits_by_name = {}
    for p in Usd.PrimRange(robot_prim):
        if p.IsA(UsdPhysics.CollisionGroup):
            # The authored hand group includes the entire stage and filters itself.
            # Restrict it to its explicit hand members so floor contacts work.
            p.GetAttribute('collection:colliders:includeRoot').Set(False)
            p.GetRelationship('collection:colliders:excludes').SetTargets([])
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            body = UsdPhysics.RigidBodyAPI(p)
            body.CreateVelocityAttr(Gf.Vec3f(0))
            body.CreateAngularVelocityAttr(Gf.Vec3f(0))
        if p.HasAPI(UsdPhysics.CollisionAPI) and p.IsA(UsdGeom.Mesh):
            UsdPhysics.MeshCollisionAPI.Apply(p).CreateApproximationAttr('convexHull')
            collisions += 1
        if p.IsA(UsdPhysics.RevoluteJoint):
            joint = UsdPhysics.RevoluteJoint(p)
            limits_by_name[p.GetName()] = [joint.GetLowerLimitAttr().Get(), joint.GetUpperLimitAttr().Get()]
            drive = UsdPhysics.DriveAPI.Apply(p, 'angular')
            arm = '_AR5_' in p.GetName()
            drive.CreateStiffnessAttr(2500.0 if arm else 50.0)
            drive.CreateDampingAttr(150.0 if arm else 2.0)
            drive.CreateTargetVelocityAttr(0.0)
    physx = PhysxSchema.PhysxArticulationAPI.Apply(robot_prim)
    physx.CreateEnabledSelfCollisionsAttr(False)
    physx.CreateSolverPositionIterationCountAttr(16)
    physx.CreateSolverVelocityIterationCountAttr(4)
    world = World(stage_units_in_meters=1.0, physics_dt=1/120, rendering_dt=1/30,
                  backend='numpy', device='cpu')
    world.scene.add_default_ground_plane(restitution=0.0)
    from isaacsim.core.api.objects import DynamicCuboid
    probe = world.scene.add(DynamicCuboid('/GravityProbe', name='gravity_probe',
        position=np.array([-3.0,-1.0,1.0]), size=0.1, mass=0.1,
        color=np.array([0.2,0.6,0.9])))
    light = UsdLux.DomeLight.Define(stage, '/TestLight')
    light.CreateIntensityAttr(1500)
    robot = world.scene.add(SingleArticulation('/dual_ar5_o6', name='dual_arm', reset_xform_properties=False))
    world.reset()
    names = robot.dof_names
    right = [names.index(f'right_AR5_5_07R_W4C4A2_joint_{i}') for i in range(1,8)]
    left = [i for i,n in enumerate(names) if n.startswith('left_AR5')]
    q0 = robot.get_joint_positions().copy()
    base_position = robot.get_world_pose()[0].copy()
    assert len(names) == 36 and np.isfinite(q0).all(), 'Invalid articulation initialization'
    robot.set_joint_velocities(np.zeros(len(names)))
    target = q0.copy()
    dt = 1/120
    max_speed = 0.0
    max_left_drift = 0.0
    def step(command, render=False):
        global max_speed, max_left_drift
        robot.apply_action(ArticulationAction(joint_positions=command))
        world.step(render=render)
        q = robot.get_joint_positions()
        v = robot.get_joint_velocities()
        if not np.isfinite(q).all() or not np.isfinite(v).all():
            raise RuntimeError('Non-finite physics state')
        max_speed = max(max_speed, float(np.max(np.abs(v))))
        max_left_drift = max(max_left_drift, float(np.max(np.abs(q[left]-q0[left]))))
        if np.max(np.abs(v)) > 15:
            raise RuntimeError('Unexpected joint speed; stopping test')
        return q.copy()
    print('ROBOT_READY', json.dumps({'dofs':names,'right_indices':right,'initial_deg':np.rad2deg(q0[right]).tolist(),'convex_colliders':collisions}), flush=True)
    for _ in range(30): step(target)
    probe_fall_z = float(probe.get_world_pose()[0][2])
    for _ in range(210): step(target)
    probe_rest_z = float(probe.get_world_pose()[0][2])
    contact_passed = probe_fall_z < 0.9 and abs(probe_rest_z-0.05)<0.01
    hold_error = float(np.max(np.abs(robot.get_joint_positions()-q0)))
    results=[]
    for index in right:
        start=target.copy()
        endpoint=start.copy()
        lower,upper=np.deg2rad(limits_by_name[names[index]])
        delta=math.radians(3) if start[index]+math.radians(3)<upper-0.01 else -math.radians(3)
        endpoint[index]+=delta
        assert lower < endpoint[index] < upper
        for k in range(240):
            a=(k+1)/240
            step(start+(endpoint-start)*(3*a*a-2*a*a*a))
        for _ in range(120): actual=step(endpoint)
        error=abs(float(actual[index]-endpoint[index]))
        moved=float(actual[index]-start[index])
        results.append({'joint':names[index],'command_deg':math.degrees(delta),'measured_delta_deg':math.degrees(moved),'error_deg':math.degrees(error)})
        print('JOINT_TEST',json.dumps(results[-1]),flush=True)
        for k in range(240):
            a=(k+1)/240
            step(endpoint+(start-endpoint)*(3*a*a-2*a*a*a))
        for _ in range(120): step(start)
    base_drift = float(np.linalg.norm(robot.get_world_pose()[0]-base_position))
    report={'passed': contact_passed and base_drift<0.001 and all(r['error_deg']<1.0 and abs(r['measured_delta_deg'])>1.5 for r in results) and math.degrees(max_left_drift)<1.0,
            'gravity_probe':{'passed':contact_passed,'height_after_0_25s_m':probe_fall_z,'resting_height_m':probe_rest_z},
            'base_drift_m':base_drift,'convex_mesh_colliders':collisions,
            'gravity_m_s2':9.81,'physics_hz':120,'backend':'CPU PhysX',
            'scope':'Robot-only, convex-hull mesh collision approximation, self-collision disabled; no kitchen/knife/contact grasp validation',
            'hold_max_error_deg':math.degrees(hold_error),'max_left_arm_drift_deg':math.degrees(max_left_drift),
            'max_joint_speed_rad_s':max_speed,'joint_tests':results}
    (ROOT/'logs/right_arm_physics_report.json').write_text(json.dumps(report,indent=2))
    print('PHYSICS_REPORT',json.dumps(report),flush=True)
    if not report['passed']: raise RuntimeError('Joint-control acceptance checks failed')
    if args.gui:
        from omni.kit.viewport.utility import get_active_viewport
        camera=UsdGeom.Camera.Define(stage,'/TestCamera')
        camera.CreateClippingRangeAttr((0.01,1000))
        camera.CreateFocalLengthAttr(18)
        mat=Gf.Matrix4d().SetLookAt(Gf.Vec3d(-4.0,-3.4,2.1),Gf.Vec3d(-1.65,-1.25,1.0),Gf.Vec3d(0,0,1)).GetInverse()
        UsdGeom.Xformable(camera).AddTransformOp().Set(mat)
        get_active_viewport().camera_path='/TestCamera'
        for _ in range(30): step(target,True)
    if args.capture:
        import asyncio
        from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
        args.capture.parent.mkdir(parents=True,exist_ok=True)
        future=asyncio.ensure_future(capture_viewport_to_file(get_active_viewport(),str(args.capture.resolve())).wait_for_result())
        for _ in range(300):
            if future.done(): break
            app.update()
        if not future.done(): raise RuntimeError('Capture timeout')
        future.result()
    if args.interactive:
        import omni.ui as ui
        window=ui.Window('Right arm — gentle joint control',width=430,height=430)
        desired=target.copy()
        models=[]
        def reset_targets():
            for model,value in zip(models,np.rad2deg(q0[right])): model.set_value(float(value))
        with window.frame:
            with ui.VStack(spacing=8):
                ui.Label('Simulation only | 7 right-arm joints | degrees')
                ui.Label('Limited to +/- 10 degrees around the starting pose.')
                for number,index in enumerate(right,1):
                    lower,upper=limits_by_name[names[index]]
                    center=float(np.rad2deg(q0[index]))
                    with ui.HStack():
                        ui.Label(f'Joint {number}',width=70)
                        slider=ui.FloatSlider(min=max(lower,center-10),max=min(upper,center+10))
                        slider.model.set_value(center)
                        slider.model.add_value_changed_fn(lambda model,i=index: desired.__setitem__(i,math.radians(model.as_float)))
                        models.append(slider.model)
                ui.Button('Return to starting pose',clicked_fn=reset_targets)
                ui.Label('Left arm and fingers hold their starting targets.')
                ui.Label('Kitchen, knife and self-collision are excluded.')
        # Exercise the same model callback used by the sliders and return button.
        models[0].set_value(float(np.rad2deg(q0[right[0]]))+1.0)
        assert abs(desired[right[0]]-q0[right[0]]-math.radians(1))<1e-5
        for _ in range(180):
            target += np.clip(desired-target,-math.radians(5)*dt,math.radians(5)*dt)
            actual=step(target)
        slider_error=abs(math.degrees(float(actual[right[0]]-desired[right[0]])))
        assert slider_error<1.0, 'Slider command did not reach target'
        reset_targets()
        assert np.max(np.abs(desired-q0))<1e-5
        for _ in range(180):
            target += np.clip(desired-target,-math.radians(5)*dt,math.radians(5)*dt)
            step(target)
        print('UI_CONTROL_TEST_PASSED error_deg='+str(slider_error),flush=True)
        print('INTERACTIVE_READY',flush=True)
        while app.is_running():
            begin=time.monotonic()
            for _ in range(4):
                target += np.clip(desired-target,-math.radians(5)*dt,math.radians(5)*dt)
                step(target)
            world.render()
            time.sleep(max(0,1/30-(time.monotonic()-begin)))
except BaseException:
    import traceback
    traceback.print_exc()
    # Kit fast shutdown can mask Python exceptions; retain an explicit failure marker.
    print('CONTROL_FAILED', flush=True)
    raise
finally:
    app.close()
