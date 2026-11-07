from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/reset_replay_20261031_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'reset_replay_measurements.json').read_text());assert sup['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
previous=json.loads((root/'runs/native/contact_feedback_20261031_02/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in previous.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_reset_replay_worker.py','tomato_reset_replay_reference.py','tomato_turning_sequence_reference.py','tomato_contact_feedback_worker.py','tomato_offset_contact_reference.py','tomato_physx_proxy_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_reset_replay_reference.py')]+[Path(n) for n in installed]
files.extend([Path('/home/omen/IsaacLab/source/isaaclab_physx/isaaclab_physx/assets/rigid_object/rigid_object.py'),Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/sim/collide.py'),Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/sim/contacts.py')])
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
errors={key:max(c['assessment']['max_errors'][key] for c in m['comparisons']) for key in m['comparisons'][0]['assessment']['max_errors']}
report=dict(supervisor=sup,measurements=m,max_replay_errors=errors,source_sha256=pins,focused_tests_passed=13,
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/'newton-physx-reset-replay-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX reset and replay — 31 October 2026

PASS for reset after cleared contact and reset during active contact in both persistent analytic turning fixtures. Checklist item 15 remains in progress. Checklist item 22, which concerns the eventual robot/material scene, is not completed by this isolated test.

The same identity-oriented and Y-rotated/offset-COM particle/box fixtures, models, bodies, Newton solvers, state buffers and collision pipelines were retained throughout. This was not a fresh-process restart. Particle/rigid mass, synthetic isotropic inertia, zero gravity/damping/friction and fixed 1750 N/m contact stiffness were unchanged from the earlier turning test.

Schedule: run a 16-interval baseline; reset both fixtures after their 12 cleared-contact coast intervals; replay two intervals until both have active contact; reset both fixtures again while the active contact count is one; replay the full 16 intervals. Exactly 68 Newton steps and 34 shared CPU PhysX steps were executed, dt=1/1200 s. Two reset cycles covered both bodies, for four dirty-wrench reset checks and four trace comparisons.

Before each reset both instantaneous and permanent wrench queues were deliberately populated with the known diagnostic force (99, -55, 33) N and torque (1, 2, 3) N m. No simulation step applied these loads. RigidObject.reset cleared both queues; the initial link pose and COM twist were written back by the PhysX owner, then write_data_to_sim cleared the backend force. Both restored rigid starting packets matched exactly.

SolverVBD.reset was called on both reusable Newton states with PARTICLE_Q/PARTICLE_QD flags. Particle defaults were restored exactly; externally owned body state remained unchanged by Newton reset, as required by the installed API. State force arrays were cleared. The pipeline's reset_contact_matching discarded correspondence history, Contacts.clear invalidated the old active prefix, and the PhysX reset pose/twist was copied into both Newton body states. Fresh collision detection was mandatory before each subsequent solve. No manual editing of solver caches or reconstruction of models/solvers was used. The installed VBD reset documentation says particle previous positions and body-particle history rebaseline/rebuild on the next step; this test validates the resulting behavior for these fixtures, not that every internal array is zero after reset.

The two-interval replay matched the baseline prefix for both fixtures. The full replay after active-contact reset matched all 16 baseline intervals. Every compared numerical field had zero measured difference: before/after particle position and velocity, link position and quaternion, COM linear/angular velocity, soft force, and COM reaction torque. Contact counts and interval indices matched exactly. Final replay contacts cleared naturally after four contact intervals, followed by 12 zero-input coast intervals per fixture. All inherited per-step trajectory, impulse and angular-balance checks also passed.

Replay limits: positions 1e-7 m, linear velocity 2e-5 m/s, angular velocity 2e-6 rad/s, quaternion-component distance 5e-7, force 2e-5 N, torque 2e-7 N m. Limits were not relaxed. Four focused replay/reference/guard-contract tests plus nine existing supervisor tests passed; controls reject an old angular velocity, missing contact, and leftover force.

'''
s+=f'''The protected run completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. There were no memory warnings or resource-monitor errors; no owned live processes remained. Snapshots/hashes include the installed reset/contact APIs. Original frozen project files and previously pinned installed dependencies remain unchanged.

Next bounded step: validate unequal principal moments of inertia in rotated rigid frames, where torque and angular acceleration need not align. This extends the current isotropic-body test toward robot-link behavior. General anisotropic rotating dynamics, articulated-link coupling, reset of material damage/history, long-run/time-step sensitivity, general contact energy and the real blade's full-surface collision backend remain unvalidated. No robot or blade was loaded.
'''
(out/'newton-physx-reset-replay-check-20261031.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['progress']='Turning exchange and contact clearing pass. Reset after coast and during active contact replays exactly for both fixtures; dirty force queues clear. Next: unequal rotational inertia in rotated frames. Full coupling validation remains open.'
i['evidence']='newton-physx-reset-replay-check-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nIsolated reset/replay: newton-physx-reset-replay-check-20261031.txt\nItem 15: reset after coast and active contact replays exactly. Next: unequal rotational inertia in rotated frames. Item 22 remains unvalidated for the future robot/material scene.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check reset and replay','Check turning resistance by axis').replace('Repeated turning contact passes; forces clear after separation. Next: reset the test and check that it repeats cleanly.','Reset and replay match exactly, including reset during contact. Next: check a body that resists turning differently around each axis.');p.write_text(s)
print(json.dumps(dict(replay_errors=errors,reset_cycles=2,dirty_wrench_resets=4,source_files_snapshotted=len(files)),indent=2))
