"""Guarded actual-robot fixed-tool dry stroke with collision and reset checks."""
import argparse,hashlib,json,signal,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from tomato_isaac_startup_worker import write


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=None;passed=False;steps=0;newton_steps=0;episodes=[];resets=[]
    def stop(*args):raise InterruptedError('Fixed mount diagnostic stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        plan_path=ROOT/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json'
        plan=json.loads(plan_path.read_text())
        pins={**plan['source_sha256'],str(plan_path):hashlib.sha256(plan_path.read_bytes()).hexdigest(),
              plan['scene']:hashlib.sha256(Path(plan['scene']).read_bytes()).hexdigest(),
              str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              **{str(ROOT/p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['rl/tomato_fixed_mount_target.py','rl/tomato_robot_scene_fixture.py','rl/tomato_isaac_startup_guard.py','rl/tomato_native_full_model.py','rl/tomato_exact_blade_coverage.py','rl/tomato_exact_blade_queries.py','rl/tomato_mesh_weighted_contact.py','work/exact_blade_cells.json']}}
        if not all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items()):raise ValueError('Source pin changed')
        write(out,'input_manifest.json',dict(source_sha256=pins,physx_step_cap=3851,newton_step_cap=30,
            knife_connection='user-authorized ideal fixed mount',training=False))
        from isaaclab.app import AppLauncher
        app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
        import numpy as np,torch
        from scipy.spatial.transform import Rotation
        from pxr import UsdPhysics,UsdGeom
        import isaaclab.sim as sim_utils
        from isaaclab_physx.physics import PhysxCfg,PhysxManager
        from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
        from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg
        from isaaclab.actuators import ImplicitActuatorCfg
        from isaaclab.app.settings_manager import get_settings_manager
        get_settings_manager().set_bool('/physics/disableContactProcessing',False)
        sys.path.insert(0,str(ROOT/'scripts'))
        from reach_kinematics import ArmKinematics
        dt=plan['dt_s']
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=dt,use_fabric=False,use_newton_actuators=False,
            physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),log_dir=str(out)))
        get_settings_manager().set_bool('/physics/disableContactProcessing',False)
        sim.stage.GetRootLayer().subLayerPaths.append(plan['scene'])
        m=np.array(plan['robot_root_world_matrix'])
        robot=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,
            init_state=ArticulationCfg.InitialStateCfg(pos=tuple(m[:3,3]),rot=tuple(Rotation.from_matrix(m[:3,:3]).as_quat()),joint_pos=plan['home_rad']),
            actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),
              'hand':ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),
              'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
        floor=sim_utils.CuboidCfg(size=(.2,.2,.02),collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=True))
        floor.func('/ContactControlFloor',floor,translation=(2.,0.,-.01))
        probe_spawn=sim_utils.CuboidCfg(size=(.02,.02,.02),
            rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),PhysxRigidBodyCfg(disable_gravity=True,sleep_threshold=0.,stabilization_threshold=0.)],
            collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=True),mass_props=sim_utils.MassCfg(mass=.01,density=0.))
        probe=RigidObject(RigidObjectCfg(prim_path='/ContactControlProbe',spawn=probe_spawn,
            init_state=RigidObjectCfg.InitialStateCfg(pos=(2.,0.,.3),rot=(0.,0.,0.,1.))))
        for prim in (sim.stage.GetPrimAtPath('/ContactControlProbe'),):
            prim.AddAppliedSchema('PhysxContactReportAPI')
            prim.CreateAttribute('physxContactReport:threshold',__import__('pxr').Sdf.ValueTypeNames.Float).Set(0.)
        sim.stage.GetRootLayer().Export(str(out/'mounted_scene.usda'))
        sim.reset()
        get_settings_manager().set_bool('/physics/disableContactProcessing',False)
        tool=robot.body_names.index('MountedKnife');hand=robot.body_names.index(plan['hand_path'].rsplit('/',1)[-1])
        if robot.num_joints!=36:raise ValueError('Mount must add no actuator DOF')
        ids=[robot.joint_names.index(n) for n in plan['right_joint_names']]
        home=torch.tensor([[plan['home_rad'][n] for n in robot.joint_names]],dtype=torch.float32)
        mount=np.asarray(plan['mount_hand_from_knife'])
        blade=np.asarray(json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices'])
        target=json.loads((ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text())
        target_x=np.asarray([n['position_m'] for n in target['nodes']])+[0.,0.,.002]
        target_lo=target_x.min(0);target_hi=target_x.max(0)
        bodies=[str(p.GetPath()) for p in sim.stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)]
        filters=bodies+[plan['board_path'],plan['counter_path'],'/ContactControlFloor/geometry/mesh']
        view=PhysxManager.get_physics_sim_view().create_rigid_contact_view(bodies,[filters for _ in bodies],max_contact_data_count=16384)
        def arr(value):
            if isinstance(value,np.ndarray):return value
            if hasattr(value,'numpy'):return value.numpy()
            return value.detach().cpu().numpy()
        def transform(pose):
            t=np.eye(4);t[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();t[:3,3]=pose[:3];return t
        trace0=None
        for episode in range(2):
            if episode:
                for composer in (robot.instantaneous_wrench_composer,robot.permanent_wrench_composer):
                    composer.set_forces_and_torques_index(forces=torch.ones((1,1,3)),torques=torch.ones((1,1,3)),positions=None,body_ids=[tool],is_global=True)
                    if not composer.active:raise ValueError('Dirty mount wrench missing')
                robot.write_joint_velocity_to_sim_index(velocity=torch.ones_like(home)*.1)
            robot.reset();robot.write_joint_state_to_sim_index(position=home,velocity=torch.zeros_like(home));robot.set_joint_position_target_index(target=home)
            robot.write_data_to_sim();robot.update(dt)
            reset=dict(episode=episode,joint_error_rad=float((robot.data.joint_pos.torch-home).abs().max()),
                joint_speed_rad_s=float(robot.data.joint_vel.torch.abs().max()),
                tool_speed=float(robot.data.body_com_vel_w.torch[0,tool].abs().max()),
                queues_clear=not robot.instantaneous_wrench_composer.active and not robot.permanent_wrench_composer.active)
            resets.append(reset)
            trace=[];max_contact=0.;contact_pairs={};min_gap=float('inf');min_board=float('inf');max_mount=0.;max_angle=0.;max_speed=0.;max_track=0.
            for i,right in enumerate(plan['right_joint_route_rad']):
                goal=home.clone();goal[:,ids]=torch.tensor([right],dtype=torch.float32)
                for substep in range(plan['substeps_per_sample']):
                    if (out/'stop.request').exists():raise InterruptedError('Guard stop between robot substeps')
                    robot.set_joint_position_target_index(target=goal);robot.write_data_to_sim();sim.step(render=False);steps+=1;robot.update(dt)
                    poses=robot.data.body_link_pose_w.torch[0].cpu().numpy();t=transform(poses[tool]);expected=transform(poses[hand])@mount
                    mount_error=float(np.linalg.norm(t[:3,3]-expected[:3,3]));angle=float(Rotation.from_matrix(t[:3,:3]@expected[:3,:3].T).magnitude())
                    world=blade@t[:3,:3].T+t[:3,3]
                    # Positive separation on any coordinate axis certifies disjoint AABBs.
                    separation=float(np.maximum(target_lo-world.max(0),world.min(0)-target_hi).max())
                    board=float(world[:,2].min())
                    speed=float(robot.data.joint_vel.torch.abs().max());tracking=float((robot.data.joint_pos.torch[:,ids]-goal[:,ids]).abs().max())
                    contact=arr(view.get_contact_force_matrix(dt=dt));norm=np.linalg.norm(contact,axis=-1)
                    peak=float(norm.max(initial=0.));max_contact=max(max_contact,peak)
                    for a,b in zip(*np.where(norm>.1)):
                        key=bodies[a]+' -> '+filters[b];contact_pairs[key]=max(contact_pairs.get(key,0.),float(norm[a,b]))
                    min_gap=min(min_gap,separation);min_board=min(min_board,board);max_mount=max(max_mount,mount_error);max_angle=max(max_angle,angle);max_speed=max(max_speed,speed);max_track=max(max_track,tracking)
                    if not np.isfinite(poses).all() or speed>3. or separation<=.015 or board<=.004 or mount_error>2e-5 or angle>2e-4:
                        write(out,'failed_state.json',dict(episode=episode,sample=i,substep=substep,speed=speed,separation=separation,board=board,mount_error=mount_error,angle=angle,contact_pairs=contact_pairs))
                        raise ValueError('Fixed-tool dry motion exceeded a geometric or velocity gate')
                trace.append(dict(sample=i,q=robot.data.joint_pos.torch.cpu().tolist()[0],qd=robot.data.joint_vel.torch.cpu().tolist()[0],tool_pose=poses[tool].tolist()))
            measurement=dict(episode=episode,minimum_target_aabb_separation_m=min_gap,minimum_blade_board_clearance_m=min_board,
                maximum_mount_position_error_m=max_mount,maximum_mount_angle_error_rad=max_angle,maximum_joint_speed_rad_s=max_speed,
                maximum_right_tracking_error_rad=max_track,maximum_contact_force_n=max_contact,contact_pairs_over_point1_n=contact_pairs,trace=trace)
            episodes.append(measurement);write(out,'dry_motion_partial.json',dict(episodes=episodes,resets=resets,steps=steps))
        # A positive control prevents a disabled contact pipeline from passing
        # the no-collision gate solely because all returned forces are zero.
        if get_settings_manager().get('/physics/disableContactProcessing'):
            raise ValueError('Contact processing was disabled')
        probe_pose=probe.data.default_root_pose.torch.clone();dirty_pose=probe_pose.clone();dirty_pose[:,2]=.009
        probe.write_root_pose_to_sim_index(root_pose=dirty_pose)
        impact_velocity=torch.zeros((1,6));impact_velocity[:,2]=-.1
        probe.write_root_velocity_to_sim_index(root_velocity=impact_velocity)
        probe.write_data_to_sim();robot.write_data_to_sim();sim.step(render=False);steps+=1;probe.update(dt);robot.update(dt)
        measured=arr(view.get_contact_force_matrix(dt=dt))
        positive=float(np.linalg.norm(measured[bodies.index('/ContactControlProbe'),filters.index('/ContactControlFloor/geometry/mesh')]))
        if positive<.01:raise ValueError(f'Collision positive control failed: {positive=}')
        probe.reset();probe.write_root_pose_to_sim_index(root_pose=probe_pose);probe.write_root_velocity_to_sim_index(root_velocity=torch.zeros((1,6)))
        cleared=[]
        for _ in range(2):
            probe.write_data_to_sim();robot.write_data_to_sim();sim.step(render=False);steps+=1;probe.update(dt);robot.update(dt)
            measured=arr(view.get_contact_force_matrix(dt=dt))
            cleared.append(float(np.linalg.norm(measured[bodies.index('/ContactControlProbe'),filters.index('/ContactControlFloor/geometry/mesh')])))
        write(out,'collision_positive_control.json',dict(contact_processing_enabled=True,overlap_force_n=positive,reset_clear_forces_n=cleared,
            scope='Separate deliberate probe/floor overlap confirms native monitoring; positive force then zero after pose reset.'))
        qerr=max(abs(a-b) for f,s in zip(episodes[0]['trace'],episodes[1]['trace']) for a,b in zip(f['q'],s['q']))
        perr=max(abs(a-b) for f,s in zip(episodes[0]['trace'],episodes[1]['trace']) for a,b in zip(f['tool_pose'],s['tool_pose']))
        checks=dict(contact_monitor_positive=positive>.01 and max(cleared)<1e-6,
            no_added_dof=robot.num_joints==36,rigid_mount=all(e['maximum_mount_position_error_m']<2e-5 and e['maximum_mount_angle_error_rad']<2e-4 for e in episodes),
            no_target_contact=all(e['minimum_target_aabb_separation_m']>.015 for e in episodes),
            tracking_bounded=all(e['maximum_right_tracking_error_rad']<.03 for e in episodes),
            stroke_executed=all(max(t['tool_pose'][2] for t in e['trace'])-min(t['tool_pose'][2] for t in e['trace'])>.13 for e in episodes),
            blade_above_board=all(e['minimum_blade_board_clearance_m']>.004 for e in episodes),
            no_forbidden_rigid_contacts=all(not e['contact_pairs_over_point1_n'] for e in episodes),
            reset_clean=all(r['joint_error_rad']<1e-7 and r['joint_speed_rad_s']==0 and r['tool_speed']<2e-5 and r['queues_clear'] for r in resets),
            replay_matches=qerr<1e-5 and perr<2e-6,
            sources_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items()))
        from tomato_robot_scene_fixture import check_fixture
        newton_steps=check_fixture(out)
        from tomato_fixed_mount_target import check_target
        newton_steps+=check_target(out,robot.data.body_link_pose_w.torch[0,tool].cpu().tolist())
        write(out,'fixed_mount_measurements.json',dict(checks=checks,episodes=episodes,resets=resets,replay_joint_error_rad=qerr,replay_tool_pose_error=perr,
            physics_steps=steps,newton_steps=newton_steps,body_names=robot.body_names,joint_names=robot.joint_names,
            scope='Fixed mount dry motion under robot gravity. Target fixture checked separately. No actual cutting, finger grasp or hardware calibration.'))
        if not all(checks.values()):raise ValueError('Fixed-mount checks failed: '+str(checks))
        if steps!=3851 or newton_steps!=30:raise ValueError('Unexpected fixed mount diagnostic steps')
        passed=True
    except BaseException as exc:
        write(out,'worker_error.json',dict(error=repr(exc),traceback=traceback.format_exc()))
    finally:
        write(out,'worker_result.json',dict(diagnostic_passed=passed,fixed_mount_passed=passed,controlled_steps=steps,newton_steps=newton_steps,
            episodes_completed=len(episodes),shutdown_requested=app is not None,training=False))
        if app is not None:app.close(exit_code=0 if passed else 1)
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
