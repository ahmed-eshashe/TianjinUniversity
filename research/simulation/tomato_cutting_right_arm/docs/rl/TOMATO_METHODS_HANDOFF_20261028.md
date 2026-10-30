# Transferable tomato validation methods — 28 October 2026

The user redirected work from further tiny insertion steps to checks useful for
the larger simulation. The depth continuation automation is paused. The accepted
9.638916015625 mm checkpoint and its next-target candidate remain preserved;
no accepted physical state was changed. The original authorization deadline and
all frozen mechanics, grasp and resource safeguards remain unchanged.

## Completed reference check

`rl/tomato_wrench_contract.py` is a small, standalone SI reference for a future
adapter. It rotates force and moment into a common world frame and shifts the
moment to a common reference point using `moment + arm cross force`. It reports
force residuals in N separately from moment residuals in N m and computes
instantaneous mechanical power in W. Rotation matrices must be finite,
orthonormal and right handed. These algebra validation tolerances do not change
any existing physical acceptance tolerance.

Twelve analytic tests cover known lever arms, rotations, shifts, action/reaction
and power invariance. Deliberate errors include doubled action signs, omitted
moment arms, millimetres supplied as metres, invalid axes and nonfinite inputs.
Seven existing false-separation tests also pass, including a tiny remaining
cohesive bridge and hidden bulk/volume connections. Total: **19 passed**.

Evidence: `runs/offline/tomato_methods_20261028_01/tests.json` records exact source
hashes, runtime and memory; `quota_checks.json` records actual before/after usage
readings. The run used one thread, shared locks, 512 MiB address-space limit,
45 s CPU, 55 s alarm and 60 s parent timeout. Peak RSS was approximately 19.3 MiB.
Existing session source hashes were verified unchanged. No simulator or training
modules were imported. No controller was modified.

## What this proves and what remains open

These tests establish reference calculations, not simulator coupling, a real
sensor model, calibrated tomato forces or a completed slice. They provide known
answers against which an adapter's exported loads can be tested. A unit mistake
is detectable against known reference data; arbitrary data cannot reveal its own
missing unit declaration. Callers must declare units, named bodies, frames,
origins, timestamp and sampling convention. Pair residuals require synchronized
samples, a shared reference point, and the same contact interaction isolated
from gravity, fixtures and other loads. Instantaneous power alone does not prove
an integrated work ledger or stable coupling.

## Next method and integration checks

1. Specify a backend adapter output containing SI blade/tomato contact wrenches,
   frame transforms, body identifiers, timestamps, velocities at the reported
   origins and contact impulse/force sampling conventions. Use these reference
   cases to test the adapter before interpreting tomato results. Confirm actual
   wrist sensor axes before using force channels; torque-only sensing is not
   full force measurement.
2. After the RAM upgrade, remeasure RAM and VRAM and use the existing guarded
   startup/runtime floors. Implement a separate reviewed tomato worker; the
   current guard has no ready tomato mode. Begin with one headless contact
   coupon and nonfracturing indentation. Verify equal-and-opposite loads in a
   common frame and integrated work, including fixture and tool work. Define
   adapter-specific numerical tolerances before those runs; do not borrow
   arbitrary algebra tolerances as physical acceptance limits.
3. Test no-contact, off-plane, partial-cut, stop/withdrawal and reset controls.
   Reuse the existing offline damage/contact checks as expectations, then gather
   new backend evidence. A saved offline result is not a backend pass.
4. Establish timestep and mesh sensitivity with consistent area/energy scaling.
   Current single-branch insertion progress is not convergence evidence.
5. Require all physical connections to disappear and independent motion/contact
   after withdrawal before claiming release. The prototype plan requires at
   least one simulated second of observation; an algebraic topology test or a
   supported quasistatic reclosure check cannot substitute for it.

These steps follow `NEWTON_TOMATO_PROTOTYPE_PLAN.md` and
`TOMATO_SLICING_IMPLEMENTATION_PLAN.md`. Robot dynamics, sensor calibration,
backend implementation and training remain separate work. More RAM provides
capacity; these tests help determine whether the resulting physics is credible.
