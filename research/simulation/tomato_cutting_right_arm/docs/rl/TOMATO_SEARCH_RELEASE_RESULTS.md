# Offline contact-release search correction

The original search stopped at 8.375 mm insertion. The new numerical search now independently qualifies through **8.75 mm**. **121 tests pass**, including all previous 111 regressions and ten checks of the new search. No physical model, controller, material or acceptance limit was changed.

## What went wrong

A solver searches for positions that balance all forces while satisfying unilateral contacts. A temporary search position is not yet a physical result. At the failing position, four contacts had attractive predicted loads and needed release. Removing them exposed one negative search-matrix diagonal (-0.60355 N/m), making the old Newton search unsuitable. The original worker stopped safely instead of accepting that state. The diagnostic reproduces the problem and retains the released row identities.

This did not prove physical tomato collapse: the last accepted 8.3125 mm state passed its exact physical stability check. Three earlier continuation attempts, including smaller-step and unpredicted controls, were rejected.

## What changed

The separately versioned search uses the original physical Newton matrix whenever suitable. If the matrix has a nonpositive search diagonal, the iterative search solve fails, or the Newton direction increases energy, it switches to a positive diagonal numerical search metric. That metric proposes a downhill direction subject to the same contact constraints. The line search still evaluates the **original physical energy** and rejects invalid volume/contact states. No material stiffness shift, damping, force modification or artificial dissipation is added.

In the diagnostic, the fallback adds four missing blocking contacts and then returns to physical Newton steps. The independently evaluated physical tangent is never replaced by the search matrix. KKT force balance alone cannot establish physical stability, so every endpoint still needs the unchanged physical eigenvalue test and independent audit.

The new backend is `triangle_search_evolving_v1`. A same-depth source-transition checkpoint at 8.3125 mm verifies the entire original source/state provenance and reproduces exactly the original stored energy and damage/opening history. Subsequent endpoints inherit the real insertion work and fracture history; none imports the separately tested withdrawal/reclosure states.

## Verified evidence

| Check | Result |
| --- | --- |
| Independently audited new-backend endpoints, including transition hold | 7 |
| Latest insertion | 8.75 mm |
| Damaged patches / fully failed patches | 5 / 0 of 47 |
| Maximum damage D | 0.9976220064 |
| Material components | 1 |
| Maximum cumulative work error | 0.064872% (unchanged limit 1%) |
| Minimum swept blade gap | -8.25728e-16 m (unchanged tolerance -1e-9 m) |
| Minimum physical stability eigenvalue | 1.521e-05 (unchanged floor 1e-6) |
| Peak numerical-worker RSS, including uncommitted chunks | 207.10 MiB |

Last accepted checkpoint: `runs/offline/tomato_optimizer_release_01/search_batch06_mode_retry/attempt001_01`. Every acceptance recomputes force balance, unilateral contact/complementarity, exact swept triangle contact, volume and surface validity, irreversible damage consistency, exact fracture loss, cumulative/incremental work and material connectivity. The independent auditor imports the original physical model and never uses the numerical search metric for stability.

The analytic tests include a concave interior direction that reaches a valid constrained boundary minimum, and an indefinite matrix with positive diagonals whose Newton direction ascends. They verify the actual unchanged model energy and Hessian. The same eight earlier contact-optimizer regressions also run against the new search.

## Physical-stability rejection and same-pose restart

The first converged 8.75 mm state failed the original stability floor. Independent recomputation confirmed a normalized eigenvalue -1.1464e-6, including with damage held fixed. It remained rejected. The mode localized near outer slice nodes 1009–1011, away from the guided cut face; neither direction violated the weak contact inequalities. This is a surface mode in the present uncalibrated model, not a measured real-tomato instability.

Directional gradient differences converge to the analytic curvature: at a 3 nm difference step, relative error is about 0.0127%. Direct second differences of total energy become dominated by cancellation at these tiny steps and were not used as the derivative proof. A 10 micrometre guess increased actual model energy and was rejected. A two-micrometre guess in the other direction lowered energy while preserving contact, support positions and admissible volume. This was only a numerical starting estimate; it did not impose a physical push or commit the rejected state.

