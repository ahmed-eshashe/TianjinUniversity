# Phase 2 local resource feasibility results

Scope: one minimal robot, board, countertop and free kitchen knife; CPU PhysX, GPU PyTorch, one RGB-D camera and an untrained small image encoder. The PPO workload uses a posture reward and small joint offsets. It does not teach or test knife pickup.

## Decision

GO for the measured one-environment Core/PyTorch prototype only; full grasp training remains gated by Phase 3, native Isaac Lab integration and dependency assessment

| Probe | Test duration | Resets | Small PPO updates | Peak process RAM | Minimum available RAM | Peak total GPU use |
| --- | --- | --- | --- | --- | --- | --- |
| State only | 60.0 s | 11 | 3 | 7.522 GB | 4.785 GB | 2045 MiB |
| Camera pilot | 30.1 s | 5 | 2 | 7.755 GB | 4.613 GB | 2503 MiB |
| Camera stability and resume | 1800.1 s | 277 | 12 | 7.747 GB | 4.466 GB | 2658 MiB |

## Stability and resume

The long test ran for 1800.1 measured seconds, excluding simulator startup. Checkpoint restoration loaded 2 prior small updates, restored optimizer state, observation statistics, resource-probe curriculum marker and Python/NumPy/PyTorch/CUDA/reset-generator states. RNG equality was checked immediately after restoration. It then began a fresh physical episode; this is not an exact replay of in-flight contact solver state.

Final checkpoint round-trip: True. Current final-run source/scene hashes match the recorded configuration: True. Original accepted baseline hashes remain unchanged: True.

A subsequent deliberately injected checkpoint request tested the early-stop path with ample memory, then resumed for 15 seconds using the final stricter startup budget. Graceful stop/resume check passed: True. See `graceful_resume_checks.json`; its intentional incomplete stop is not a simulator crash or a passed soak.

Post-warmup memory comparison: {"rss_growth_mib": 21.876953125, "gpu_used_growth_mib": -18.0}. This compares median readings from 130–430 seconds with the last five minutes. The preselected reporting threshold is at most 256 MiB growth for either process RAM or total GPU use. Pass: True. Available host RAM and free VRAM must also retain the watchdog reserves throughout; see `memory_report.json` and the full resource trace.

## Measured configuration and speed

- One environment, CPU PhysX at 240 simulated Hz.
- One 128 by 128 RGB-D view, requested 20 simulated Hz, 24 mm focal length, square pixels.
- GPU inference with an untrained compact RGB-D encoder; no knife localisation accuracy claimed.
- GPU 64 by 64 tanh actor/critic, 64-transition rollout and two PPO epochs per update.
- Independent-joint offsets limited to 0.015 rad around the ready posture, with 0.002 rad per-control-step target slew.
- Measured action throughput: 9.83 steps per wall-clock second. This is workload throughput, not a prediction of learning convergence.
- Recorded timing totals: {"physics_seconds": 1433.5898676369616, "render_seconds": 273.3524675926383, "encoder_seconds": 34.13540086097055, "ppo_update_seconds": 0.37695048700697953}.
- Maximum passive mimic residual: 2.27e-07 rad in this small-motion test.

A million action steps at this measured rate would take approximately 28.3 hours in this specific harness. The eventual task, learning budget and any native vectorized/GPU physics configuration have not been benchmarked. Do not promise a pickup-training duration from this projection.

## Safeguards and limitations

The same single-instance lock as the old controllers is used. The final wrapper requires **10 GB available host RAM and 4 GiB free VRAM before startup**, derived from the measured incremental load plus reserve. This is stricter than the original startup floor. Runtime GPU thresholds remain 1.5 GiB warning and 1 GiB hard stop. Reserve tests and live lock refusal are recorded separately.

Original Linux units are 5,000,000 kB startup floor, 3,000,000 kB warning and 2,000,000 kB stop (5.12, 3.072 and 2.048 decimal GB). The first new wrapper used decimal GB; this small conversion difference was corrected during the soak, with an additional strict host monitor applied to the in-flight run. Every resource sample, including those before the correction, also retained the stricter runtime reserves: True. `guard_unit_correction.json` and `strict_host_monitor.json` preserve this detail. The launch wrapper and final wrapper are stored separately in the source snapshot; the tested child workload did not change. The subsequent stop/resume check uses the final, stricter startup budget.

No additional environments were enabled. The selected one-environment workload fits, but multiple environments and future perception training may consume more memory. Native Isaac Lab DirectRLEnv and its selected RL adapter require their own integration/resource test. Package consistency issues remain in `dependency_check.txt`; this result does not certify the entire installed environment.

Self-collision is disabled, contact parameters are provisional, and small posture movements do not validate a physical grasp. These remain Phase 3 work. The knife uses its original kitchen geometry and begins over the board centre, with physical reset/settling checks. It is not attached or moved directly inside an episode. The full kitchen and hardware are outside this benchmark.

## Evidence

- `docs/rl/phase2_summary.json`: numerical decision and comparison.
- `docs/rl/minimal_scene_checks.json`: source geometry, knife count, attachment and board checks.
- `docs/rl/safeguard_checks.json`: guard tests and concurrent-controller refusal.
- `docs/rl/graceful_resume_checks.json`: deliberate checkpoint stop followed by a successful short resume.
- `docs/rl/phase2_resources.png`: complete RAM/VRAM trace.
- `runs/rl/phase2/camera_soak_30min_01/`: configuration, source hashes, logs, resource trace, checkpoint, camera image/depth and result.
- `rl/README.md`: bounded commands, output meanings and stop/resume instructions.

Stop after this report. Full training and further project phases have not been authorized.
