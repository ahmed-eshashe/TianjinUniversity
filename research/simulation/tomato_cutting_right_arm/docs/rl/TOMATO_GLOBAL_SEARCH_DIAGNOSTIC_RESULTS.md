# Contact-cycle diagnosis and bounded numerical guess test

25 October 2026, 22:28 UTC. Offline quasistatic model only.

## Verified progress

The last independently accepted insertion is **8.828125 mm**, at `runs/offline/tomato_curvature_search_01/insertion07_refined/attempt008`. Two of 47 patches have completely failed. Forty-five still connect the two pieces; the material graph remains one component. This is not a full cut or independent slice release.

Actual force residual is 1.37669206e-08, physical stability eigenvalue 0.00178794258 (required >=1e-6), work-balance error 0.057854%, and swept blade gap -2.49800181e-16 m (required >=-1e-9). The worker and independent auditor both pass. Model laws and all physical acceptance thresholds are unchanged.

## What stalled

At the larger 8.84375 mm target, the old numerical search repeatedly released then re-added contact row57. All ten candidate chunks have exactly the same position-file hash. This is a numerical bookkeeping cycle; it does not establish physical instability. Evidence and exact source/candidate digests are in `runs/offline/tomato_global_search_01/contact_cycle_diagnostic.json`.

The suspected cause is that a reduced-space search shift changes when the contact set changes, so the numerical quadratic and predicted normal loads can change even at identical positions. This explanation remains a numerical hypothesis; the repeated cycle itself is confirmed.

## Separate numerical guess method

`rl/tomato_contact_global_search.py` constructs its numerical search matrix over all support-free degrees of freedom, independently of active contact selection, retaining off-diagonal coupling. Its normal-load prediction uses the same numerical matrix as its direction. This is only a numerical matrix: stored physical energy, force and Hessian are unchanged. It is not physical stiffness, damping or a constitutive change, and its eigenvalues are not the physical stability acceptance calculation.

All **143 combined regression tests pass**, including the earlier132. In a frozen uncommitted damage diagnostic, six iterations break the repeated two-set cycle and acquire other contacts. Thirty iterations reduce the independently fitted current force residual from 0.374552715 to 2.10747648e-05, while energy falls from 0.0054724616907960736 to 0.0054724554436974913 J. This guess is still unconverged and is never accepted as a physical state. Diagnostic runtime 7.538s, high-water RSS 212.957 MiB.

A verified adapter passes only positions, contact bookkeeping and the same explicitly provisional trial damage to the unchanged v3 worker, anchored to the same real accepted predecessor. No reactions, work or failed history are transferred. The usual worker then recomputes damage eligibility and consistency from committed history and performs every original physical check. The new search is not installed as a new physical backend.

## Why the converged larger step was rejected

The unmodified v3 worker converges at8.84375 mm, but its interpolated path has swept penetration 32.805441 nanometres, above the unchanged1 nanometre allowance. The final polygon itself is clear to roundoff. Passing equilibrium, energy and physical stability cannot override a failed path-contact test. This endpoint remains rejected with its positions, history and work uncommitted.

Halving the actual insertion interval from the last accepted8.8125 mm state produces an independently passing8.828125 mm endpoint. The rejected larger step is not repaired or relabelled. The two-step path must be checked again before the previously rejected depth can be reached.

## Preserved safeguards and next step

Original250-file/241-file manifests, prior seven-file/five-file and v3 four-file qualified source snapshots all pass. The seven archived v3 helpers and the new global-source snapshot also match. Peak coupled-worker RSS this cohort is 216.270 MiB, below the unchanged512 MiB address-space cap. CPU45s, alarm55s, parent timeout60s, one thread, shared locks, quota lease and hard deadline remain active. No simulator import/launch, training, installation, controller, material or grasp-criterion changes.

Next bounded step: target8.84375 mm from the NEW qualified8.828125 checkpoint using the v3 positions-only predictor. If the swept path fails, refine that interval again without accepting or repairing a failed state. If contact bookkeeping cycles, diagnose and create a target-specific, source-verified uncommitted guess; the current hard-coded global seed applies only to its original8.8125 predecessor/8.84375 target and must not be reused after the predecessor changes.
