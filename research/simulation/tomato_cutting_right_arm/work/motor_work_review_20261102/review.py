from pathlib import Path
import json,hashlib,numpy as np,shutil
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm'); W=R/'work/motor_work_review_20261102'; O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
S=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/isaacsim')
paths=[Path('/home/omen/IsaacLab/source/isaaclab/isaaclab/actuators/actuator_pd.py'),S/'extscache/omni.physics.tensors-110.3.2+110.3.0.lx64.r.cp312.u7f4/omni/physics/tensors/api.py',S/'extsDeprecated/isaacsim.core.prims/isaacsim/core/prims/impl/articulation.py',S/'exts/isaacsim.robot_setup.gain_tuner.ui/isaacsim/robot_setup/gain_tuner/ui/ui_builder.py']
evidence=[]
for name in ['dry_tracking_corrected','near_approach']:
 p=R/f'runs/native/{name}_20261102_01/measured_motion.npz'
 with np.load(p) as z: fields=list(z.keys())
 evidence.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),fields=fields,measured_drive_effort_recorded=False))
p=R/'runs/native/corrected_exchange_clear_20261102_01/robot_trace.json'; rows=json.loads(p.read_text()); evidence.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),fields=list(rows[0]),measured_drive_effort_recorded=False))
result=dict(status='bounded_source_and_trace_review_complete',native_invocations=0,physics_steps=0,target_steps=0,actual_motor_work_qualified=False,touch_launch_ready=False,installed_solver_measured_candidate='root articulation view get_dof_projected_joint_forces()',candidate_runtime_readback_tested=False,implicit_applied_effort_is_approximate=True,actuation_force_getter_is_not_total_implicit_drive_effort=True,source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},traces=evidence,old_failed_verdicts_unchanged=True,recommended_next_action='One contact-free robot-only measured-effort capture protocol; no loaded touch until interval semantics and complete work accounting are defensible.',stop_rule='One protected invocation, maximum 120 executed robot steps at 1/240s and 180s wall; stop on unsupported/nonfinite/inconsistent readback. No solver/damping/material sweep. Do not infer work qualification from finite or matching effort channels alone.')
(W/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
report='''BOUNDED MOTOR-WORK REVIEW — 2 November 2026

Verdict: source/trace assessment complete. Actual corrected-controller motor work remains unqualified; no loaded contact is authorized by this result. No new simulator process or physics steps were used.

What the installed source establishes
1. IsaacLab ImplicitActuator.compute explicitly describes computed/applied effort as approximate telemetry that may differ from the solver's internal effort (actuator_pd.py:202–227). Reconstructing Kp error + Kd error + gravity from saved commands is therefore not independent measurement of actual implicit drive work.
2. The installed tensor API says set_dof_actuation_forces is independent of the implicit PD force (api.py:1760 onward). The installed legacy get_applied_joint_efforts wrapper returns those explicitly set efforts (articulation.py:1092–1130). This getter must not be substituted for total motor effort.
3. A distinct installed API, get_dof_projected_joint_forces (api.py:1995), projects incoming joint force along the DOF motion direction. Its legacy wrapper is explicitly called get_measured_joint_efforts. The installed PhysX gain tuner records this channel instead of analytical PD effort (ui_builder.py:6487–6520). This is a real candidate measured channel, not proof that it is an isolated motor-work meter.
4. The docs inspected here do not establish the precise interval averaging needed for our discrete work ledger, nor independent separation of drive, joint-friction and limit contributions for our articulation. Full six-axis incoming joint wrench is also a transmitted load, not automatically actuator work. A candidate torque readback alone does not close whole-system energy accounting or the old failed force audit.

Existing evidence
The corrected dry and near-approach NPZ files record actual q/qd, poses, position/velocity commands and gravity feedforward, but no solver-measured joint efforts. The clear integration robot trace likewise records gravity feedforward rather than measured drive effort. Consequently actual implicit motor work cannot be recovered independently from these saved traces. The measured-field inventory and hashes are in measurements.json. Old dry-motion/component passes stay valid. Old moving force/work failures remain failed. No historical file or frozen worker was edited.

Decision and finite next action
Do not launch loaded touch yet. Recommend ONE short contact-free robot-only capture using the existing corrected controller, articulation and verified clear configuration. Record solver-measured projected efforts immediately after each actual step, full incoming wrenches, explicit feedforward, approximate actuator telemetry, actual q/qd before and after, commands, joint ordering/axes and physical clocks. Clone refreshed buffers rather than retaining mutable views. Keep gains, gravity, damping and effort limits unchanged. An initial-state reset must be separated from executed motion.

Bound this protocol to at most120 executed robot steps at1/240s (0.5 simulated seconds), one protected invocation and180s wall time, with separately declared initialization counts before launch. No deformable solve, contact, video, fracture or training. Expected cost is minutes at most, based on the9s static native operator and48s live-clear runs; the180s deadline is a cap, not a runtime guarantee. A failure after usable data ends this protocol; no revised branch or automatic rerun.

Exit: determine whether the measured channel is accessible, fresh, finite and correctly ordered, and whether its sign/origin relationship to independent joint-wrench projection is supported. Projection agreement checks interface semantics, not independent physical accuracy. Establish interval semantics and contributions before choosing a motor-work quadrature; do not double count feedforward if already included. A finite API result alone is not a passing energy gate. If exact motor work remains unresolved, stop with that limitation and present a prospective scoped measurement contract for the user's decision, rather than widening old thresholds or continuing diagnostics.

Near-contact motion/overshoot bounds remain an additional independent prerequisite even if this effort channel becomes usable. Existing65.7micrometre dry tracking error exceeds the20.8micrometre static contact penetration example; no direct lowering to that frozen configuration is justified.

Checklist: assessment complete; measured-effort runtime check untested; complete moving force/work qualification open; loaded touch not ready. Fixed ideal knife mount retained. Experimental validation17 and loaded/post-cut reset22 remain pending.

Primary background (not evidence of installed runtime behavior):
https://nvidia-omniverse.github.io/PhysX/physx/5.6.0/docs/Articulations.html
PhysX documents implicit drives; installed local source is the authority for the API statements above.
'''
(W/'MOTOR_WORK_REVIEW_20261102.txt').write_text(report)
shutil.copy2(W/'MOTOR_WORK_REVIEW_20261102.txt',O/'motor-work-review-20261102.txt')
print(json.dumps({k:result[k]for k in ['status','native_invocations','actual_motor_work_qualified','touch_launch_ready']}))
