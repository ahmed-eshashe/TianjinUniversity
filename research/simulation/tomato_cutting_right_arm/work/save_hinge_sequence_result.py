from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/hinge_sequence_20261101_01';sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'hinge_sequence_measurements.json').read_text());assert sup['passed']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/hinge_contact_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_hinge_sequence_worker.py','tomato_hinge_sequence_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_hinge_sequence_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
steps=[s for c in m['cases'] for s in c['steps']]
metrics={key:max(s[key] for s in steps) for key in ('force_error_n','point_error_m','torque_error_nm')}
for key in steps[0]['checks']:metrics[key]=max(s['checks'][key] for s in steps)
report=dict(passed=True,scope='32 persistent particle-to-hinge exchanges with natural separation in both orientations.',
 supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=13,
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/'newton-physx-hinge-sequence-check-20261101.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX repeated hinge contact and natural separation — 1 November 2026

PASS for 32 persistent coupled exchanges in each of two passive-hinge fixtures. The particles separated naturally with no reposition, velocity reset or artificial contact deletion. Checklist item 15 remains open for broader coupling qualification.

Both near-origin, locally authored fixed-base articulations retain the previous identity and 90-degree-yaw orientations. Each moving link has mass 0.02 kg, COM radius 0.01 m from its Z hinge and synthetic COM Z inertia 0.0001 kg m². One 0.01 kg CUDA Newton particle starts 1 mm inside the link's +Y side at link-local (0.004,0.004,0) m. CPU PhysX owns joint motion and constraints; Newton owns the particle and carries a kinematic link proxy. No drive, joint stiffness/damping/friction, gravity or PhysX collisions were enabled. There are no cross-fixture constraints. No robot, real blade, remote asset or cutting material was loaded.

The same model, solver, pipeline, contact buffers and pair of Newton states were reused. Every interval validated the latest PhysX link pose/COM twist in both Newton body states, regenerated collisions, solved the particle for 16 iterations against the frozen proxy, collected the native contact force/COM torque using actual solver caches, delivered the world wrench once to the selected moving link, stepped PhysX, copied actual rigid state back exactly and swapped soft states. The fixed contact stiffness was 1750 N/m with zero damping/friction/radius/margin. dt=1/2400 s, TGS position substeps=16, velocity iterations=0.

Exactly 64 Newton steps and 32 shared CPU PhysX steps ran, for 0.0133333 s per fixture. There were 66 exact link-state packet echo events (initial plus after every PhysX step for each fixture), each copying pose and COM twist into both actual Newton states. Every fixture generated 10 contact intervals followed by 22 cleared-contact coast intervals. No new wrench was queued during coast; contact did not reappear. Normals were checked against the updated link orientation, and both fixtures exercised a measurable contact-normal change.

The independent reference uses incoming particle velocity and the current frozen +Y plane to solve unilateral soft contact. Generalized hinge effort includes both force about the pivot and the reaction torque about COM. The effective one-DOF inertia was independently checked against I_COM+m*r². Per-interval particle/joint state and a separately advanced full trajectory were checked. Actual delivered effort and particle force were integrated independently to compare accumulated hinge/particle impulses. Particle orbital angular momentum plus effective hinge inertia times joint velocity was checked about the free hinge axis. This does not assert free-body linear momentum conservation for the fixed-base constraint. Joint coast velocity stayed constant after contact disappeared. General contact work/energy was not qualified in this step.

Fixture coverage:
'''
for c in m['cases']:
 s+=f"  {c['id']}: {c['contact_steps']} contact steps, {c['coast_steps']} coast steps; normal change {c['active_normal_change']:.9g}; final joint velocity {c['steps'][-1]['after']['qd']:.12g} rad/s.\n"
s+='\nMaximum errors across all fixture intervals:\n'
for key,value in metrics.items():s+=f'  {key}: {value:.9g}\n'
s+='''
Retained gates: force 2e-5 N, projected point/particle position and particle trajectory 1e-7 m, COM torque 2e-7 N m, joint position/trajectory 1e-6 rad, joint/particle velocity and accumulated velocity reference 2e-5 in their respective units, accumulated particle impulse 2e-7 N s, joint impulse/hinge-axis angular balance 2e-8 N m s, and coast joint velocity change 2e-6 rad/s. Each fixture required at least three coast intervals and active-normal change of at least 1e-5. No tolerance was relaxed. Four focused host-reference/guard-contract tests and nine supervisor tests passed, including natural separation, rotational equivalence, angular balance and stale-force expectations.

'''
s+=f'''The protected run completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No memory warnings or monitor errors occurred, and no owned live processes remained. Source snapshots/hashes were saved. Original frozen production inputs and previously pinned installed dependencies remain unchanged.

Next bounded step: reset and replay these coupled articulated fixtures after coast and during contact, checking joint state, force queues, Newton state and collision history. Multi-joint robot dynamics, jointed contact work/energy, broader coordinate precision, material cutting and the real blade's collision backend remain unvalidated.
'''
(out/'newton-physx-hinge-sequence-check-20261101.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(i for i in d['items'] if i['id']==15)
i['progress']='Both passive hinges pass 32 repeated Newton-contact exchanges: 10 contact steps then 22 natural coast steps, updated normals, accumulated joint/particle impulse and hinge-axis angular balance. No particle reset/reposition. Next: jointed reset and replay.'
i['evidence']='newton-physx-hinge-sequence-check-20261101.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — repeated hinge contact: newton-physx-hinge-sequence-check-20261101.txt\nBoth 32-step fixtures pass: 10 contact intervals, 22 natural coast intervals; no reposition/reset. Next: jointed reset/replay. Item 15 remains open.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Repeat jointed contact and check separation','Check jointed reset and replay').replace('Actual Newton contact drives the hinge correctly in both orientations. Next: repeat the exchange and check natural separation.','Both hinges pass repeated contact and natural separation. Next: check that the jointed scene resets and repeats cleanly.');p.write_text(s)
print(json.dumps(metrics,indent=2))
