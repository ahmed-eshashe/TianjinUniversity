from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/contact_feedback_20261031_02'
supervisor=json.loads((run/'supervisor_result.json').read_text())
measurements=json.loads((run/'contact_feedback_measurements.json').read_text())
assert supervisor['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
unchanged=all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
assert unchanged
files=[root/'rl'/n for n in ('tomato_contact_feedback_worker.py','tomato_partitioned_reference.py','tomato_isaac_startup_guard.py','tests/test_tomato_partitioned_reference.py')]
files.extend([Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src')/n for n in ('solvers/vbd/solver_vbd.py','solvers/vbd/rigid_vbd_kernels.py','solvers/coupled/interface.py')])
files.extend([Path('/home/omen/IsaacLab/source')/n for n in ('isaaclab_physx/isaaclab_physx/physics/physx_manager.py','isaaclab_physx/isaaclab_physx/physics/physx_manager_cfg.py','isaaclab_physx/isaaclab_physx/sim/schemas/schemas_cfg.py')])
manifest={}
for i,p in enumerate(files):
    target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=manifest,original_frozen_sources_unchanged=unchanged),indent=2)+'\n')
report=dict(supervisor=supervisor,measurements=measurements,source_integrity=manifest,
    original_frozen_sources_unchanged=unchanged,focused_tests_passed=15,
    initial_failed_run=str(root/'runs/native/contact_feedback_20261031_01'),
    failed_gate_cause='Reference assumed one full force update for PhysX position; installed TGS default uses force per position iteration. Unchanged position/velocity/force/impulse/work tolerances; corrected discrete reference with explicit/readback 16 TGS position iterations, zero velocity iterations.',
    documentation='https://nvidia-omniverse.github.io/PhysX/physx/5.7.0/docs/Simulation.html')
(out/'newton-physx-contact-feedback-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'newton-physx-contact-feedback-check-20261031.txt').write_text('''Newton–CPU PhysX contact feedback — 31 October 2026

PASS for one declared partitioned interval in two isolated synthetic fixtures. Checklist item 15 remains unfinished; no repeated-loop, robot or blade qualification is claimed.

Two 0.02 kg CPU PhysX boxes were paired with fresh CUDA Newton models containing one 0.01 kg particle each. Newton's boxes were kinematic proxies; PhysX exclusively owned rigid motion. Initial velocities, local COM offsets, gravity, damping and friction were zero. PhysX collisions were disabled, and only Newton generated contact. Shape/soft stiffnesses were 2500/1000 N/m, giving the actual fixed native cache 1750 N/m. Contact radii and margins were zero. No robot, blade or material-cutting model was loaded.

Schedule at dt=1/1200 s: read CPU pose/twist, copy exactly into both Newton body states, generate contacts, solve Newton particles for 16 iterations with the proxy frozen, collect final contact force through the native contact helper with actual solver caches/previous particle state, apply the opposite force and COM torque once through the instantaneous PhysX composer, advance PhysX once, and copy its updated pose/twist exactly back into both Newton states. This explicit global-contact collector does not use the default external-rigid momentum harvester, which would not recover reaction from the frozen proxy. Body state remained unchanged during each Newton solve. This fixture has zero contact torque.

Exactly two Newton steps (one per fresh fixture) and one shared PhysX step were executed. The contact case generated one particle/box contact; the clear control generated none. The native final contact force was 1.56037152 N. Particle velocity was +0.13003097 m/s and PhysX box velocity -0.06501549 m/s. Momentum residual was zero at recorded float32 precision; maximum impulse residual was 1.20e-10 kg m/s. The clear control had zero force and zero motion.

The first run correctly failed its position/work gates because the reference assumed a single semiimplicit force update for the PhysX body. Installed IsaacLab enables external force application at each TGS position iteration. The corrected worker explicitly specifies and reads back TGS, 16 position iterations, zero velocity iterations, and force-per-iteration. The independent reference sums 16 constant-force substeps, giving box displacement dt*v_final*17/32. This changes the integration reference, not the tolerances. The initial failed run is preserved. NVIDIA documents this force-application behavior: https://nvidia-omniverse.github.io/PhysX/physx/5.7.0/docs/Simulation.html

With that declared schedule, position error was 8.30e-12 m, velocity error 6.23e-9 m/s, and force error 6.93e-8 N. Work/energy identity error was 1.37e-11 J. Energy is not conserved by this split implicit scheme: measured change was -9.6731e-5 J. The audit separately accounts for particle/PhysX numerical dissipation (8.7182e-5 J), the potential quadratic term (1.6457e-5 J), and positive frozen-proxy splitting work (6.9078e-6 J). The force is evaluated before the PhysX recoil, so it differs from stiffness times the final coupled penetration.

Unchanged gates: position 1e-7 m, velocity 2e-5 m/s, force 2e-5 N, momentum/impulse 2e-7 kg m/s, work/energy identities 2e-8 J. Six focused reference tests and nine existing guard tests pass. The reference tests reject missing reaction and the wrong single-step PhysX position assumption.

The passing protected run completed in 6.22 seconds with at least 23.20 GB available RAM and 7.52 GB free GPU memory. No memory warning, monitor error or owned live process remained. Source snapshots/hashes and original frozen-source integrity were saved. Original production files and installed libraries were not modified.

Next bounded step: repeat several coupled intervals with fresh collision records and check state synchronization, impulse accumulation, contact clearing and energy/work. Rotation/nonzero-COM contact feedback, articulated robot links, reset behavior, time-step sensitivity and the real blade's collision-generated full-surface path remain unvalidated.
''')
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());item=next(i for i in d['items'] if i['id']==15)
item['progress']='One Newton-contact → CPU PhysX reaction interval passes: native force, recoil, exact state echo, impulse and schedule-specific work checks; clear control passes. Next: repeated intervals and contact clearing. Full coupling validation remains open.'
item['evidence']='newton-physx-contact-feedback-check-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';s=p.read_text();s+='\nOne-interval Newton–PhysX contact feedback: newton-physx-contact-feedback-check-20261031.txt\nItem 15 remains in progress. Next: repeated coupling intervals and fresh contact clearing.\n';p.write_text(s)
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Test contact-force feedback','Repeat the contact exchange').replace('CPU PhysX state/force input passes, including CUDA echo and stale-force clearing. Next: actual Newton contact reaction feedback.','One contact-force exchange passes, including recoil, momentum and work checks. Next: repeat the exchange and verify contact clearing.');p.write_text(s)
print(json.dumps(dict(original_sources_unchanged=unchanged,passing_run=str(run),source_files_snapshotted=len(files))))
