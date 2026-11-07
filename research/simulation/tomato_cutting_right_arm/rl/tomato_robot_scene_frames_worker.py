"""Bounded actual-robot loading, frame comparison and dirty rigid-state reset."""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import sys
import traceback

ROOT=Path(__file__).resolve().parents[1]
from tomato_isaac_startup_worker import write


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output
    app=None;passed=False;steps=0;newton_steps=0
    def stop(signum,frame):
        raise InterruptedError('Robot scene frame check stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        audit=json.loads((ROOT/'runs/offline/robot_scene_20261101_01/scene_audit.json').read_text())
        if not audit['passed']:raise ValueError('Scene audit required')
        if not all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in audit['source_sha256'].items()):raise ValueError('Audited source changed')
        code_paths=[Path(__file__),ROOT/'rl/tomato_robot_scene_audit.py',ROOT/'rl/tomato_robot_scene_fixture.py',
            ROOT/'scripts/reach_kinematics.py',ROOT/'rl/tomato_native_full_model.py',ROOT/'rl/tomato_native_full_gather.py',
            ROOT/'rl/tomato_native_volume_steps.py',ROOT/'rl/tomato_isaac_startup_guard.py',
            ROOT/'runs/offline/robot_scene_20261101_01/scene_audit.json',Path(audit['scene'])]
        code_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in code_paths}
        write(out,'input_manifest.json',dict(source_sha256={**audit['source_sha256'],**code_pins},
            physx_step_cap=2,newton_step_cap=6,knife_attachment=False,training=False))
        from isaaclab.app import AppLauncher
        app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
        import numpy as np
        import torch
        from scipy.spatial.transform import Rotation
        from pxr import UsdGeom
        import isaaclab.sim as sim_utils
        from isaaclab_physx.physics import PhysxCfg
        from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
        from isaaclab.actuators import ImplicitActuatorCfg
        sys.path.insert(0,str(ROOT/'scripts'))
        from reach_kinematics import ArmKinematics
        dt=1/240
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=dt,use_fabric=False,use_newton_actuators=False,
            physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),log_dir=str(out)))
        sim.stage.GetRootLayer().subLayerPaths.append(audit['scene'])
        matrix=np.array(audit['robot_root_world_matrix'])
        robot=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,
            init_state=ArticulationCfg.InitialStateCfg(pos=tuple(matrix[:3,3]),rot=tuple(Rotation.from_matrix(matrix[:3,:3]).as_quat()),joint_pos=audit['home_rad']),
            actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),
                'hand':ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),
                'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
        km=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(sim.stage.GetPrimAtPath(audit['knife_path']))).T
        knife=RigidObject(RigidObjectCfg(prim_path=audit['knife_path'],spawn=None,
            init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(km[:3,3]),rot=tuple(Rotation.from_matrix(km[:3,:3]).as_quat()))))
        kin=ArmKinematics(sim.stage)
        sim.stage.GetRootLayer().Export(str(out/'scene.usda'))
        sim.reset()
        if 'isaaclab_physx' not in sim.physics_manager.__module__:raise ValueError('CPU PhysX required')
        q=torch.tensor([[audit['home_rad'][n] for n in robot.joint_names]],dtype=torch.float32)
        initial=knife.data.default_root_pose.torch.clone()
        errors=[];reset_checks=[]
        def reset(dirty=False):
            if dirty:
                for asset in (robot,knife):
                    for composer in (asset.instantaneous_wrench_composer,asset.permanent_wrench_composer):
                        composer.set_forces_and_torques_index(forces=torch.ones((1,1,3)),torques=torch.ones((1,1,3)),positions=None,body_ids=[0],is_global=True)
                        if not composer.active:raise ValueError('Dirty wrench not established')
                robot.write_joint_velocity_to_sim_index(velocity=torch.ones_like(q)*.1)
                knife.write_root_velocity_to_sim_index(root_velocity=torch.ones((1,6))*.1)
            robot.reset();knife.reset()
            robot.write_joint_state_to_sim_index(position=q,velocity=torch.zeros_like(q))
            robot.set_joint_position_target_index(target=q)
            knife.write_root_pose_to_sim_index(root_pose=initial)
            knife.write_root_velocity_to_sim_index(root_velocity=torch.zeros((1,6)))
            robot.write_data_to_sim();knife.write_data_to_sim()
            reset_checks.append(dict(dirty=dirty,joint_position_error_rad=float((robot.data.joint_pos.torch-q).abs().max()),
                joint_speed_rad_s=float(robot.data.joint_vel.torch.abs().max()),knife_pose_error=float((knife.data.root_pose_w.torch-initial).abs().max()),
                knife_speed=float(knife.data.root_vel_w.torch.abs().max()),
                wrenches_clear=all(not c.active for a in (robot,knife) for c in (a.instantaneous_wrench_composer,a.permanent_wrench_composer))))
        for episode in range(2):
            reset(dirty=bool(episode))
            # Joint frame prediction uses actual float32 joint values, not double targets.
            actual=robot.data.body_link_pose_w.torch[0].cpu().numpy()
            qr=np.array([float(robot.data.joint_pos.torch[0,robot.joint_names.index(n)]) for n in kin.names])
            for path,t in kin.transforms(qr).items():
                name=path.rsplit('/',1)[-1]
                if name not in robot.body_names:continue
                a=actual[robot.body_names.index(name)]
                errors.append(dict(episode=episode,body=name,position_error_m=float(np.linalg.norm(a[:3]-t[:3,3])),
                    rotation_error_rad=float(Rotation.from_matrix(Rotation.from_quat(a[3:]).as_matrix()@t[:3,:3].T).magnitude())))
            if (out/'stop.request').exists():raise InterruptedError('Guard requested stop')
            sim.step(render=False);steps+=1;robot.update(dt);knife.update(dt)
        checks=dict(actual_robot_loaded=robot.num_joints==36,frames_match=max(e['position_error_m'] for e in errors)<2e-6 and max(e['rotation_error_rad'] for e in errors)<2e-5,
            resets_clear=all(r['joint_position_error_rad']<1e-7 and r['joint_speed_rad_s']==0 and r['knife_pose_error']<1e-7 and r['knife_speed']==0 and r['wrenches_clear'] for r in reset_checks),
            finite_state=bool(torch.isfinite(robot.data.joint_pos.torch).all()),
            sources_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in audit['source_sha256'].items()))
        write(out,'robot_scene_frames.json',dict(checks=checks,errors=errors,resets=reset_checks,joint_names=robot.joint_names,body_names=robot.body_names,
            fixed_base=robot.is_fixed_base,num_joints=robot.num_joints,scope='Actual robot frame and rigid reset check only; no knife mounting, trajectory, tomato mechanics or training.'))
        if not all(checks.values()):raise ValueError('Robot frame or rigid reset gate failed')
        from tomato_robot_scene_fixture import check_fixture
        newton_steps=check_fixture(out)
        if not all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in code_pins.items()):raise ValueError('Scene diagnostic source changed during execution')
        passed=True
    except BaseException as exc:
        write(out,'worker_error.json',dict(error=repr(exc),traceback=traceback.format_exc()))
    finally:
        write(out,'worker_result.json',dict(diagnostic_passed=passed,robot_scene_frames_passed=passed,controlled_steps=steps,newton_steps=newton_steps,shutdown_requested=app is not None,training=False))
        if app is not None:app.close()
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
