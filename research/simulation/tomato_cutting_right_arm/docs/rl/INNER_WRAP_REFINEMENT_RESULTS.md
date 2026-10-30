# Inner surface grasp refinement and diagnostic logging

Two offline grip proposals now place inner finger surfaces substantially nearer the handle and meet the selected-contact geometric opposition check. **Neither is ready for pickup testing:** positive contact gaps remain and the provisional point-contact model finds no load balance. One proposal also has small confirmed handle intersections. The active grasp plan has not been replaced. There is no new physical grasp result.

The controller now records the final targets and raw contact changes needed to investigate the next bounded test. All 55 automated tests pass, including evidence-preservation and motor-target regressions. The simulator and full training remained paused throughout this work.

## Refined proposals

The first search used a 120-second optimization budget over four local starts: index/middle/ring and index/middle/little contact groups, seeded from the existing candidates. It optimized wrist pose and coupled finger angles against eligible inner exterior surfaces, palm proximity, thumb opposition, board/blade clearance and penetration penalties. Its approximate face-axis distances were used only for proposals. The two best were then polished with exact convex distances and checked independently against original exterior surfaces.

The knife pose is the existing board-supported reference used in the earlier diagnostics. These are terminal pose proposals; they do not demonstrate a route from a flat central reset. No knife transform or collision asset was changed. Finger joints stay within the existing flexion range and the same mimic coupling; thumb limits remain unchanged.

| Geometric quantity | Proposal A, index/middle/ring | Proposal B, index/middle/little |
| --- | --- | --- |
| Palm-to-handle distance | 0.183 mm | 0.648 mm |
| Thumb-to-handle distance | 0.135 mm | 0.235 mm |
| Index proximal surface distance | 0.195 mm | 0.522 mm |
| Second inner surface distance | Ring, 0.326 mm | Little, 0.460 mm |
| Middle inner surface distance | 0.662 mm | 1.964 mm |
| Selected contact radial enclosure/opposition | Both pass geometrically | Both pass geometrically |
| Hand clearance above the board plane | 9.67 mm | 9.83 mm |
| Conservative blade separation bound | 72.44 mm | 62.06 mm |

For comparison, the earlier leading candidate's middle/ring inner distances were 6.88/5.21 mm, and the earlier third candidate failed selected-contact thumb opposition. These distance improvements are geometry results, not loaded contacts or frozen-oracle success. The listed inner witnesses were independently verified to lie on original convex exterior faces, rather than an artificial face created by clipping at the 15 mm inner boundary.

Proposal A has middle/handle and ring/handle intersections with inscribed intersection radii of about 0.049/0.015 mm. These are intersection measures, not penetration depths or compliant-pad compression estimates. Proposal B has no handle intersection detected above the 1 micrometre numerical check; its face-axis lower bound alone was slightly negative, demonstrating why that lower bound must not be treated as proof of overlap. Both still have positive required contact gaps. The 1 micrometre check is numerical precision, not a new grasp-success tolerance.

Both poses are reachable by right-arm IK at the reference knife pose. Whole-robot terminal envelope checks still leave the existing decomposed arm link 5/7 ambiguities, one on each arm. No collision filter was added. Cooked shapes, full arm/environment clearance, a continuous approach route, physical settling and camera visibility remain unverified.

The conditional load model uses selected hypothetical contact witnesses, the provisional knife mass/COM, friction 0.6, an inscribed eight-ray friction cone, 0.05–10 N normal force per selected contact and existing actuator load limits. It finds no equilibrium at nominal gravity with actuator limits, or at 1.25 times gravity even with actuator limits removed. Therefore increasing motor force alone is not supported by these checks. A finite, selected point-contact model cannot reject every possible contact patch, pose or real compliant pad; its result is not global mechanical impossibility. The next endpoint refinement must explicitly consider contact normals, longitudinal load distribution and the knife's moment, in addition to proximity and radial opposition.

The approximate search plus screening took about 139 seconds. Final exact-distance polishing and screening took about 84 seconds. Geometry processes peaked at approximately 425 MB RAM with numerical threads limited to one. Early exact-distance attempts were refused by the numerical distance certificate. A separate Minkowski-boundary witness calculation now handles those grazing cases without loosening certificate tolerances; an independent known-gap test covers it. The initial refused polishing result is retained alongside the final result.

