"""Bounded Phase 2 resource probe. This is NOT a knife-learning environment."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--seconds', type=int, required=True)
p.add_argument('--camera', action='store_true')
p.add_argument('--width', type=int, default=128)
p.add_argument('--max-updates', type=int, default=12)
p.add_argument('--resume', type=Path)
a = p.parse_args()
OUT = a.output; OUT.mkdir(parents=True, exist_ok=True)


def write(name, value):
    tmp = OUT / (name + '.tmp'); tmp.write_text(json.dumps(value, indent=2)); tmp.replace(OUT / name)


def main(app):
    import numpy as np
    import torch
    from scipy.spatial.transform import Rotation
    from pxr import Gf, Usd, UsdGeom, UsdLux
    import omni.usd
    from isaacsim.core.api import World
    from isaacsim.core.prims import SingleArticulation, SingleRigidPrim
    from isaacsim.core.utils.types import ArticulationAction
    from probe_policy import ProbePolicy, RunningMoments, VisionProxy, ppo_update, save_checkpoint

    torch.set_num_threads(1)
    random.seed(731); np.random.seed(731); torch.manual_seed(731); torch.cuda.manual_seed_all(731)
    reset_rng = np.random.default_rng(731)
    manifest = json.loads((ROOT / 'rl/scene/manifest.json').read_text())
    context = omni.usd.get_context(); context.open_stage(str(ROOT / 'rl/scene/minimal_benchmark.usda'))
    stage = context.get_stage(); stage.SetEditTarget(stage.GetSessionLayer())
    light = UsdLux.DomeLight.Define(stage, '/BenchmarkLight'); light.CreateIntensityAttr(1000.)
    world = World(stage_units_in_meters=1., physics_dt=1/240, rendering_dt=1/20, backend='numpy', device='cpu')
    world.scene.add_default_ground_plane()
    robot = world.scene.add(SingleArticulation('/dual_ar5_o6', name='robot', reset_xform_properties=False))
    knife = world.scene.add(SingleRigidPrim(manifest['knife_path'], name='existing_knife', reset_xform_properties=False))
    world.reset()
    names = robot.dof_names
    home = np.array([manifest['home_rad'][n] for n in names], dtype=np.float32)
    audit = json.loads((ROOT / 'docs/rl/phase1_inventory.json').read_text())
    independent_names = audit['right_arm_independent'] + audit['right_hand_independent']
    independent = np.array([names.index(n) for n in independent_names])
    left = np.array([i for i, n in enumerate(names) if n.startswith('left_')])
    limits = {x['name']: x['limits_rad'] for x in audit['joints']}
    lower = np.array([limits[n][0] for n in independent_names]); upper = np.array([limits[n][1] for n in independent_names])
    q_initial, quat_initial = knife.get_world_pose()
    reset_count = 0; physics_steps = 0; control_steps = 0; render_count = 0
    max_speed = 0.; max_left_drift = 0.; max_tracking_error = 0.; max_mimic_error = 0.
    board_lo, board_hi = np.array(manifest['board_world_bounds'])
    camera = None; vision = None; latent = np.zeros(16, dtype=np.float32)
    camera_checks = {}; camera_age = []; last_camera_stamp = -1
    camera_seconds = 0.; vision_seconds = 0.; physics_seconds = 0.; update_seconds = 0.
    if a.camera:
        from isaacsim.sensors.camera import Camera
        camera_path = '/dual_ar5_o6/BenchmarkEye'
        camprim = UsdGeom.Camera.Define(stage, camera_path)
        camprim.CreateClippingRangeAttr((.02, 5.)); camprim.CreateFocalLengthAttr(24.)
        camprim.CreateHorizontalApertureAttr(20.955); camprim.CreateVerticalApertureAttr(20.955)
        root_world = np.array(manifest['robot_root_world_matrix'])
        eye = root_world[:3, 3] + np.array([.05, .15, 1.65])
        centre = (board_lo + board_hi) / 2; centre[2] = board_hi[2]
        matrix = np.array(Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye), Gf.Vec3d(*centre), Gf.Vec3d(0, 0, 1)).GetInverse()).T
        UsdGeom.Xformable(camprim).AddTransformOp().Set(Gf.Matrix4d((np.linalg.inv(root_world) @ matrix).T.tolist()))
        camera = Camera(camera_path, resolution=(a.width, a.width), frequency=20)
        camera.initialize(); camera.add_distance_to_image_plane_to_frame()
        vision = VisionProxy().cuda().eval()
        camera_checks.update(camera_path=camera_path, eye_world_m=eye.tolist(), look_at_world_m=centre.tolist(),
                             width=a.width, height=a.width, requested_hz=20, depth_type='distance_to_image_plane',
                             focal_length_mm=24., intrinsics=np.asarray(camera.get_intrinsics_matrix()).tolist(),
                             perception='UNTRAINED small RGB-D encoder, inference allocation proxy only')
    device = 'cuda'
    observation_size = 39 + (16 if a.camera else 0)
    policy = ProbePolicy(observation_size, 13).to(device)
    optimizer = torch.optim.Adam(policy.parameters(), lr=3e-4)
    moments = RunningMoments(observation_size)
    counts = {'updates': 0, 'transitions': 0, 'episodes': 0}
    resume_checks = {}
    if a.resume:
        saved = torch.load(a.resume, map_location=device, weights_only=False)
        if saved['config']['camera'] != a.camera or saved['config']['observation_size'] != observation_size:
            raise ValueError('Checkpoint observation/camera schema does not match')
        policy.load_state_dict(saved['policy']); optimizer.load_state_dict(saved['optimizer'])
        if vision:
            vision.load_state_dict(saved['vision_proxy'])
        moments.count = saved['normalization']['count']; moments.mean = saved['normalization']['mean']; moments.m2 = saved['normalization']['m2']
        counts = saved['counters'].copy()
        random.setstate(saved['rng']['python']); np.random.set_state(saved['rng']['numpy']); torch.set_rng_state(saved['rng']['torch'].cpu())
        torch.cuda.set_rng_state_all([x.cpu() for x in saved['rng']['cuda']]); reset_rng.bit_generator.state = saved['rng']['reset_generator']
        numpy_restored = np.random.get_state()
        rng_equal = bool(random.getstate() == saved['rng']['python'] and
                         numpy_restored[0] == saved['rng']['numpy'][0] and np.array_equal(numpy_restored[1], saved['rng']['numpy'][1]) and
                         numpy_restored[2:] == saved['rng']['numpy'][2:] and
                         torch.equal(torch.get_rng_state(), saved['rng']['torch'].cpu()) and
                         all(torch.equal(x.cpu(), y.cpu()) for x,y in zip(torch.cuda.get_rng_state_all(), saved['rng']['cuda'])) and
                         reset_rng.bit_generator.state == saved['rng']['reset_generator'])
        resume_checks = {'loaded': True, 'optimizer_entries': len(optimizer.state), 'normalization_count': moments.count,
                         'prior_updates': counts['updates'], 'curriculum': saved['curriculum'], 'rng_restored': rng_equal,
                         'physical_state': 'new episode; no claim of bit-exact PhysX contact-state continuation'}
        assert resume_checks['optimizer_entries'] > 0 and moments.count > 0 and rng_equal
    initial_updates = counts['updates']; initial_transitions = counts['transitions']
    first_weights = torch.cat([v.detach().flatten() for v in policy.parameters()]).clone()
    target = home.copy(); previous_action = np.zeros(13, dtype=np.float32)
    config = {'camera': a.camera, 'observation_size': observation_size, 'action_size': 13,
              'physics_hz': 240, 'action_hz': 20, 'episode_controls': 64, 'rollout_controls': 64,
              'policy': '64x64 tanh PPO probe, two epochs per 64 transitions', 'reward': 'negative bounded posture error only',
              'full_grasp_training': False, 'device': device, 'physics_device': 'cpu', 'width': a.width,
              'max_updates_this_run': a.max_updates, 'requested_seconds': a.seconds,
              'hashes': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [ROOT/'rl/benchmark.py', ROOT/'rl/probe_policy.py', ROOT/'rl/scene/minimal_benchmark.usda']}}
    write('run_configuration.json', config)

    def reset():
        nonlocal reset_count, target, previous_action
        # Teleport ONLY at an explicit episode reset, never within an episode.
        robot.set_joint_positions(home); robot.set_joint_velocities(np.zeros(len(names)))
        offset = np.array([*reset_rng.uniform(-.02, .02, 2), .002])
        knife.set_world_pose(q_initial + offset, quat_initial)
        knife.set_linear_velocity(np.zeros(3)); knife.set_angular_velocity(np.zeros(3))
        target = home.copy(); previous_action = np.zeros(13, dtype=np.float32)
        robot.apply_action(ArticulationAction(joint_positions=target))
        reset_count += 1; counts['episodes'] += 1

    def camera_read(save=False):
        nonlocal render_count, camera_seconds, vision_seconds, latent, last_camera_stamp
        t = time.perf_counter(); world.render(); camera_seconds += time.perf_counter() - t; render_count += 1
        rgba = camera.get_rgba(); depth = camera.get_depth()
        if rgba is None or depth is None or np.size(rgba) == 0 or np.size(depth) == 0:
            return False
        rgba = np.asarray(rgba); depth = np.asarray(depth).reshape(a.width, a.width)
        if rgba.shape[:2] != (a.width, a.width) or not np.isfinite(rgba).all() or rgba[..., :3].std() < 1.:
            raise RuntimeError('Invalid or blank RGB frame')
        finite = np.isfinite(depth) & (depth > .02) & (depth < 5.)
        if finite.mean() < .3:
            raise RuntimeError('Depth frame lacks useful finite distances')
        frame = camera.get_current_frame()
        # In Isaac Sim 6.1 rendering_frame is a ReferenceTime dictionary.
        # rendering_time is the SDK's simulation timestamp in seconds.
        stamp = float(frame.get('rendering_time', 0.))
        if stamp <= 0:
            return False
        if last_camera_stamp >= 0 and stamp < last_camera_stamp:
            raise RuntimeError('Camera frame counter moved backwards')
        if stamp != last_camera_stamp:
            camera_checks['distinct_timestamps'] = camera_checks.get('distinct_timestamps', 0) + 1
        last_camera_stamp = stamp
        age = max(0., float(world.current_time)-stamp)
        camera_age.append(age)
        if age > .25:
            raise RuntimeError(f'Stale camera observation: {age} simulated seconds')
        camera_checks.update(last_timestamp_seconds=stamp, depth_valid_fraction=float(finite.mean()), rgb_std=float(rgba[..., :3].std()))
        image = np.concatenate([rgba[..., :3].astype(np.float32)/255., np.nan_to_num(depth, nan=0., posinf=0., neginf=0.)[..., None]/5.], axis=-1)
        t = time.perf_counter()
        with torch.inference_mode():
            latent = vision(torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).to(device)).squeeze(0).cpu().numpy()
        torch.cuda.synchronize(); vision_seconds += time.perf_counter() - t
        if not np.isfinite(latent).all():
            raise RuntimeError('Non-finite vision proxy output')
        if save:
            from PIL import Image
            Image.fromarray(rgba[..., :3].astype(np.uint8)).save(OUT / 'camera_rgb.png')
            np.save(OUT / 'camera_depth.npy', depth)
            corners = np.array([[x, y, board_hi[2]] for x in [board_lo[0], board_hi[0]] for y in [board_lo[1], board_hi[1]]])
            pixels = camera.get_image_coords_from_world_points(corners)
            camera_checks['board_corner_pixels'] = np.asarray(pixels).tolist()
            camera_checks['board_in_frame'] = bool(np.all(np.asarray(pixels) > 1) and np.all(np.asarray(pixels) < a.width-1))
            write('camera_checks.json', camera_checks)
        return True

    def observation():
        q = robot.get_joint_positions(); qd = robot.get_joint_velocities()
        raw = np.r_[q[independent] - home[independent], qd[independent], previous_action, latent if a.camera else []].astype(np.float32)
        moments.observe(raw)
        normalized = np.clip((raw - moments.mean) / np.sqrt(moments.m2/max(1, moments.count-1)+.01), -5., 5.).astype(np.float32)
        return torch.as_tensor(normalized, device=device)

    reset()
    for _ in range(120):
        robot.apply_action(ArticulationAction(joint_positions=target)); world.step(render=False)
    if camera:
        for _ in range(30):
            world.step(render=False)
            if camera_read():
                break
        if not camera_read(save=True):
            raise RuntimeError('Camera failed to initialise')
        if not camera_checks['board_in_frame']:
            raise RuntimeError('Camera does not contain the whole board')
    start = time.monotonic(); last_status = start; last_checkpoint = start
    rollout = []; observation_tensor = observation(); local_updates = 0
    # Small fixed update budget distributed across the soak; never a full training run.
    update_interval = max(0., (a.seconds - 5) / max(1, a.max_updates))
    next_update = start; all_losses = []; next_reset = 64
    progress = (OUT / 'progress.jsonl').open('w', buffering=1)
    stopped_for_reserve = False
    try:
        while time.monotonic() - start < a.seconds:
            with torch.no_grad():
                action, logp, value, _ = policy.evaluate(observation_tensor)
            bounded = action.clamp(-1, 1).detach().cpu().numpy()
            desired = np.clip(home[independent] + bounded * .015, lower + .0001, upper - .0001)
            target[independent] += np.clip(desired-target[independent], -.002, .002)
            if not np.isfinite(target).all():
                raise RuntimeError('Non-finite command')
            t = time.perf_counter()
            for _ in range(12):
                robot.apply_action(ArticulationAction(joint_positions=target)); world.step(render=False); physics_steps += 1
            physics_seconds += time.perf_counter() - t
            q = robot.get_joint_positions(); qd = robot.get_joint_velocities()
            if not np.isfinite(q).all() or not np.isfinite(qd).all():
                raise RuntimeError('Non-finite physical state')
            speed = float(np.max(np.abs(qd))); max_speed = max(max_speed, speed)
            drift = float(np.max(np.abs(q[left]-home[left]))); max_left_drift = max(max_left_drift, drift)
            tracking = float(np.max(np.abs(q[independent]-target[independent]))); max_tracking_error = max(max_tracking_error, tracking)
            if speed > 3. or drift > math.radians(3) or tracking > math.radians(12):
                raise RuntimeError(f'Physical guard: speed={speed}, parked drift={drift}, tracking={tracking}')
            for follower in audit['right_hand_followers']:
                master_path = next(iter(follower['mimic_relationships'].values()))[0]
                master = master_path.split('/')[-1]
                ratio = 1.86 if 'thumb' in follower['name'] else .89
                max_mimic_error = max(max_mimic_error, abs(float(q[names.index(follower['name'])]-ratio*q[names.index(master)])))
            pos, _ = knife.get_world_pose()
            if not np.isfinite(pos).all() or pos[2] < board_hi[2]-.04:
                raise RuntimeError('Knife fell through/off the supporting board during resource probe')
            if camera:
                if not camera_read():
                    raise RuntimeError('Camera frame disappeared')
            control_steps += 1; previous_action = bounded.astype(np.float32)
            done = control_steps >= next_reset
            next_observation = observation()
            # Surrogate posture reward deliberately has no grasp success term.
            reward = -float(np.square((q[independent]-home[independent])/.015).mean())
            if local_updates < a.max_updates and time.monotonic() >= next_update:
                rollout.append((observation_tensor.detach(), action.detach(), logp.detach(), torch.tensor(reward, device=device), value.detach(), torch.tensor(float(done), device=device)))
                counts['transitions'] += 1
            if len(rollout) == 64:
                with torch.no_grad():
                    _, _, nv, _ = policy.evaluate(next_observation)
                t = time.perf_counter(); losses = ppo_update(policy, optimizer, rollout, nv.detach(), device); torch.cuda.synchronize(); update_seconds += time.perf_counter()-t
                all_losses.extend(losses); rollout.clear(); local_updates += 1; counts['updates'] += 1; next_update = time.monotonic()+update_interval
            if done:
                reset(); next_reset = control_steps+64; next_observation = observation()
            observation_tensor = next_observation
            now = time.monotonic()
            counters = dict(counts)
            if now-last_checkpoint >= 30 or (OUT/'checkpoint_and_stop.request').exists():
                save_checkpoint(OUT/'checkpoint.pt', policy, optimizer, vision, moments, counters, reset_rng, config); last_checkpoint = now
            if (OUT/'checkpoint_and_stop.request').exists():
                stopped_for_reserve = True; break
            if now-last_status >= 10:
                row = {'elapsed_s': now-start, 'physics_steps': physics_steps, 'control_steps': control_steps,
                       'resets': reset_count, 'updates_this_run': local_updates, 'render_frames': render_count,
                       'cuda_allocated_mib': torch.cuda.memory_allocated()/1024**2,
                       'cuda_reserved_mib': torch.cuda.memory_reserved()/1024**2}
                progress.write(json.dumps(row)+'\n'); write('status.json', row); print('BENCH_PROGRESS', json.dumps(row), flush=True); last_status = now
        save_checkpoint(OUT/'checkpoint.pt', policy, optimizer, vision, moments, counts.copy(), reset_rng, config)
    finally:
        progress.close()
    elapsed = time.monotonic()-start
    weight_delta = float((torch.cat([v.detach().flatten() for v in policy.parameters()])-first_weights).abs().max())
    saved = torch.load(OUT/'checkpoint.pt', map_location=device, weights_only=False)
    restored = ProbePolicy(observation_size, 13).to(device); restored.load_state_dict(saved['policy'])
    with torch.no_grad():
        expected = torch.cat([v.flatten() for v in policy.parameters()]); actual = torch.cat([v.flatten() for v in restored.parameters()])
    roundtrip = bool(torch.equal(expected, actual) and saved['counters']==counts and saved['normalization']['count']==moments.count and
                     np.array_equal(saved['normalization']['mean'], moments.mean) and np.array_equal(saved['normalization']['m2'], moments.m2))
    if camera:
        camera_read(save=True); write('camera_checks.json', camera_checks)
    passed = bool(not stopped_for_reserve and elapsed >= a.seconds and local_updates >= 1 and reset_count >= 2 and weight_delta > 0 and roundtrip and
                  (not camera or (camera_checks['board_in_frame'] and camera_checks.get('distinct_timestamps', 0) >= 10)))
    result = {'passed': passed, 'scope': 'Resource feasibility only; posture-surrogate PPO and untrained vision encoder. No knife skill learned or evaluated.',
              'elapsed_test_wall_s': elapsed, 'physics_steps': physics_steps, 'control_steps': control_steps,
              'simulated_seconds': physics_steps/240, 'physics_steps_per_wall_s': physics_steps/elapsed,
              'action_steps_per_wall_s': control_steps/elapsed, 'reset_count': reset_count,
              'updates_this_run': local_updates, 'total_learner_updates': counts['updates'], 'transitions_this_run': counts['transitions']-initial_transitions,
              'initial_learner_updates': initial_updates, 'checkpoint_roundtrip': roundtrip, 'resume_checks': resume_checks,
              'max_parameter_change': weight_delta, 'losses_finite': all(np.isfinite(all_losses)),
              'physics_seconds': physics_seconds, 'render_seconds': camera_seconds, 'encoder_seconds': vision_seconds,
              'ppo_update_seconds': update_seconds, 'camera_frames': render_count, 'camera_checks': camera_checks,
              'max_camera_age_sim_s': max(camera_age, default=0.),
              'max_joint_speed_rad_s': max_speed, 'max_parked_joint_drift_rad': max_left_drift,
              'max_tracking_error_rad': max_tracking_error, 'max_mimic_residual_rad': max_mimic_error,
              'cuda_peak_allocated_mib': torch.cuda.max_memory_allocated()/1024**2,
              'cuda_peak_reserved_mib': torch.cuda.max_memory_reserved()/1024**2,
              'stopped_for_reserve': stopped_for_reserve, 'configuration': config,
              'remaining_gaps': ['Core World harness is not yet a native Isaac Lab DirectRLEnv', 'Vision proxy is untrained and produces no knife pose',
                                 'Self-collision disabled', 'Small-motion resource probe does not validate grasp contact dynamics',
                                 'Later teacher/perception workloads may require more memory']}
    write('result.json', result); print('BENCH_RESULT', json.dumps(result), flush=True)
    if not passed:
        raise RuntimeError('Benchmark acceptance failed')


if __name__ == '__main__':
    app = None
    try:
        from isaacsim import SimulationApp
        app = SimulationApp({'headless': True, 'width': 128, 'height': 128, 'anti_aliasing': 0, 'renderer': 'RaytracedLighting'})
        main(app)
    except BaseException as exc:
        write('failure.json', {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()})
        traceback.print_exc(); print('BENCH_FAILED', str(exc), flush=True)
        raise
    finally:
        if app:
            app.close()
