"""Summarise completed bounded probes; never starts a simulator or training."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def summarise(folder):
    result = read(folder/'result.json'); memory = read(folder/'memory_report.json')
    rows = [json.loads(x) for x in (folder/'resources.jsonl').read_text().splitlines()]
    valid = [x for x in rows if x['rss_bytes'] > 0]
    early = [x for x in valid if 130 <= x['wall_s'] <= 430]
    late = [x for x in valid if x['wall_s'] >= max(130, valid[-1]['wall_s']-300)]
    growth = None
    if early and late and result['elapsed_test_wall_s'] >= 1800:
        growth = {key.replace('_bytes', '_growth_mib'): (statistics.median(x[key] for x in late)-statistics.median(x[key] for x in early))/1024**2 for key in ['rss_bytes','gpu_used_bytes']}
    hashes_match = all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha for path,sha in result['configuration']['hashes'].items())
    return {'path': str(folder.relative_to(ROOT)), 'passed': result['passed'], 'memory': memory,
            'duration_s': result['elapsed_test_wall_s'], 'physics_steps': result['physics_steps'],
            'control_steps_per_s': result['action_steps_per_wall_s'], 'resets': result['reset_count'],
            'updates': result['updates_this_run'], 'checkpoint_roundtrip': result['checkpoint_roundtrip'],
            'resume_checks': result['resume_checks'], 'camera_frames': result['camera_frames'],
            'configuration_hashes_match_current_files': hashes_match, 'post_warmup_memory_growth': growth,
            'timing_s': {k:result[k] for k in ['physics_seconds','render_seconds','encoder_seconds','ppo_update_seconds']},
            'max_mimic_residual_rad': result['max_mimic_residual_rad'], 'configuration': result['configuration']}


def main():
    p = argparse.ArgumentParser();p.add_argument('--soak', default='runs/rl/phase2/camera_soak_30min_01');a=p.parse_args()
    soak = summarise(ROOT/a.soak)
    state = summarise(ROOT/'runs/rl/phase2/state_smoke_01')
    camera = summarise(ROOT/'runs/rl/phase2/camera_smoke_03')
    growth = soak['post_warmup_memory_growth']
    stability = bool(growth and growth['rss_growth_mib'] <= 256 and growth['gpu_used_growth_mib'] <= 256)
    inventory = read(ROOT/'docs/rl/phase1_inventory.json')
    safeguard_checks = read(ROOT/'docs/rl/safeguard_checks.json')
    stop_file = ROOT/'docs/rl/graceful_resume_checks.json'
    graceful_checks = read(stop_file) if stop_file.exists() else {'passed': False}
    reserves = all(x['available_ram_bytes'] >= 3_000_000*1024 and x['gpu_free_bytes'] >= 1536*1024**2
                   for x in (json.loads(line) for line in (ROOT/a.soak/'resources.jsonl').read_text().splitlines()))
    preserved = all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha for path,sha in inventory['baseline_sha256'].items())
    scope_passed = bool(soak['passed'] and soak['duration_s'] >= 1800 and soak['memory']['reason']=='normal exit' and
                        not soak['memory']['warning_requested'] and soak['memory']['child_exit_code']==0 and
                        stability and reserves and safeguard_checks['passed'] and graceful_checks['passed'] and soak['configuration_hashes_match_current_files'] and
                        soak['resume_checks'].get('rng_restored') and preserved)
    summary = {'resource_probe_passed':scope_passed, 'state_probe':state, 'camera_pilot':camera, 'camera_soak':soak,
               'post_warmup_growth_threshold_mib':256, 'post_warmup_growth_check_passed':stability,
               'accepted_baselines_preserved':preserved, 'exact_original_reserves_retained':reserves,
               'safeguard_checks':safeguard_checks, 'graceful_stop_resume_checks':graceful_checks,
               'decision':'GO for the measured one-environment Core/PyTorch prototype only; full grasp training remains gated by Phase 3, native Isaac Lab integration and dependency assessment' if scope_passed else 'NO GO: investigate the failed resource/stability checks before advancing',
               'not_established':['knife pickup skill','trained vision model','native Isaac Lab task/adapter compatibility',
                                  'multiple environments','GPU physics throughput','physical robot/tactile interfaces','self-collision readiness']}
    (ROOT/'docs/rl/phase2_summary.json').write_text(json.dumps(summary,indent=2))
    # Preserve the exact current probe sources after verifying the final run hashes.
    if soak['configuration_hashes_match_current_files']:
        target = ROOT/a.soak/'source_snapshot'; target.mkdir(exist_ok=True)
        for relative in ['rl/benchmark.py','rl/probe_policy.py','rl/guard_benchmark.py','rl/prepare_benchmark_scene.py']:
            (target/Path(relative).name).write_bytes((ROOT/relative).read_bytes())
    text = '''# Phase 2 local resource feasibility results

Scope: one minimal robot, board, countertop and free kitchen knife; CPU PhysX, GPU PyTorch, one RGB-D camera and an untrained small image encoder. The PPO workload uses a posture reward and small joint offsets. It does not teach or test knife pickup.

## Decision

'''+summary['decision']+'\n\n'
    text += '| Probe | Test duration | Resets | Small PPO updates | Peak process RAM | Minimum available RAM | Peak total GPU use |\n| --- | --- | --- | --- | --- | --- | --- |\n'
    for label,x in [('State only',state),('Camera pilot',camera),('Camera stability and resume',soak)]:
        m=x['memory'];text+=f"| {label} | {x['duration_s']:.1f} s | {x['resets']} | {x['updates']} | {m['peak_rss_gb']:.3f} GB | {m['min_available_ram_gb']:.3f} GB | {m['peak_gpu_used_mib']:.0f} MiB |\n"
    text += f'''
## Stability and resume

The long test ran for {soak['duration_s']:.1f} measured seconds, excluding simulator startup. Checkpoint restoration loaded {soak['resume_checks'].get('prior_updates',0)} prior small updates, restored optimizer state, observation statistics, resource-probe curriculum marker and Python/NumPy/PyTorch/CUDA/reset-generator states. RNG equality was checked immediately after restoration. It then began a fresh physical episode; this is not an exact replay of in-flight contact solver state.

Final checkpoint round-trip: {soak['checkpoint_roundtrip']}. Current final-run source/scene hashes match the recorded configuration: {soak['configuration_hashes_match_current_files']}. Original accepted baseline hashes remain unchanged: {preserved}.

A subsequent deliberately injected checkpoint request tested the early-stop path with ample memory, then resumed for 15 seconds using the final stricter startup budget. Graceful stop/resume check passed: {graceful_checks['passed']}. See `graceful_resume_checks.json`; its intentional incomplete stop is not a simulator crash or a passed soak.

Post-warmup memory comparison: {json.dumps(growth)}. This compares median readings from 130–430 seconds with the last five minutes. The preselected reporting threshold is at most 256 MiB growth for either process RAM or total GPU use. Pass: {stability}. Available host RAM and free VRAM must also retain the watchdog reserves throughout; see `memory_report.json` and the full resource trace.

## Measured configuration and speed

- One environment, CPU PhysX at 240 simulated Hz.
- One 128 by 128 RGB-D view, requested 20 simulated Hz, 24 mm focal length, square pixels.
- GPU inference with an untrained compact RGB-D encoder; no knife localisation accuracy claimed.
- GPU 64 by 64 tanh actor/critic, 64-transition rollout and two PPO epochs per update.
- Independent-joint offsets limited to 0.015 rad around the ready posture, with 0.002 rad per-control-step target slew.
- Measured action throughput: {soak['control_steps_per_s']:.2f} steps per wall-clock second. This is workload throughput, not a prediction of learning convergence.
- Recorded timing totals: {json.dumps(soak['timing_s'])}.
- Maximum passive mimic residual: {soak['max_mimic_residual_rad']:.3g} rad in this small-motion test.

A million action steps at this measured rate would take approximately {1_000_000/max(1e-9,soak['control_steps_per_s'])/3600:.1f} hours in this specific harness. The eventual task, learning budget and any native vectorized/GPU physics configuration have not been benchmarked. Do not promise a pickup-training duration from this projection.

## Safeguards and limitations

The same single-instance lock as the old controllers is used. The final wrapper requires **10 GB available host RAM and 4 GiB free VRAM before startup**, derived from the measured incremental load plus reserve. This is stricter than the original startup floor. Runtime GPU thresholds remain 1.5 GiB warning and 1 GiB hard stop. Reserve tests and live lock refusal are recorded separately.

Original Linux units are 5,000,000 kB startup floor, 3,000,000 kB warning and 2,000,000 kB stop (5.12, 3.072 and 2.048 decimal GB). The first new wrapper used decimal GB; this small conversion difference was corrected during the soak, with an additional strict host monitor applied to the in-flight run. Every resource sample, including those before the correction, also retained the stricter runtime reserves: {reserves}. `guard_unit_correction.json` and `strict_host_monitor.json` preserve this detail. The launch wrapper and final wrapper are stored separately in the source snapshot; the tested child workload did not change. The subsequent stop/resume check uses the final, stricter startup budget.

No additional environments were enabled. The selected one-environment workload fits, but multiple environments and future perception training may consume more memory. Native Isaac Lab DirectRLEnv and its selected RL adapter require their own integration/resource test. Package consistency issues remain in `dependency_check.txt`; this result does not certify the entire installed environment.

Self-collision is disabled, contact parameters are provisional, and small posture movements do not validate a physical grasp. These remain Phase 3 work. The knife uses its original kitchen geometry and begins over the board centre, with physical reset/settling checks. It is not attached or moved directly inside an episode. The full kitchen and hardware are outside this benchmark.

## Evidence

- `docs/rl/phase2_summary.json`: numerical decision and comparison.
- `docs/rl/minimal_scene_checks.json`: source geometry, knife count, attachment and board checks.
- `docs/rl/safeguard_checks.json`: guard tests and concurrent-controller refusal.
- `docs/rl/graceful_resume_checks.json`: deliberate checkpoint stop followed by a successful short resume.
- `docs/rl/phase2_resources.png`: complete RAM/VRAM trace.
- `{a.soak}/`: configuration, source hashes, logs, resource trace, checkpoint, camera image/depth and result.
- `rl/README.md`: bounded commands, output meanings and stop/resume instructions.

Stop after this report. Full training and further project phases have not been authorized.
'''
    (ROOT/'docs/rl/PHASE2_RESULTS.md').write_text(text)
    print(json.dumps({'resource_probe_passed':scope_passed,'decision':summary['decision'],'growth':growth}))


if __name__=='__main__':
    main()