Evidence and source snapshots are under [the offline work directory](../../runs/offline/grasp_refinement_01). Principal artifacts are [initial proposals](../../runs/offline/grasp_refinement_01/refined_candidates.json), [exact-distance proposals](../../runs/offline/grasp_refinement_01/polished_candidates.json) and [surface and intersection checks](../../runs/offline/grasp_refinement_01/surface_validation.json). The previous reports and active controller target remain historical and active respectively; no new candidate was silently promoted.

## Diagnostic logging changes

[central_grasp.py](../../rl/central_grasp.py), [contact_evaluator.py](../../rl/contact_evaluator.py) and the new [grasp_diagnostics.py](../../rl/grasp_diagnostics.py) now provide:

- A bounded command trace separating the ideal projected displacement, pressure adjustment, diagnostic clipping, desired joint targets, final interpolated/limited targets and current joint state. It records FK point displacement for the final target separately from the intermediate projected residual.
- Explicit current-knife and fixed-reference-knife poses. This exposes the existing frame interpretation issue without changing the control strategy during a logging change.
- Physics-step contact diagnostics including points below the unchanged 0.05 N evidence threshold, separations, normal directions, pair counts, backend normal-force vectors and moments about the provisional knife COM.
- Friction points and vectors separately from normal contacts. The backend reuses count/index buffers, so normal diagnostics are extracted before querying friction. The two point sets are not paired by array index.
- Joint velocities, actual hand-link poses, preceding versus next applied targets, backend step counter and the location of the read relative to the simulation call. In the installed Isaac Lab source, `_apply_action` occurs before the next simulation step; live state/contact synchronization still requires physical validation.

Shape and feature IDs are not exposed by this contact API and are explicitly marked unavailable. Normal direction, separation sign and friction direction are marked uncalibrated. Backend normal moments do not claim a complete physical wrench or force-balance reconstruction. FK uses the authored passive coupling; measured link poses are recorded separately.

The prior progress field incorrectly named a displacement residual as velocity. New rolling progress names it `projected_linear_displacement_residual_m` and directs readers to the final command trace. Existing run files are untouched.

The physics trace retains at most 96 frames and the command trace at most 96 control updates. Each raw frame retains at most 96 normal points, 64 pair summaries and 96 friction points, with explicit truncation flags and aggregate counts. Name tables and integer references avoid repeated long asset paths per point. This does not increase the backend's existing contact-buffer allocation. Overflow, low-memory stops and the original physical safeguards remain enforced. Detailed logs are saved in `seating_substeps.json` and `command_diagnostics.json` when a later guarded run reaches the relevant phase.

## Verification and next gate

All **55 automated tests pass**. The additions cover exact known-distance geometry, near-grazing Minkowski witnesses, inner samples staying on original exterior surfaces, final-command FK, retained subthreshold contacts, separate friction points, bounded buffers and invalid backend indices. A mock contact backend that reuses its count buffers confirms that enabling raw diagnostics preserves all existing oracle-facing fields. Regression tests execute the old and updated target-interpolation methods on identical inputs, including joint-limit cases, and require bit-identical targets.

Changed modules compile. Runtime diagnostic code has not been exercised inside a live simulator, so live integration and logging overhead remain unverified. No learning or physical-grasp success is claimed by these tests.

The memory guard, frozen criteria and `grasp_metrics.py`, original robot, derived scenes and active grasp plan match their pre-work hashes. The two runtime files changed for logging; the target law, effort limits, friction settings and success thresholds were preserved. Before/after code snapshots and final hashes are retained in the offline work directory. No simulator process or training job was started.

The next useful work is a load-aware contact-layout refinement or a focused review of the selected contact model and knife mass/COM assumptions, followed by inspection of cooked shapes when sufficient memory is available. The new candidate poses should not be sent directly into pickup tests. The first dynamic diagnostic remains the paired stationary pinch versus small seating movement, after validating the new logging on simple known contacts, using the unchanged guarded launcher and memory reserves. A complete successful scripted pickup is still not an automatic prerequisite for a separately authorized bounded learning pilot.
