# Astra focused grasp review and proposed next decisions

Date: 19 October 2026. Scope: evidence review and planning only. No simulator, training job, hardware operation, controller change, configuration change, or asset modification was performed for this review. The only intended deliverable is this document. The actual working project is `/home/omen/teamwork_projects/tomato_cutting_right_arm`; synced ChatGPT project sources remain read-only.

## Decision

A human-like **functional** handle wrap is plausible with this hand, but is not established. The six independent hand actuators do not reproduce a human hand's independent finger joints or compliant palm. The existing results establish a board-supported, predominantly thumb/index fingertip pinch and an unsuccessful attempt to move from that pinch into a wrap. They do not establish that the hand cannot wrap this handle, that torsional friction is the root cause, or that reinforcement learning requires a successful scripted pickup first.

The immediate priority should be a small, instrumented separation of three questions:

1. Can the current hand and actual collision shapes satisfy the unchanged final wrap geometry at all, with a load-bearing contact arrangement?
2. Does the existing supported pinch fail while holding still, or specifically when the hand is commanded to seat around the handle?
3. Does the contact model respond as intended in a controlled contact experiment, and do measured contact forces explain the knife's motion?

After those checks, a separately authorized, bounded learning experiment can be a means of discovering manipulation. A complete scripted pickup is not an automatic entry requirement. Full task training remains prohibited under the present authorization, Phase 3 remains incomplete, and this review does not authorize any experiment below.

Preserve the frozen terminal criteria: palm support, opposing thumb, at least three curled fingers, at least two inner contacts, 115° combined finger curl, 15 mm tip-distance criterion for distal inner contacts, 5 cm unsupported lift, 3 seconds continuous hold and no more than 10 mm hand-relative slip. Blade/unsafe contact, attachments and commanded knife motion during an episode remain disallowed. Initial placement is permitted only at reset. See [criteria](phase3_grasp_criteria.json) and [evaluator](../../rl/grasp_metrics.py).

## Evidence and limits of this review

I read the [original vision RL plan](../../RL_VISION_KNIFE_PICKUP_PLAN.md), [phase status](PHASE_STATUS.md), [contact-transfer report](CONTACT_TRANSFER_RESULTS.md), [machine-readable results](contact_transfer_results.json), relevant current source and stored source snapshots. I independently inspected the raw `trajectory.json`, final 96-entry `seating_substeps.json`, failure records and configuration records for completed runs 01–05 and 07 under [the Phase 3 run directory](../../runs/rl/phase3). Runs 06, 08 and 09 contain startup refusals, not physical tests.

I also opened the composed USD with the offline USD library, without starting Isaac Sim, to inspect authored collision approximation, material binding, dimensions and offsets. That verifies authored composition, not the engine's cooked hulls or live solver configuration. No new rendering or physical-contact experiment was performed. Existing summary assertions about old tests or preservation hashes are not substitutes for new physical validation; this review did not rerun the reported 42 tests or re-certify every baseline asset.

Line references below refer to the source present during this review. Run snapshots differ in line numbering and are authoritative for their own execution. All numerical values extracted here are observations from recorded files, or explicitly identified calculations/proposals.

## Mechanical feasibility of the requested wrap

### What the mechanism can and cannot control

The recorded inventory has seven independent right-arm joints, six independent hand joints and five passive hand followers. Four fingers have one independent flexion coordinate each, with `q_DIP = 0.89 q_MCP`; the thumb has yaw and pitch, with `q_IP = 1.86 q_CMC_pitch`. The policy cannot independently adjust a finger's distal joint or add finger spreading that the mechanism does not provide. See [Phase 1 audit](PHASE1_AUDIT.md), [inventory](phase1_inventory.json) and `HandGeometry.transforms`, [plan_contact_seating.py](../../rl/plan_contact_seating.py), lines 26–35.

The frozen 115° combined curl corresponds to an MCP angle of about **60.85°** under the authored finger coupling. This is within the model's 1.6 rad MCP range and the diagnostic 85° cap. Thus the curl threshold alone is not mechanically impossible. It does not guarantee that the inner finger surface reaches the handle while the palm and thumb also contact it. Coupled flexion can move a distal pad away from the handle after a near-contact configuration; simply increasing closure is not a general solution.

