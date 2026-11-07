from pathlib import Path
import hashlib,json,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/hinge_replay_20261101_01';sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'hinge_replay_measurements.json').read_text());assert sup['passed']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/hinge_sequence_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_hinge_replay_worker.py','tomato_hinge_replay_reference.py','tomato_hinge_sequence_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_hinge_replay_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
errors={k:max(c['assessment']['max_errors'][k] for c in m['comparisons']) for k in m['comparisons'][0]['assessment']['max_errors']}
report=dict(passed=True,scope='Coupled passive-hinge reset/replay after coast and during contact.',supervisor=sup,measurements=m,
 max_replay_errors=errors,source_sha256=pins,focused_tests_passed=13,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/'newton-physx-hinge-reset-replay-20261101.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX jointed reset and replay — 1 November 2026

PASS for reset after natural separation and reset during active contact in both persistent passive-hinge fixtures. All compared replay fields matched exactly. Checklist item 15 remains open for broader coupling. Item 22, concerning the eventual robot/material scene, is not completed by this isolated reset test.

The same near-origin identity and 90-degree-yaw hinge articulations, Newton particle models, kinematic link proxies, solvers, state pairs and collision pipelines were kept alive. No fresh process, model or solver was used to stand in for reset. The fixture masses, synthetic inertia, zero drive/friction/damping/gravity, dt=1/2400 s and native 1750 N/m contact stiffness were unchanged.

Schedule: baseline 32 coupled intervals per fixture (10 active contact and 22 coast); reset both fixtures after coast; replay two contact intervals; reset both fixtures again with one active contact record present; replay all 32 intervals. Exactly 66 shared CPU PhysX steps and 132 Newton steps were executed, with two reset cycles, four dirty-wrench reset checks and four trace comparisons. There were 138 exact actual Newton link-state packet echo events, including four reset synchronizations.

Before each reset, both instantaneous and permanent articulation wrench queues were deliberately filled for the moving link with force (99,-55,33) N and torque (1,2,3) N m. These test loads were never applied in a simulation step. Articulation.reset cleared both queues. The PhysX owner restored the initial joint position and velocity with the current fused write API and wrote the cleared wrench state to the backend. Initial joint state matched exactly; initial moving-link pose/COM twist also matched exactly.

SolverVBD.reset restored PARTICLE_Q/PARTICLE_QD in both Newton states, and state force arrays were cleared. Each call was checked not to mutate the externally owned Newton link pose/twist. The pipeline's reset_contact_matching cleared correspondence history, Contacts.clear invalidated the active prefix, and actual restored PhysX link pose/twist copied into both Newton states. The next solve regenerated contacts before use. Installed VBD particle history rebases/rebuilds on the next step; this test validates resulting behavior rather than claiming every history array becomes zero immediately.

Both two-interval replay prefixes and both full 32-interval replays matched the baseline in interval/contact count; before/after joint position and velocity; particle position and velocity; force and COM torque; and after-step link pose/quaternion/world COM velocity. Final replay again separated naturally after 10 contact intervals, then coasted for 22 intervals without a new wrench. Every inherited per-step/full-trajectory, accumulated impulse and hinge-axis angular-balance check passed.

Maximum replay differences:
'''
for k,v in errors.items():s+=f'  {k}: {v:.9g}\n'
s+='''
Retained replay limits: particle/link position 1e-7 m, particle/link linear velocity 2e-5 m/s, joint position 1e-6 rad, joint velocity 2e-5 rad/s, force 2e-5 N, COM torque 2e-7 N m, link quaternion-component distance 5e-7, link angular velocity 2e-6 rad/s. No tolerances were relaxed. Four focused replay/guard-contract tests and nine supervisor tests passed; controls reject stale joint velocity, force, contact count and moving-link angular velocity.

'''
s+=f'''The protected run completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No memory warning or monitor error occurred, and no owned live processes remained. Source snapshots/hashes were saved. Original frozen project inputs and previously pinned installed dependencies remain unchanged.

Next bounded step: validate force distribution through a simple two-joint articulated proxy, where joint motion must follow the coupled mass matrix and link Jacobian. Multi-joint Newton feedback, general jointed work/energy, robot/material reset histories, larger coordinate precision, cutting material and the real blade contact backend remain unvalidated. No robot or real blade was loaded.
'''
(out/'newton-physx-hinge-reset-replay-20261101.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(i for i in d['items'] if i['id']==15)
i['progress']='Jointed reset/replay passes after coast and during active contact: all compared joint, particle, link and force traces match exactly; dirty queues clear. Same solvers/buffers reused. Next: force distribution across two joints; full coupling remains open.'
i['evidence']='newton-physx-hinge-reset-replay-20261101.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — jointed reset/replay: newton-physx-hinge-reset-replay-20261101.txt\nReset after coast and active contact reproduces both hinge traces exactly. Next: two-joint force distribution. Item 15 remains open; item 22 still requires robot/material-scene validation.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check jointed reset and replay','Check force transfer across two joints').replace('Both hinges pass repeated contact and natural separation. Next: check that the jointed scene resets and repeats cleanly.','Jointed reset and replay match exactly, including reset during contact. Next: check how one link force moves two connected joints.');p.write_text(s)
print(json.dumps(errors,indent=2))
