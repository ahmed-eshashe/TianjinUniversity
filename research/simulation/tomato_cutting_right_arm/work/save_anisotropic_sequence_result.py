from pathlib import Path
import hashlib,json,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/anisotropic_sequence_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'anisotropic_sequence_measurements.json').read_text());assert sup['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
prev=json.loads((root/'runs/native/spin_near_origin_2400_20261031_01/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in prev.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_anisotropic_sequence_worker.py','tomato_anisotropic_sequence_reference.py','tomato_half_step_reaction.py','tomato_anisotropic_reference.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_physx_proxy_reference.py','tomato_isaac_startup_guard.py','tests/test_tomato_anisotropic_sequence_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
steps=[s for c in m['cases'] for s in c['steps']]
metrics={key:max(s[key] for s in steps) for key in ('force_error_n','torque_error_nm','point_error_m')}
for section in ('pulse_check','motion_checks'):
 for key,value in steps[0][section].items():
  if isinstance(value,(int,float)) and 'error' in key:metrics[key]=max(s[section][key] for s in steps)
report=dict(passed=True,scope='32 near-origin half-step exchanges in two unequal-inertia analytic particle/box fixtures.',
 supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=12,
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/'newton-physx-unequal-inertia-sequence-20261101.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX repeated unequal-inertia contact — 1 November 2026

PASS for 32 consecutive near-origin half-step contact exchanges in each of two isolated analytic particle/box fixtures. Checklist item 15 remains open for broader coupling qualification. Earlier far-origin precision failures remain preserved.

The identity and obliquely rotated/offset-COM fixtures both began at actor origin (0,0,0) with zero initial velocities. Their PhysX collisions were disabled, so overlap did not couple the two fixtures. The second body used a 60-degree rotation about normalized (1,2,3) and local COM (0.002,-0.001,0.0005) m. Each had a 0.01 kg Newton particle initially at body-local (0.004,0.003,0.001) m and a 0.02 kg PhysX box whose top was local z=0.002 m. Synthetic principal moments were explicitly specified/read back as (0.0001,0.0002,0.00025) kg m². They are diagnostic mass properties, not a claim about the inertia of the displayed geometry. Gyroscopic forces were enabled and read back.

Exactly 64 Newton steps and 32 shared CPU PhysX steps ran at dt=1/2400 s, for 0.0133333 seconds per fixture. The same models, solvers, pair of states, collision pipelines and contact buffers were reused. Every interval copied PhysX link pose/world COM twist into both Newton body states exactly, regenerated contacts, solved the particle against a frozen proxy for 16 iterations, collected the native contact reaction from actual solver caches, applied the world force/COM torque once with positions=None, stepped PhysX, copied state back exactly and swapped soft states. The isolated reaction collector uses the same 1/2400 s step as the solve. Contact stiffness was the native fixed cache 1750 N/m; damping, friction, radius/margin and gravity were zero. TGS used 16 force substeps and zero velocity iterations.

Each fixture generated eight active contacts, then separated naturally and coasted for 24 intervals. No new wrench was queued after contact cleared. Both instantaneous and permanent composers remained inactive, linear velocity stayed constant, and spin/angular momentum followed the unequal-inertia reference within the declared short-step limits. Fresh normals matched the evolving body orientation; projected points, force directions and torque lever arms were checked every active interval. Contact did not reappear.

The independent soft reference uses the current frozen top-plane pose and incoming particle velocity. Rigid reference acceleration transforms torque and the gyroscopic term with the initial world inertia tensor for each short interval, then uses the declared TGS force schedule and sequential quaternion increments. This is a small-spin, short-interval approximation, not a claim to reproduce PhysX's complete anisotropic integrator. Both per-step response and a full reference trajectory from the initial state were checked. Body spin angular momentum was computed with the updated world inertia tensor, not scalar inertia times angular velocity. Linear and angular impulses were accumulated from actual force/torque samples; the total orbital-plus-spin increment includes the known TGS translation splitting correction. General contact work/energy was not qualified by this step.

Maximum errors across both fixtures:
'''
for key,value in metrics.items():s+=f'  {key}: {value:.9g}\n'
s+='\nFixture coverage:\n'
for c in m['cases']:s+=f"  {c['id']}: {32-c['coast_steps']} contact steps, {c['coast_steps']} coast steps; active-contact normal change {c['active_contact_normal_change']:.9g}.\n"
s+='''
Retained gates: force 2e-5 N, COM torque 2e-7 N m, contact point and particle/COM/trajectory position 1e-7 m, particle/COM velocity 2e-5 m/s, angular velocity 2e-6 rad/s, orientation 1e-6 rad, accumulated linear impulse 2e-7 N s, angular impulse/balance 2e-8 N m s. No tolerances were relaxed. Three focused independent-reference/guard-contract tests and nine existing supervisor tests pass, including the isotropic limit and exact bounded step counts.

'''
s+=f'''The protected worker completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. There were no resource warnings or monitor errors and no owned live processes remained. Source snapshots/hashes were saved. Original frozen project inputs and pinned installed dependencies remain unchanged.

Next bounded step: inspect and validate the force-transfer interface for a simple one-joint articulated proxy before applying it to a robot. Constraint reactions and joint dynamics require different balance checks from a free body. Full articulated robot coupling, general contact energy, broader coordinate accuracy, reset of material history, long-run stability, cutting material and the real blade's collision-generated contact backend remain unvalidated. No robot or real blade was loaded.
'''
(out/'newton-physx-unequal-inertia-sequence-20261101.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(i for i in d['items'] if i['id']==15)
i['progress']='32 near-origin half-step unequal-inertia exchanges pass for both fixtures: eight contact steps, 24 zero-input coast steps, updated world COM torque and accumulated linear/angular impulse. Next: simple jointed-link force transfer. Full coupling remains open.'
i['evidence']='newton-physx-unequal-inertia-sequence-20261101.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — repeated unequal-inertia contact: newton-physx-unequal-inertia-sequence-20261101.txt\nBoth 32-step near-origin/half-step fixtures pass, with 24 coast intervals each. Item 15 remains open. Next: simple jointed-link force transfer.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Combine spinning with contact','Check force transfer through a joint').replace('Near-origin spin passes the unchanged accuracy limits. Next: repeat contact with unequal turning resistance in this tested setup.','Repeated contact with unequal turning resistance passes for both test bodies. Next: check force transfer on a simple jointed link.').replace('Updated 31 Oct 2026','Updated 1 Nov 2026');p.write_text(s)
print(json.dumps(metrics,indent=2))