A human-like functional wrap should mean useful palm support, opposition, enclosure and retention. Matching a human hand's appearance or exact closure sequence is a separate and more restrictive objective. Retain the preference for fingers establishing support before firm thumb opposition, but record whether the coupled hand can accomplish it and permit a temporary pinch, tilt or board-assisted reorientation as an intermediate physical action.

### Dimensions and geometric proposals

The offline composed scene inspection found handle collision vertices spanning approximately **172.58 × 36.66 × 21.10 mm** in knife-local axes; the whole knife spans **438.27 × 51.95 × 21.10 mm**. Finger distal meshes span roughly 22.32 × 12.19 × 40.32 mm in their mesh coordinates. These bounding dimensions are not pad thicknesses, local cross-sections or a calibrated fit measurement. The large knife/board combination matters: the board is about **469.43 × 298.63 mm**, so many position/yaw combinations cannot contain the entire flat knife. See [phase3_physics.json](phase3_physics.json) and the composed [scene](../../rl/scene/phase3_grasp.usda).

The top [refined supported-wrap proposal](refined_supported_wrap.json) uses index/middle/ring MCP angles of 70°, pinky 60°, thumb yaw 40° and thumb pitch 18°. The first three would have 132.3° combined curl under the model; pinky would have 113.4°, below the frozen 115° requirement, which is acceptable only because three other fingers would have to qualify. Its reported board clearance is 6.02 mm, palm gap 0.034 mm, thumb gap 2.00 mm, middle distal gap 2.33 mm and ring distal gap 0.59 mm; the index gap is approximately -0.97 mm. This is a near-contact proposal with allowed geometric overlap, not a physically settled wrap.

The proposal predicate checks gaps and count of nearby fingers. It does **not** establish opposing contact normals, the two required inner contacts, feasible contact forces, actuator equilibrium, full self-collision clearance, or a continuous route from the initial state. See [refine_supported_wrap.py](../../rl/refine_supported_wrap.py), especially the final `predicted_simultaneous_contacts` predicate, and [plan_supported_wrap.py](../../rl/plan_supported_wrap.py), lines 44–49. `predicted_wrap_found: true` therefore must not be read as a positive instance of the frozen oracle.

There is also a representation gap. `HandGeometry` constructs a single convex hull for each mesh and stores one mesh entry per rigid-body name (lines 17–25). The actual palm and thumb mount/metacarpal colliders use convex decomposition. A single hull can fill recesses and change the predicted palm surface. Multiple meshes on a future link would overwrite an earlier entry rather than form a union. The current offline near-contact computation is useful for proposals, but must be checked against the actual collider union before accepting or rejecting a terminal wrap. The path planner uses face-normal separating-axis bounds, not complete contact mechanics, and has no hand self-collision term in its objective (lines 61–106).

**Mechanical conclusion:** neither impossibility nor successful feasibility has been proved. The highest-value geometric result now is a small set of terminal candidates that meet the actual frozen contact geometry with valid self-collision clearance and plausible load balance. A finite failed search would only reject its searched posture region, not prove that the entire mechanism is incapable.

## What actually fails in the recordings

### Repeated abrupt index loss

The following was recomputed from raw substep traces. Forces are sums of recorded handle-contact normal forces by digit. The contact logger omits individual points below 0.05 N, so a recorded zero means no retained point above that threshold, not proof of literally zero interaction. Tip distance is the logger's principal-axis distal-tip coordinate, not independently measured surface arclength.

| Run | Last loaded thumb/index sample: control, substep | Next sample: thumb/index force | Previous thumb/index force | Index distance behind tip immediately before loss |
| --- | --- | --- | --- | --- |
| 01 | 765, 9 | 0.348 / 0 N | 2.879 / 2.734 N | 0.083 mm |
| 02 | 930, 3 | 0.150 / 0 N | 3.029 / 2.737 N | 0.351 mm |
| 03 | 834, 7 | 0 / 0 N | 2.799 / 2.528 N | 0.301 mm |
| 04 | 793, 9 | 0.258 / 0 N | 4.213 / 3.979 N | 0.121 mm |
| 05 | 761, 9 | 0.200 / 0 N | 3.006 / 2.897 N | 0.119 mm |
| 07 | 761, 9 | 0.200 / 0 N | 3.006 / 2.897 N | 0.119 mm |

