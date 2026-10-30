# Dedicated guard preparation — partial implementation and tested scope

rl/tomato_preupgrade_guard.py reuses the unchanged production startup/warning/
hard-stop policy and adds nonfinite-input refusal. The CLI only prints a future
native command; it has no execute option, launches nothing and imports no engine.
It reports whether the future worker source exists rather than pretending it is
ready. Twelve tests passed, including real tiny stdlib-only dummy subprocesses:
normal exit, timeout, TERM-ignoring process, spawned child group cleanup,
KeyboardInterrupt cleanup, resource refusal/warning and three monitor errors.
The outer worker enforced original 512MiB/45CPU/55alarm/60parent/one-thread caps
and both shared locks. No native worker, simulation or training was launched.

Process groups are private via start_new_session. Cleanup sends TERM then KILL
to descendants even if the leader exited. Child cleanup tests allow transient
non-executing zombies pending OS reaping but reject any remaining running member.
Tests are supervisor mechanics, not a guarantee that a future GPU/driver process
responds identically. Escaped/new-session descendants are not covered by this
process-group mechanism and require review for the eventual actual worker.

Remaining P5 work: real native monitor acquisition, bounded checkpoint signal/
acknowledgement, report schema, source/config/authorization/deadline validation,
shared-lock ownership and final command integration. Current module does NOT
claim that complete native launch path is ready. Native execution is disabled.
The production guard/controller and frozen criteria were not edited.

Next P6 source references (read as text only):
newton/examples/vbd/example_vbd_gripper_soft_grid.py
newton/examples/vbd/example_vbd_gripper_soft_triangle.py
newton/tests/test_collision_pipeline.py
newton/tests/test_solver_vbd.py
in /home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/.
These contain full-surface contact usage. Inspect exact constructors, geometry,
SDF configuration, spring/material setup, collision capacities, state update and
reaction collection. Build the smallest independent coupon/config source,
keeping runtime imports behind a disabled future execution entry point. Do not
replace the robot hand solver or fabricate a native damage law.
