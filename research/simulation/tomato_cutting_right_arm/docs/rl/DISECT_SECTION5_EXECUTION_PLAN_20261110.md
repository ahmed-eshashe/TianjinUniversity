# Section 5 — connect the candidate to the robot

## Review of available evidence (10 November 2026)

This is a saved-result and implementation review, not an independent rerun of every historical test. Sources: v40/final_campaign_review.json; v43/constitutive_controls.json, packet_isolation.json, settle_contact_result.json, qualification_sequence.py; current DiSECt checklist; the Section 4 execution plan and research roadmap.

- The original-material v40 run stopped on local element compression before fracture. It does not establish a slice or qualify robot cutting.
- The user-approved v43 candidate changes only bulk elastic coefficients, targeting E=0.4 MPa and nu=0.3. The stabilized-law coefficient conversion and CPU/GPU constitutive controls are documented. Packet isolation/reset checks pass. Published constants remain a prior; experimental validation remains pending.
- Its fresh one-second coarse hold completed in 6,330.9 seconds. Late maximum speed was0.155mm/s (limit1mm/s), solver residual4.75e-10 and force-balance error1.27e-11N. This is a supported-settling component pass only.
- At review time the independent half-step hold was running at0.883/1.000s; the comparison result did not exist. Do not infer its eventual result from this snapshot.
- The supervisor automatically performs the half-step hold and settling comparison, then STOPS. It does not automatically finish contact qualification or Section4. Sol must resume the remaining gated work explicitly after reviewing those outputs.
- The conservative timestep uses a rest bulk stiffness bound. It is not a proof for the complete nonlinear contact/fracture system. Dynamic refinement remains necessary. Runtime is unsuitable for claiming training readiness; speed is deferred, not passed.

Review conclusion: preserve these useful component results, but do not mark Section4 complete or adopt the engine from them. The next scientific dependency is the new material's fresh contact and damage qualification.

## Scope and dependencies

Keep the existing robot, kitchen, natural handle grip, backward/outward elbow, fixed knife attachment and motion interface. The attachment remains disclosed. Robot motion is scripted for this section. No learning, new material tuning, larger stops or video work.

Preparation, interface tests and unloaded robot motion may proceed before a successful slice. Loaded coupling requires the exact candidate's fresh contact qualification and Section4 GateB damage/stop/withdrawal pass. A robot separation claim requires Section4 GateC/D separation/stability evidence for that same candidate. Full Section4 completion is still governed by its own plan; partial preparation does not bypass it.

## Gate 5A — freeze and verify the interface

1. Inventory the existing robot launcher/controller, actual blade pose reader, wrench application point, reset code and candidate adapter. Record exact paths, versions/hashes and candidate result files. Reuse the verified implementation; do not invent replacement paths or silently use old-material checkpoints.
2. Define one interface contract: units (m,s,N,Nm), world/robot/hand/blade/material transforms, quaternion convention, blade COM and wrench origins, timestamps, step IDs, solver substeps, and state ownership. Candidate owns tissue mechanics; articulation owns robot motion.
3. Drive material contact from the ACTUAL mounted-blade pose. Commanded pose is a target, not measured motion. Interpolate actual endpoint poses on a declared clock; never advance one engine twice or drop physical time to hide slow execution.
4. Return equal-and-opposite contact reaction once. Transform torque with the lever-arm term when changing origin. Disable any duplicate native knife–tomato contact response while retaining required scene collisions; document who owns each collision and support response.
5. Independent fixtures: zero contact, known force at an offset point, pure couple, rigid frame rotation/translation, reversed sign, delayed/duplicate sample and reset. Verify force/torque conservation and power invariance under frame/origin changes using analytic expected values (relative tolerance1e-8, absolute floors1e-8N and1e-10Nm). Deliberate sign/origin/time errors must be rejected.

Deliver interface contract, ownership table, test report and manifest. This tests mapped contact work, not unresolved native motor-work interpretation.

## Gate 5B — unloaded mounted-robot route

Use a separate scene/version and the existing dry route. Close fingers on the handle before lifting; retain the disclosed fixed mount. Preserve outward/backward elbow and relaxed left-arm posture. Verify pickup, approach, controlled stop and the approved horizontal retreat.