Each adjacent pair has **identical recorded commanded joint targets**. The loss occurs within one nominal 1/240-second physics interval, not at a new command discontinuity between those two trace entries. That weakens the explanation of a sudden target jump at that exact instant. It does not exclude accumulated actuator load, earlier commands, collision geometry transitions, or contact-solver effects.

In run 05, knife vertical velocity changes from about -0.0073 to -0.0643 m/s at the recorded collapse; angular velocity already grows in the preceding substep. The board still carries approximately 0.62 N before and 0.43 N after collapse. This is a loss of a board-supported pinch, not failure of an already unsupported wrap. The trace does not contain the complete time-aligned contact wrench needed to assign causality to those accelerations.

Run 04 substantially reduced tracked-point errors: the last control sample before loss has a 0.557 mm maximum material-point error and 0.084 mm additional lateral drift. Run 05's control 761 sample has an 8.65 micrometre tracked-point error and 0.0031 mm lateral drift, yet the next control sample loses index support. These values demonstrate that a small kinematic tracking residual is not a stability certificate.

Across the raw control trajectories, no palm contact appears and the frozen oracle reports zero qualifying wrapping fingers. Run 01's ring contact peaks at 1.143 N and remains above 0.3 N for eight control samples, or 0.4 seconds. No other run acquires a recorded middle/ring/pinky handle load. The [direction audit](contact_transfer_direction_audit.json) reports a ring closing-normal derivative of +0.000768 m/rad versus -0.065755 m/rad for the index at run 01's control 762. This prior offline calculation is evidence of an unfavorable local ring approach direction, subject to its normal convention; it is not a force-closure calculation.

### What the patch experiment establishes

I compared file bytes: runs 05 and 07 have **identical** `trajectory.json`, `seating_substeps.json` and `rolling_progress.json`. Run 07's configuration records a 2 mm nominal torsional patch radius, zero minimum radius and exactly five distal colliders. It establishes no observed benefit and no observable response in this trajectory. It does not establish that physical pad compliance is irrelevant, that the setting took effect in the active backend, or that a 1 mm minimum will work.

