V28 — isolated approximate tomato training experiment

User authorization: “Build a separate approximate RL model (Recommended)”.
Existing Isaac/DiSECt scenes, robot, kitchen, grip and detailed-solver evidence
are not replaced. This is not DiSECt, MPM, official CRESSim or calibrated tomato
mechanics. It is a separately implemented GPU elastic bond network.

WHAT RUNS LIVE
The tomato is represented by massive spheres and elastic, massless bonds.
The finite tapered knife acts on the spheres. Its actual motion can spend work
to irreversibly break intersected bonds. No future cut surface is supplied to
the physics, and no mesh is swapped to simulate separation. Broken bonds never
re-form. Disconnected pieces can still push each other through noncohesive
particle contact, and a bottom fixture supports the initial body.

src/environment.py provides reset(ids), step(actions), observations, rewards,
termination and timeout for multiple independent bodies. Six action values are
world-frame blade linear/angular velocities. Material axes use Y-up. Actor observations exclude hidden damage and connectivity. Privileged critic
information and task-evaluation signals are returned separately in info. The default task is one cut
followed by horizontal blade withdrawal. Scripts choose commands online; no
policy has yet been trained. This is a blade-control task, not the existing
articulated robot environment.

VIEW
Run launch_live.sh in a terminal. It opens a separate Isaac Sim stage and runs
the solver live. It does not open or modify the original kitchen scene.
Pause/resume, reset, manual blade motion and horizontal withdrawal controls are
provided. The optional pull-apart test explicitly releases the support and adds
an outward impulse AFTER cohesive separation; it does not create the cut.
Sphere display exposes the actual approximation rather than hiding it behind an
intact cosmetic tomato mesh. Performance with rendering is not the RL benchmark.

APPROXIMATIONS AND LIMITS
- 3.5 mm spacing, 2,803 particles and 31,950 initial bonds at nominal size.
- Saved shape envelope approximately 65 x 55 x 65 mm; sphere envelope differs.
- Mass is preserved at approximately 121.253 g. The collidable spheres occupy
  only about 38% of the old solid volume; bonds bridge the gaps. This is NOT a
  watertight continuum or a skin/pulp/seed model. Features below several particle
  spacings are not physically resolved, and thin slices need separate evaluation.
- Nominal Young's modulus 100 kPa, network small-strain Poisson ratio 0.25 rather
  than the reference's 0.4. Central springs also differ at finite strain.
- Provisional 80 J/m² fracture budgets and an empirical sawing contribution.
  Surface sampling underestimates tested ideal-plane fracture areas by 5–13%.
- Measured imposed-strain force/stress differences from the reference span
  roughly 4–66% across the tested cases. These differences are disclosed, not
  experimental calibration. The old 5% equivalence requirement was explicitly
  waived for this separate approximate model.
- Tapered blade proxy (120 mm edge, 30 mm height, 1 mm spine), not original CAD.
- The 0.1 mm penetration stop concerns collidable spheres and this blade only.
  It does not certify the volume in the gaps or the old continuous tomato.
- 2 N conservative sum of blade loads remains a stop. Contact impulses and
  peak forces depend on time resolution. Numerical refinement results are in
  reports; never interpret them as experimental motor-work validation.
- Default fast step 0.2 ms. A rejected numerical/penetration step can restore the
  COMPLETE state and retry at 0.1 or 0.05 ms. A force stop is not bypassed. A
  refined step size is retained for the rest of that batch episode. Resets clear
  damage/history; unsuccessful actions never earn a cutting-success reward.
- Full-size, multi-cut, changed-size and oblique test outcomes must be read
  from qualification.json, including failures. No unlimited path/size guarantee.

TIMING SCOPE
reports and runs preserve raw failed pilots as well as successful tests.
The complete-task benchmark includes actions, physics, material contact,
fracture, observations, connectivity, reward, terminal decisions and reset.
Articulated-robot dynamics, rendering and learned-policy inference are excluded.
Meeting 100 transitions/s supports a first RL experiment; it does not guarantee
learning convergence or transfer to a real tomato.

EVIDENCE PRESERVATION
parent_manifest.json records the frozen v27 files. Earlier v28 failed box-knife,
coarse and control attempts are retained. snapshots/ records implemented versions.
No experimental-validation or original research gate is marked complete by this
approximate model's results.

TRAINING INTERFACE EXAMPLE
Use CuttingEnv(num_envs=8, dt=0.0002) for the measured fast configuration.
The default dt=0.0001 is the conservative fixed-resolution starting point.
reset(ids) must be called for any completed environments before another step.
The spaces expose 6 bounded actions and actor-state observations; hidden damage
and connectivity appear only in info["critic_observation"] and task diagnostics.
