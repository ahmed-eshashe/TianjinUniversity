# Offline grasp geometry and controller checks

The bounded offline checks requested after [Astra's review](ASTRA_GRASP_REVIEW.md) are complete. **No terminal wrap has been certified, and the contact-loss cause remains unresolved.** The first two existing candidates lack two eligible inner finger regions even within a generous proximity screen. The third has promising proximity but its selected contact layout fails opposition and a provisional static load check. These findings justify revising the endpoint assumptions before another sequence of seating trials. They do not establish that the hand cannot grasp this knife.

No simulator or training was launched. The active controller, active grasp plan, frozen criteria, derived scenes, source robot and memory safeguard were preserved. New files are offline analysis tools, their tests and results. Phase 3 remains incomplete.

## Geometry and colliders

[The geometry audit](offline_grasp_audit.json) evaluates the first three entries of `refined_supported_wrap.json`, plus its measured fingertip-pinch negative. Candidate indices below are zero-based. Coupled finger and thumb joint angles obey the authored limits. All three terminal hand poses have right-arm IK solutions with position errors below 0.00014 mm and orientation errors below 0.000002 rad; those small numerical errors do not validate the approach route or arm clearance from the kitchen.

The audit preserves all enabled mesh colliders per hand body and their mesh-to-body transforms. It uses convex-envelope closest-point calculations with feasible witnesses and supporting-plane distance certificates, within 1 micrometre. The distal inner region is the collider clipped at least 15 mm behind the present evaluator's PCA tip coordinate. Proximal contact regions qualify by the unchanged rule. This checks the current geometric convention; physical validation of that convention is still needed.

For an optimistic screen, regions within **4 mm** of the handle are counted as potentially nearby. This reflects the sum of the two authored 2 mm contact offsets, and **is not a new success tolerance, soft padding or proof of loaded contact**. Positive gaps remain positive gaps with zero rest offsets. The curl requirement still applies when counting fingers.

| Existing candidate | Curled fingers near the handle | Eligible inner finger regions within 4 mm | Lowest hand clearance above board plane | Outcome |
| --- | --- | --- | --- | --- |
| 0 | Index, middle, ring | Index only | 6.02 mm | Fails two-inner-finger proximity screen |
| 1 | Index, middle, ring | Index only | 6.02 mm | Fails two-inner-finger proximity screen |
| 2 | Index, middle, little | Middle, little | 8.29 mm | Survives proximity screen; terminal feasibility unproved |

For candidates 0 and 1, the nearest eligible inner-region gaps are 3.36 mm for index, 6.88 mm for middle and 5.21 mm for ring. Thus nearby distal tips did not imply nearby inner surfaces. Candidate 2 has middle/little inner-region gaps of 3.60/3.74 mm; its palm and thumb gaps are 2.07/1.13 mm. Closing those gaps could change all other contacts, so hypothetical simultaneous contact is not an attainable settled state yet. The measured pinch negative is correctly classified as unwrapped and unsuccessful by the unchanged oracle.

There are **12 enabled hand colliders: nine convex hulls and three convex decompositions**, each with 2 mm contact offset and zero rest offset. They bind the phase contact material. There is one enabled collider per hand body in this asset, so the older planner's potential multi-mesh overwrite is not triggered by this inventory. Its single-hull approximation to the decomposed palm/thumb shapes remains a real representation limitation. Knife and support collider attributes are recorded separately in the JSON.

The full terminal self-collision screen checks **44 meshes and 868 unfiltered mesh pairs per candidate**, honoring the stage's authored body-pair filters and keeping the left side at its Phase 3 home. No additional right-hand convex-envelope intersections were found. Two envelope overlaps remain at arm links 5/7, one per arm, each involving decomposed geometry. An enclosing hull can fill a real recess: these are **unresolved envelope overlaps, not confirmed physical collisions**. Resolve them against the cooked decomposition before approving terminal collision clearance. No filter was added. Continuous approach safety and arm/environment collisions remain unverified.

## Conditional load check

Candidate 2 was also tested with a deliberately hypothetical contact set: palm, thumb, index, middle-inner and little-inner closest-point witnesses. This assumes the positive gaps can be closed without changing their positions or normals. It is a sensitivity calculation, not a physical pose.

At those selected witnesses, the radial geometry passes enclosure but fails the frozen thumb/finger opposition predicate. A static linear program with the provisional 0.25 kg knife and COM, friction 0.6, an inscribed eight-ray friction cone, 0.05–10 N normal load per selected contact and no board support finds no equilibrium for 1.25 times gravity. It also finds no solution at nominal gravity with actuator limits, or at 1.25 times gravity with actuator limits removed. Therefore this result cannot specifically blame motor strength.

The actuator check uses 80 Nm per arm joint, 1 Nm per thumb coordinate and 0.3 Nm per finger coordinate, with the authored coupling included through finite-difference Jacobians. All available actuator capacity is optimistically allocated to the knife load; robot self-weight and full drive equilibrium are omitted. Contact points/normals, friction, mass properties, the finite friction-cone approximation and force cap limit the conclusion. Other points on the surfaces, different postures or calibrated pad compliance might behave differently. **No mechanically feasible terminal solution has been established; no global impossibility has been proved.**

## Recorded contact and controller checks

The raw substep audit independently reproduces Astra's finding in all six completed transfer runs: index support collapses between adjacent recorded physics samples while commanded joint targets remain identical. The retained index contacts are only **0.083–0.351 mm behind the recorded tip coordinate**. Zero logged force means no retained contact above the logger's threshold, not proof of literally zero interaction. Runs 05 and 07 have byte-identical trajectory, substep and rolling-progress files. The nominal patch test demonstrated no changed response.

[The controller replay](offline_controller_replay.json) reconstructs four rolling updates in run 05, at control steps 661, 701, 751 and 761. It reproduces the saved desired joint targets within **0.00000019 rad** and next actuator targets within **0.00000018 rad**, supporting the interpretation of the command pipeline without replaying dynamics.

The projected linear contact residual is around numerical zero. Nonlinear FK of that ideal projected increment moves the tracked points about 0.00008–0.00009 mm. In contrast, FK of the saved actuator-target changes moves the same body material points about **0.0095–0.0217 mm** per control interval. The original residual therefore does not certify the final command. Those are small displacements and do not establish a frictional failure mechanism.

Pressure correction made no additional change to the ideal relative finger increment in these four samples. It is incorrect to infer from the code ordering alone that pressure feedback caused this event. Preserved preload, relative arm commands, frame interpretation, IK and synchronized joint interpolation remain parts of the executed pipeline. The current-versus-fixed knife-frame reinterpretation error is about **0.004–0.038 mm** at these samples; its existence is confirmed, but causal significance is unproved.

At the control interval spanning the loss, measured-joint FK moves the tracked body points about 0.105/0.154 mm. This interval includes the failure and cannot distinguish cause from response. Material-point FK is neither a measured contact-manifold trajectory nor hand-to-knife slip. All four replay samples retain the middle-finger goal at 52.5 degrees; the late acquisition schedule is not exploring a broad finger-contact search.

There is no paired hold-only trial in the evidence. Old traces lack separations and full time-aligned contact wrenches. The root cause cannot be assigned to the solver, friction, geometry or controller from this offline work alone.

## Next steps before physical testing

1. **Refine a terminal candidate around the missing requirements.** Target a second inner surface plus genuine thumb opposition, then repeat clearances and conditional load checks using credible contact normals. The existing candidate ranking is insufficient for approving an endpoint. Preserve the final grasp thresholds. A successful scripted route remains optional for later bounded learning.
2. **Prepare command and contact instrumentation.** Record projected motion, pressure adjustment, final desired and actual actuator targets, and measured joint/link motion separately. Make fixed-world and current-object reference frames explicit. Keep raw contact counts including points below the display threshold, separation, force units, body/shape identifiers available from the backend, board/self contacts and pre/post-step timing. Do not label unsupported backend fields as measured. The old residual remains useful only with its limited scope clearly named.
3. **When physical tests resume, first verify observation and cooked shapes.** Check separation sign, contact timing and normal/friction force units against simple known contacts; inspect the cooked distal-tip geometry and the ambiguous decomposed arm pairs. Memory availability alone does not resolve these measurement gates.
4. **Then perform Astra's paired hold-versus-motion test**, at most two pairs with a fresh physical prelude each time. Freeze the existing actuator targets for a 3-second hold; compare against the original small seating motion. Require thumb/index load at least 0.3 N at each completed substep, no more than 2 mm additional lateral drift and no safety violation for the hold diagnostic. Board support is explicitly allowed here. Neither branch counts as successful pickup. If the hold fails, investigate static contact/load/backend behavior; if only motion fails, investigate executed motion and contact acquisition.

No physical launch was attempted in this continuation. Report and review these findings before executing the next physical stage, as requested. The pending minimum-patch experiment is not promoted to the first test, and no uncalibrated setting is activated.

## Verification and preservation

All **47 automated tests pass**. New checks cover known face/diagonal distances, invariance under a rigid coordinate change, overlap versus clearance, a fingertip-contact case with a separated inner region, and agreement with independently saved controller targets. New tools compile. No tests claim physical contact or grasp success.

The final geometric audit takes about 34 seconds and uses approximately **425 MB peak process RAM** on this Linux laptop, with numerical threads limited to one. It does not import the simulator launcher. Protected-file hashes agree before and after the audit and between both offline tools. The 10 GB available-RAM startup reserve, all runtime stop thresholds and frozen oracle remain unchanged. These short offline measurements do not predict future camera/RL memory requirements.

Tools: [geometry and trace audit](../../rl/offline_grasp_audit.py), [controller replay](../../rl/offline_controller_replay.py). Evidence: [geometry JSON](offline_grasp_audit.json), [controller JSON](offline_controller_replay.json). Original physical evidence remains under `runs/rl/phase3/contact_transfer_*`; this continuation adds no simulator run.
