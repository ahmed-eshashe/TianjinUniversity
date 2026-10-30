# First-complete-patch-failure insertion-step comparison

Prepared 25 October 2026, 23:48 UTC. Bounded offline numerical work only. This is a local quasistatic insertion-step check, not native simulation timestep convergence, material calibration or RL.

The main path now independently passes 8.84375 mm using refined contact-safe segments. Two of 47 patches have fully failed. The earlier comparison at 3.40625–4 mm covered damage initiation, with no complete patch failures. It does not test insertion-step sensitivity of these new complete failures. Run this small paired comparison before extending the main path farther.

## Fixed baseline and separate branches

Use the exactly saved v3 hold at `runs/offline/tomato_curvature_search_01/transition_hold/attempt001`, depth 8.75 mm. Verify its summary/state/source hashes and passing independent audit. It already has committed partial damage; both paths must share precisely that history, supports, material, mesh and blade.

The existing coarse path is `insertion03_seeded/attempt002` at 8.78125 mm, then `insertion04_predicted/attempt008` at 8.8125 mm: two 0.03125 mm steps from the common baseline. Their source/state hashes and independent audits are recorded in `runs/offline/tomato_first_failure_refinement_01/plan.json`.

Create a separately labelled fine branch using targets 8.765625, 8.78125, 8.796875 and 8.8125 mm: four 0.015625 mm steps. Use NEW batch names such as `failure_half01_predicted`. Each physical predecessor must be the fine branch’s preceding ACCEPTED checkpoint. Never concatenate its work/history into the already accepted deeper main path. The main checkpoint remains `insertion26_small_global/attempt004` at 8.84375 mm.

## Bounded execution

Before each short session read actual UTC/quota, check both locks and existing source snapshots. Refresh the actual quota lease before numerical work. Use the unchanged cycle-guarded v3 launcher and positions-only predictor. First target is 8.765625 mm from the common 8.75 mm hold. On an identical restart, the existing target-specific frozen-guess helper may provide an UNCOMMITTED guess from that stopped candidate, tied to the SAME actual predecessor and target. No damage/work prediction or physical source change is allowed.

Every new endpoint must pass original equilibrium, multiplier/contact, exact swept-path, volume, surface, support, loading-side physical stability, work and irreversibility checks plus the independent auditor and source/state qualification. Never bypass an unresolved physical stability frontier. If a path segment fails, refine it and retain the rejection; report the actual additional step sequence. Resource/quota refusal stops the batch. Preserve 512 MiB address space, 45 CPU seconds, 55 s alarm, 60 s parent timeout, one thread, shared locks and at most 12 calls per batch. No simulator/native imports, training, installs, controller or physical-law changes.

## Comparison and success reporting

Compute the local fracture-work ledger separately for each path from the common baseline: change in accumulated blade work minus change in stored energy minus change in fracture dissipation. Normalize by positive local fracture dissipation and retain the existing shallow fracture-specific 1% target, with 1e-12 J absolute allowance. This supplements every original per-endpoint gate; it cannot override one. Treat a zero local fracture denominator as an inconclusive fracture comparison, not an automatic pass.

At 8.78125 and 8.8125 mm compare all 47 damages and histories, fully failed patch IDs/counts, topology, blade resistance, stored energy, fracture loss and cumulative work relative to the baseline. Report actual differences and coarse/fine fracture-work errors, sampled peak blade force, added sample locations and first-full-failure brackets. Do not invent a cross-path damage tolerance or claim exact identity without measuring it. The plan’s broader 10% load/work resolution target remains a provisional research target; it never relaxes the original 1% energy or force/contact/stability gates. A pass of the local energy gates alone is not full spatial, temporal or physical convergence.

Keep failures and alternate equilibria visible. If refinement exposes a physical stability/contact failure or substantive nonconvergence, investigate before deeper insertion; do not average it away or delete the candidate. A later interrupted withdrawal/reclosure check with fully broken patches also remains distinct from the older partial-damage validation. Neither this comparison nor depth validates full slice separation or independent release.

After each numerical batch check quota. Run capped `qualify_seed_provenance.py` (including the preserved original qualifier), then `write_results.py`; retain the main and comparison checkpoints as separate handoff fields. Hard deadline and 45%-used stop remain unchanged.