A retry at the SAME blade depth, with physical history and work anchored to the independently accepted 8.6875 mm predecessor, then passed every original gate. Its force residual was 1.67e-8 and independently checked physical stability eigenvalue 1.5210e-5, above the unchanged 1e-6 floor. Uncommitted damage from the earlier solve was only an optimization seed; the worker recomputed consistency and irreversibility from the real predecessor before acceptance. The rejected saddle and its audits remain intact. This is a quasistatic equilibrium correction, not validation of a dynamic buckling transient.

The workflow records any unresolved stability frontier and forbids ordinary deeper continuation beyond it. A documented same-pose curvature restart can be tested, but only a NEW independently passing physical state at that depth resolves the frontier. A negative numerical metric or a failed physical audit is never silently converted into a pass.

## Safeguards and limits

Original 250-file and pre-session 241-file preservation manifests and the seven qualified withdrawal/reclosure source snapshots remain unchanged. Workers are serial, hold the original shared lock, use one BLAS thread, and retain 512 MiB address-space, 45 s CPU, 55 s wall and 60 s parent limits. The batch launcher has a twelve-mechanical-call cap, fresh quota lease, orchestration lock and overnight hard deadline. Quota checks remain account-wide and cannot reserve usage consumed by other chats.

This is the same uncalibrated, guided, quasistatic spring/volume/cohesive model, not a native Newton/Isaac simulation or a trained robot. No simulator/native-engine imports or launch, training, dependency installation, controller edits or relaxed grasp/memory/physical criteria occur. There is still **no qualified full cut or independent slice release**.

## Later bounded attempts remain uncommitted

After the stable 8.75 mm checkpoint, nominal insertion steps to 8.8125 mm and 8.78125 mm each reached the twelve-call batch budget without convergence. These are not physical results and did not advance damage history. An independent current-force fit gives residual 3.45e-5 for the first stalled candidate, so its failure is not merely inaccurate predicted contact multipliers.

The smaller-step candidate also has a genuine search-space negative eigenvalue (-0.00067869) despite all reduced matrix diagonals being positive (minimum 7.20 N/m). This is a numerical search-space diagnostic, not a physical endpoint audit. The fallback then relies on diagonal descent and converges too slowly. A five-micrometre, energy-screened curvature restart lowered real model energy by 2.43e-11 J while preserving contact, support, volume and surface validity, but its following bounded solve still did not qualify. All those candidates remain separate from physical history.

The next numerical task is a better curvature-aware constrained search that retains off-diagonal stiffness coupling—for example a truncated-Newton or spectrally safeguarded numerical search matrix—tested in a NEW source version. A shift in a search matrix must never alter physical material stiffness, energy, forces, damage, work or the independently checked physical tangent. Do not repeatedly spend the same batch budget on unchanged stalled configurations, relax tolerances, or force rupture. Scalar-law feasibility is not the current blocker: the synthetic failure separation is 4 mm and the unchanged finite blade thickness cap is about 7.61 mm, but full coupled-cut feasibility still requires its actual contact/damage/release tests.

## Continue from here

Read `runs/offline/tomato_optimizer_release_01/qualification.json`, the latest `search_batch*/status.json` and `docs/rl/OVERNIGHT_PROGRESS.md`. Check actual UTC/quota and refresh the shared lease before each bounded batch. Use `run_search_probe.py` with this backend, fresh output names and the latest independently audited checkpoint; the old v1 launcher cannot continue the new source version. Keep candidates separate from physical history and audit every accepted endpoint. Do not edit qualified source files in place.

Continue deeper cutting only while all physical checks pass. Complete failure of all 47 patches, two material components, actual blade clearance, independent slice motion and nonpenetrating reclosure without healing remain separate requirements. Depth alone is never cutting success.