Before running, record the earlier verified robot tracking limits; retain the stricter limits if present. Otherwise use provisional demo gates: blade translation error<=1mm, orientation error<=1degree, hand-to-knife transform drift<=0.1mm/0.1degree. These are unloaded integration gates, not allowable tomato penetration. Recheck the complete swept geometry against body/counter/board; retain the existing1mm board-clearance margin where applicable. Any fixture collision or joint-limit violation fails. Report commanded and actual joint/blade traces and clearance minima. No per-frame root/joint teleportation to manufacture tracking.

Deliver actual-motion traces plus inspected views of grip and both arms. A visual pose alone is not a tracking pass.

## Gate 5C — bounded coupled contact, then qualified cutting

1. Check dependency files for the same material/mesh/contact versions. A green old-model component cannot authorize the new candidate.
2. Start with a nonfracturing load/stop/unload episode. Freeze its trajectory, duration, substep schedule, acceptance file and finite wall cap before launch. Check actual-pose contact, mapped reaction, articulation response and sustained target/board support.
3. Retain every Section4 limit:2N reaction and summed nodal load,0.1mm whole-material CAD penetration, volume ratio>0.1, board penetration<=0.1mm, fixed-support error<=1e-7m, board margin>=1mm, force balance<=1e-6N and residual<=1e-9. Check at accepted physical steps, before damage commit. Unloaded tracking tolerance never relaxes penetration.
4. Compare a replay driven by recorded actual blade poses against the coupled run. Then halve the coupling interval, maintaining material substep accuracy. Compare common times without event shifting: position<=0.1mm, velocity<=5mm/s, force/moment<=5% (floors1e-6N/1e-8Nm), damage<=0.01, dissipation<=5%, onset timing<=0.5ms, identical failed-group/separation verdicts.
5. Apply returned wrench exactly once to the proper mounted body. Distinguish contact-law reaction, applied native wrench and measured articulation feedback. Verify signs, origins, timestamps and support balance. Do not label a displayed reaction as verified motor effort or close the outstanding motor-work gate.
6. Only after the Section4 damage prerequisites pass, replay the qualified shallow cut with actual robot tracking, controlled stop and two-stage horizontal withdrawal. Full stroke requires the Section4 separation prerequisites. A visible groove does not count as separation.

Deliver coupled/replay/refinement reports, wrench ledger, actual tracking, material histories, support accounting and failure checkpoints. Report prescribed-motion coupling separately from genuinely load-responsive articulation behavior.

## Gate 5D — reset, failure and restart

Test fresh launch, loaded reset, failed-episode reset and post-cut reset once available. Reset both engines, all tissue damage/history, contacts, wrench queues, compensation buffers, controller integrators, clocks, observations and RNG. Restore the exact candidate's fresh starting state; do not heal a continuing cut or rebuild the remainder mid-episode.

Compare reset initial states to fresh launch (exact discrete/history/queue state; positions<=1e-9m and velocities<=1e-9m/s). Replay a short common command sequence using Gate5C physical comparison limits. Add one mid-contact checkpoint restart versus uninterrupted execution, including actuator/controller and contact clock state. Missing post-cut evidence leaves that reset item open.

## Execution discipline and completion

One GPU simulation at a time. Do not compete with the active v43 hold. Perform read-only review and CPU interface preparation meanwhile. Before each expensive run forecast time from a short measured segment and declare a wall cap; preserve recoverable state on a cap. One diagnosed correction and bounded retest per failure, then reassess; no endless branches.

Save each gate's contract, source manifest, actual timestamps, progress, results and raw traces in a separate versioned directory. Update Section5's four checklist items only when their own evidence is complete. The four items map to5A,5B,5C,5D respectively. Preserve experimental validation pending, speed deferred and strict motor-work qualification open. Engine adoption and policy training need a later evidence decision.

First action for Sol: read this plan and the latest Section4 plan; inspect the completed/pending v43 results and process state. Finish the candidate's remaining contact/damage gates. In parallel only in the scheduling sense, prepare5A's interface inventory and CPU analytic fixtures; do not launch a second GPU worker. Then follow5A–5D continuously without asking between routine steps.