The [PhysX shape reference](https://nvidia-omniverse.github.io/PhysX/physx/5.5.0/_api_build/classPxShape.html) describes nominal torsional friction as penetration-dependent, active for a single-anchor friction patch, and supported with the TGS solver. These conditions must be checked in the installed runtime; authoring a USD attribute alone is not that check. The same reference distinguishes contact offset from rest offset: contact generation may begin before geometric touching. This documentation explains possible mechanisms, not which mechanism occurred here.

No completed trace contains the newly added `separation_m` field. The 1 mm minimum-patch configurations in runs 08/09 never started. Consequently, penetration, friction-patch activity and backend response remain unresolved. The active [contact_seating_plan.json](contact_seating_plan.json) is the rolling configuration with no nonzero patch override; the pending sensitivity remains in [contact_transfer_plan_patch_min1mm.json](contact_transfer_plan_patch_min1mm.json).

## Code and collision-model audit

| Finding | Evidence | Implication and next check |
| --- | --- | --- |
| The reported no-slip residual is for an intermediate command. | [rolling_contact_control.py](../../rl/rolling_contact_control.py), lines 5–14; [central_grasp.py](../../rl/central_grasp.py), lines 430–462. `J @ delta` is computed before preload retention, force feedback, clipping, arm IK and synchronized joint interpolation. | Log both the projected command and the actual post-processing command; recompute contact-point motion using the latter and measured substep motion. A tiny printed residual does not constrain the final executed target. This is a confirmed reporting limitation; its causal contribution is unmeasured. |
| Point-preserving kinematics omit load and moment feasibility. | The rolling projection has point Jacobians only; no friction cones, wrench balance, contact-normal inequality, pressure bounds or torque limits in its projection. | Two localized opposed contacts can remain kinematically close while lacking rotational or load stability. Include gravity, board support during transfer, COM moment and actuator capacity in a prospective contact-wrench check. Do not infer stability from number of point constraints. |
| The anchor frame changes while its reference pose remains fixed. | Current knife pose defines `point_knife` at lines 416–429; `contact_reference['pose']`/`rotation` are set once at lines 403–406, used for error checks at lines 178–185 and conversion at lines 448–450. | This is a consistency risk when the knife rotates/translates: new coordinates in the current knife frame are later interpreted using the initial frame. The observed pre-loss drift in run 05 is tiny, so this is not proved to explain its collapse. Use explicit fixed-world versus current-object frame semantics in future diagnostics. |
| Pressure targets introduce extra coupled motion. | [contact_path_control.py](../../rl/contact_path_control.py), lines 33–51, changes index and thumb commands after geometric projection. Run 05 control 761 has thumb pitch actual ~0.1315 rad versus target ~0.3077 rad, and index actual ~0.8920 versus target ~0.9703 rad. | The considerable drive deflection is intentional preload, not successful posture tracking. It can interact with changing lever arms; logged estimated drive torque is not measured hardware torque. Preserve and log this distinction instead of increasing gains blindly. |
| The late rolling acquisition schedule remains tied to progress toward the old endpoint. | `qgoal` at [central_grasp.py](../../rl/central_grasp.py), line 440, holds middle near 52.5° until fraction 0.3; recorded progress is only 0.0406 at iteration 110. Ring is targeted near 70° and pinky toward 85°. | The observed rolling test does not explore all possible middle/ring acquisition approaches. A useful-contact search should target one new support explicitly, rather than assuming endpoint progress will create it. |
| Distal contacts use rigid convex hulls, not calibrated compliant pads. | Offline composed stage: thumb/four finger distal and four proximal colliders are `convexHull`; palm and thumb mounts are `convexDecomposition`. All enabled inspected hand/handle colliders bind `/Phase3ContactMaterial`, with 2 mm contact offset and zero rest offset. Source: [minimal_benchmark.usda](../../rl/scene/minimal_benchmark.usda), [phase3.usda](../../rl/scene/phase3.usda), [phase3_grasp.usda](../../rl/scene/phase3_grasp.usda). | Inspect cooked hulls and contact features around the extreme index tip. A sharp hull transition or insufficient compliant patch is plausible, not proved. Two 2 mm offsets permit contact generation within their combined shell; do not equate that shell with physical padding. |
| Knife mechanics remain provisional. | [prepare_phase3.py](../../rl/prepare_phase3.py), lines 61–99: friction 0.8/0.6, 0.25 kg total with 0.10 kg handle and 0.15 kg blade, derived COM/inertia, CCD enabled. | These settings are authored consistently but uncalibrated. Finger-force magnitude alone does not prove the available torque/friction margin around a long knife. |
| Existing records cannot reconstruct the full impulse event. | [contact_evaluator.py](../../rl/contact_evaluator.py), lines 45–105, filters points at 0.05 N and sums tangential forces by body. The final trace ring buffer is 96 entries (~0.4 s); `_apply_action` samples the preceding physics substep. Separations were added after these runs. | Record raw point counts, points below the display threshold, separation, collider/feature identity, full contact wrench, all relevant self/board contacts, drive state, and precise pre/post-step timestamps. Verify pose/contact synchronization before interpreting acceleration or friction ratios. |
| The final oracle still needs physical positive validation. | [grasp_metrics.py](../../rl/grasp_metrics.py), lines 30–75; [contact_evaluator.py](../../rl/contact_evaluator.py), lines 24–39 and 63–80. Inner distance comes from a PCA tip axis; blade classification excludes points also classified as handle within 3 mm hull tolerances. | Validate inner-contact labels against actual surfaces and collar/blade-boundary negatives, as well as positive wraps. The reported final slip is handle-centre translation in palm coordinates; add knife-angle drift as a separate diagnostic without silently changing the frozen criterion. |

The safety stops and current non-success classifications are appropriate. A normal process exit is not a passed grasp. Some drift-stop samples are written to dedicated failure/stop files before they can be appended to the normal trajectory, so a review must include both.

## Ranked hypotheses, with discriminating evidence

Ranking is by present evidence and value of the next test, not a numerical posterior probability.

1. **A marginal tip contact and missing new support make the seating path physically fragile.** High evidence for the contact location and lack of replacement load; medium confidence that this is the dominant mechanism. All six collapses occur at extremely tip-localized index contacts, and no palm/three-finger state is approached physically. Discriminator: terminal geometry/contact audit and supported hold versus seating comparison, followed by a one-finger acquisition test.
2. **The executed arm/finger motion and preload do not obey the projected contact constraint.** Confirmed structural difference in code; causal confidence medium. The residual being reported is upstream of the actual command path. Discriminator: post-processing residual, measured contact-point velocity and command-only/hold comparisons.
3. **A collision-feature/friction-manifold transition, missing torsional response, or solver sensitivity causes the abrupt release.** Plausible from the substep discontinuity, rigid tip geometry and identical patch/no-patch trajectories; confidence medium-to-low without raw separations, cooked shapes and wrench balance. Discriminator: effective-parameter/backend test, point/feature trace and then one-variable physics sensitivity. Do not assume that nominal torsional radius equals effective compliance.
4. **Unmodeled self-contact, board reaction or coupled-drive dynamics destabilizes the pinch.** Possible: prior palm-seating tests exposed thumb-mount interference, and the knife still bears on the board. No full self-contact history accompanies the collapse. Discriminator: synchronized all-body wrench and actuator/coupling trace. The current lack of a safety-stop event does not prove absence of smaller destabilizing contacts.
5. **Logging/classification/timing makes a contact transition look sharper than the physical event.** Thresholding and pre-step logging are confirmed; a wholly fictitious loss is less likely because knife velocity changes and opposed support remains lost. Discriminator: raw contact arrays plus matching body state and support forces at every completed physics step.

These can coexist. The review does not select a root cause from summary metrics alone.

## Small staged tests proposed for later authorization

All numeric diagnostic gates below are proposals to freeze before execution. They do not replace the final grasp criteria. Use the current physical reset and reproducible prelude, one simulator instance, bounded wall time, saved code/config hashes and the same stop conditions. Reconstructing a pre-loss state must include a fresh physical prelude; a saved joint/object pose alone does not restore solver/contact history. No in-episode teleport, attachment or commanded knife pose is allowed.

### A. Terminal geometry and observability audit, before further tuning

Inspect at most three existing best wrap candidates plus one explicit fingertip-pinch negative. Use the composed collision union, mesh-to-body transforms, actual mimic coupling and full self-collision checks. Evaluate actual contact locations/normals, the 15 mm inner-contact requirement, enclosure and palm/thumb/three-finger coincidence. Check board clearance for the candidate and arm IK separately. Evaluate whether bounded contact forces can balance gravity and knife moment under provisional friction and actuator limits, labeling those assumptions.

**Pass:** at least one candidate survives all geometric requirements and has a feasible, documented load solution with margin under the declared assumptions. This is a terminal-feasibility candidate, not a pickup success. **Fail:** no candidate survives; record the specific blocking requirement and expand only the implicated pose dimension or reconsider the proposed grasp/board arrangement. Do not spend another series of path trials pursuing an endpoint that never met the inner-contact or opposition conditions. A small search failure is not a global impossibility proof.

Before dynamic tests, verify raw contact count versus displayed contacts, separation sign, force units, body/shape naming and sample timing. **Pass:** known static contacts/clearances and contact-force sums agree with the independently recorded body state within predeclared measurement tolerance. **Fail:** inconsistent timestamps/frames/classification; fix instrumentation before attributing the collapse to mechanics.

### B. Hold versus motion: the first decisive dynamic comparison

Use one baseline replay and one paired hold trial, then one repeat of each only if the first pair gives a clear, reproducible difference: **at most four trials**. Reproduce the physical approach/tilt/preshape, and choose a recorded stable pinch state sufficiently before the failure. The hold trial freezes the current actuator targets for a proposed 3 seconds; the comparison executes the original small seating commands. Do not use a zero action that secretly relaxes targets toward home. Record all 240 Hz evidence listed above, with a short pre-event buffer and bounded post-event capture.

**Diagnostic hold pass:** thumb and index retain at least 0.3 N at every completed substep, no >2 mm additional knife-centre lateral drift, no safety violation, and no unaccounted collapse; board support is allowed and explicitly reported. **Failure:** any sustained loss or safety event. If hold fails similarly, investigate static load/contact/drive/backend behavior before path shaping. If hold passes while seating fails, prioritize the executed motion, contact-feature traversal and acquisition geometry. Neither outcome passes the final task.

### C. One useful new finger, before another whole-wrap trajectory

Choose middle or ring using the terminal audit and a verified normal-direction convention. Keep the original physical pinch supported. Compare a zero-motion reference with at most two small, separately bounded approach directions that the geometry predicts will load the chosen finger. Limit each trial to the acquisition interval; stop if the original pinch collapses. Do not simultaneously change pressure, friction, solver and posture.

**Pass:** chosen finger sustains >0.3 N for at least 0.5 seconds, has a contact normal/closing direction that opposes useful handle load rather than brushing tangentially, and survives a small predeclared reduction in original index support without loss of the knife. Confirm no blade/self/board violation or excessive drift. **Fail:** only brief/tangential contact, overclosure moving the pad away, or loss during unloading. This is transfer evidence, not a full wrapped grasp. Only then plan a re-anchored handoff using measured new support.

### D. Contact-model sensitivity only after its mechanism is measurable

If the preceding trace implicates torsional/feature behavior, verify the effective solver type, cooked collider, material and torsional settings. Use a separate simple contact fixture with known compressive load and bounded twist about the contact normal to compare zero patch, the existing 2 mm nominal/zero-minimum setting, and the pending 1 mm minimum setting. A diagnostic fixture is not a knife-pickup demonstration. Record separation, patch state where exposed, resisting torque and angular response.

**Pass for a sensitivity:** the intended parameter produces a reproducible, explained change in the expected physical response. **Fail/inconclusive:** authored attributes change but response does not; resolve runtime applicability before another complete pickup run. If timestep or solver-iteration sensitivity is needed instead, vary one at a time while preserving the same 20 Hz control trajectory in simulated time and recomputing force units from the actual physics interval. The current contact reader hard-codes `dt=1/240`, so merely changing physics frequency would invalidate that comparison.

Even a successful artificial minimum-patch setting is not hardware calibration and cannot be promoted to a deployment setting on pickup success alone. A compliant-pad model needs measured compliance and friction, not a setting selected solely to pass the task.

### E. Physical terminal retention and then flat-start pickup

Once a candidate and contact route are credible, test the terminal wrap under physical settling and release of any **explicitly disclosed external diagnostic support**. This may be a separate reset-level fixture to test terminal retention; it is never counted as flat-start pickup. Do not use hidden constraints. Require actual independent-oracle and visual agreement, then attempt the unchanged 5 cm/3 second/10 mm unsupported lift and hold from a valid flat reset. Keep any terminal-retention result and flat-start result separate.

An alternative to further scripted route construction is a bounded state-based learning pilot under the next section's gates. Learning is allowed to discover the route; mechanics and the evaluator still have to be credible.

## Route to vision RL without an endless scripted-pickup prerequisite

The original phased plan correctly separates physics, perception and learning, but its Phase 3 language can be interpreted too strictly as requiring a scripted end-to-end success before any learning. The scientifically useful gate is a credible physical task, controllable actions, resource headroom and trustworthy evaluation. A script is one way to produce evidence, not the sole route.

**Current state:** `central_grasp.py` uses exact object pose and simulated contact forces inside scripted feedback. `NativeValidationEnv` returns a zero task reward and has no pickup learner. The Phase 2 PPO updates exercised a posture/resource workload with an untrained image encoder. None is evidence of learned knife pickup or recognition. No existing successful scripted baseline should be relabeled as a policy or as a frozen-oracle demonstration.

A proposed progression after explicit authorization is:

1. **Bounded state-based discovery pilot.** Once collision/measurement checks pass and at least plausible terminal geometry is available, allow a small privileged-state actor/critic to explore a tightly bounded supported acquisition/transfer task. A positive final physical example need not already exist. Use finite episode/update/wall-time budgets, train/evaluate separation, a saved untrained baseline and checkpoint replay. The pilot's purpose is to discover useful contacts/routes and expose reward defects; do not claim task success or full training readiness from shaped return. A reliable positive oracle example remains necessary before final acceptance claims and before using “success” to gate large-scale curriculum promotion.
2. **Manipulation curriculum.** Start near a valid settled handle and learn approach, useful contact and retention; broaden to flat-start repositioning and lift, then position/yaw coverage. A supported or near-wrap reset may aid learning but must be labeled and evaluated separately. Gradually remove such aids; final test episodes start flat and use only physical interaction. Never make the old pinch trajectory a mandatory policy action sequence. Track actual finger-versus-thumb timing.
3. **Perception work can proceed independently.** Camera geometry, synthetic labels, pose/confidence training and latency/noise evaluation do not depend on a successful script. Run data generation, perception training and simulator/RL workloads sequentially on this laptop as memory requires.
4. **Vision-conditioned policy.** Prefer a compact camera-derived handle representation plus robot feedback for the first local attempt. A privileged critic and a state teacher are useful but optional; direct asymmetric vision RL is possible if a state teacher does not emerge. Distillation may initialize behavior, but a claim of vision RL requires actual RL updates with deployable actor inputs and subsequent camera-only evaluation. Add estimated-state errors, occlusion and delay based on measured perception performance.
5. **Broaden only when measured learning improves physical metrics.** Record useful support duration, true wrap frequency, unsupported retention and frozen task success separately from reward. Penalize repeated contact/release reward harvesting, blade contact, excessive motion and edge escapes. Do not quietly turn a failed full grasp into a success by changing curl, palm or inner-contact requirements.

A full successful script is therefore optional; meaningful mechanics, honest metrics, frozen safety limits and a bounded experiment are not. The present NO-GO for full training and no-run boundary remain unchanged by this recommendation.

### Camera and deployable observation plan

Start with the original agreed **one RGB-D camera near the head/upper torso**, viewing the board. The existing benchmark camera in [benchmark.py](../../rl/benchmark.py), lines 66–83, uses 24 mm focal length, 20.955 mm square aperture, 0.02–5 m clipping, 20 Hz requested frames and depth-to-image-plane. It was a resource probe, not calibrated real hardware. Use its recorded placement as a starting candidate, not proof of visibility during a hand wrap.

For the eventual camera specification, record mounting transform, intrinsics, distortion/depth convention, units, resolution, frame timestamps, actual latency and synchronization with joint states. Verify the USD-to-ROS optical convention in [interface_contract.json](interface_contract.json). Test full-board coverage both empty and with the arm at pregrasp, tilt, wrap and lift poses; report handle pixels, occlusion and missing depth by board region. Compare modest full-frame resolutions or a full-board frame plus crop only as measured accuracy demands. A crop must be selected from camera evidence, not privileged knife coordinates.

Actor inputs should be RGB-D features or estimated handle pose/orientation and confidence, valid-depth/visibility flags, observation age, available joint positions/velocities and recent actions. For occluded contact, short observation/action history or a compact recurrent state can preserve an estimate, but must represent growing uncertainty. Simulator contact identity/force, exact knife pose, ground-truth segmentation and oracle labels stay in rewards, critic, labels and evaluation only. Motor currents, force/torque and tactile inputs remain excluded until the actual hardware interface and semantics are verified.

The final hand can occlude its own handle. Evaluate controlled bounded continuation versus pause/reobserve behavior for short and long occlusions; do not demand an impossible always-visible handle or allow indefinite blind motion. Do not add a wrist camera unless coverage tests justify it and the physical mount is feasible. Measure position/orientation error in the board frame and hand frame, across visible and occluded states. Set acceptance tolerances from observed grasp sensitivity rather than an arbitrary millimetre claim.

Perform an actor-input audit and a causal vision test: move the knife in the image while holding irrelevant privileged inputs fixed; the target must change accordingly. Remove or occlude the knife; confidence/recovery must respond. Evaluate the saved policy with learning disabled and ground-truth actor channels physically absent, not merely promised unused.

### Whole-board evaluation

Partition the entire intended board into a predeclared position grid and yaw bins, including centre, four sides and corners. Classify each bin separately for (a) valid flat whole-knife placement, (b) camera visibility, (c) arm reach and collision-free approach, and (d) manipulation success. Report invalid-footprint and unreachable/occluded bins explicitly; conditional success over a convenient subset is not whole-board success.

Use separate training, validation and final-test seeds. Record the starting handle region, whole-knife footprint, final grasp location, nudging displacement, yaw and whether pickup depends on an edge. Maintain a centre/away-from-edge group in which the episode stays away from an edge until pickup. Retain failures and excluded counts in denominators appropriate to the declared task. If board/robot/camera placement must change to achieve intended coverage, propose it openly rather than hiding exclusions.

The original proposed final target remains useful: at least 200 held-out episodes, at least 90% overall and 80% in each predeclared major group, with counts and confidence intervals. It must be frozen before testing and may require more episodes if many groups would otherwise have too few samples. Report safety events separately, completion time, slip, angle drift, peak forces, contact sequence, memory and interventions. Zero observed unsafe events is not a proof of zero risk. The final set must not become an iterative tuning set. Report training-seed variability when the local budget permits and label a single-training-seed result explicitly.

## Missing physical properties and deployment implications

| Missing or provisional property | Why it changes the decision |
| --- | --- |
| Actual handle/knife dimensions, mass, COM and inertia; correct intended knife scale | Determines fit, moment arm, board coverage and the force/torque needed to retain the knife. The present 0.25 kg split and 438 mm knife are simulation assumptions/asset facts, not measured hardware. |
| Pad and palm material, thickness, local shape, stiffness, damping and torsional response | Determines whether an extreme rigid-tip contact resembles the real hand, how contact area develops, and whether the proposed patch model is meaningful. |
| Friction of finger/handle and knife/board over realistic loads | Determines transfer and slip; the uniform 0.8/0.6 pair is uncalibrated. Randomization ranges should eventually come from measurements. |
| Hand coupling/backlash, joint zero and limits, motor strength, controller gains and command rate | Determines actual reachable wrap shapes and retained preload. A USD mimic relation is not a measured transmission model. |
| Right-arm and six-channel hand command/feedback mapping, signs, units and latency | Determines which policy actions and proprioceptive inputs can be deployed. The vendor channel order and USD thumb ordering must not be copied by index. |
| Tactile option, wrist sensing, encoder/velocity availability and meaning of current estimates | Determines observability. Unknown tactile hardware cannot justify a force-feedback deployment policy. |
| Real camera, mount, calibration, depth failures and timing | Determines pose accuracy, occlusion and state-estimation uncertainty under the hand. |
| Stop behavior, stale-command handling and physical workspace | Required before any separately authorized hardware operation; simulation success alone does not validate these interfaces. |

The physical robot using the same nominal arm/hand models reduces one uncertainty but does not resolve any of these measurements. Continue local-only development. Later hardware work should begin with perception-only and empty-hand checks, then a blunt surrogate under the separate hardware protocol from the original plan; this report authorizes none of it.

## Resource and preservation boundary

The laptop has approximately 16 GB host RAM and 8 GB VRAM. Keep [guard_benchmark.py](../../rl/guard_benchmark.py), lines 15–20 and 43 onward, unchanged: startup requires **10,000,000,000 available host bytes and 4 GiB free VRAM**, with the existing host checkpoint/hard-stop reserves of 3,000,000/2,000,000 Linux kB and GPU checkpoint/stop reserves of 1.5/1 GiB. Preserve the shared controller lock, bounded logging and graceful checkpoint-stop behavior. Do not lower startup memory to make the pending sensitivity run.

The completed short contact trials used about 2.52 GB peak worker RAM with no reported memory warnings. The earlier RGB-D resource soak used about 7.75 GB process RAM and 2.66 GB total GPU memory at peak. Neither proves that the future camera task, larger learner, replay buffer or full kitchen fits. Re-measure the actual chosen learning workload under the same guard before extending it. Keep one environment initially and avoid concurrent simulator, perception training and full-kitchen viewer workloads. Throughput from the posture probe is not a training-duration promise.

No source robot, accepted baseline, success criteria, controller, active plan or safeguard was intentionally edited in this review. The active plan remains rolling/zero override, the 1 mm minimum-patch branch remains unexecuted, and six failed physical diagnostics plus three startup refusals remain the accurate contact-transfer outcome.

The recommended next decision is a bounded authorization for terminal/collider validation and the paired hold-versus-motion diagnostic, with the above evidence requirements. It is not another unconditional sequence of seating tweaks or a commitment to complete a script before learning can begin.
