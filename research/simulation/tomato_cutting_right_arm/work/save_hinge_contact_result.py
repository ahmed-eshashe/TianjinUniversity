from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/hinge_contact_20261101_01';sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'hinge_contact_measurements.json').read_text());assert sup['passed']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/hinge_interface_20261101_03/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_hinge_contact_worker.py','tomato_hinge_contact_reference.py','tomato_hinge_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_hinge_contact_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={key:max(c[key] for c in m['cases']) for key in ('force_error_n','point_error_m','torque_error_nm','coast_joint_velocity_change_rad_s')}
for section in ('pulse_check','balance_checks'):
 for key in m['cases'][0][section]:metrics[key]=max(c[section][key] for c in m['cases'])
report=dict(passed=True,scope='One actual contact exchange plus deliberate clear control per passive hinge.',
 supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=13,
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/'newton-physx-hinge-contact-check-20261101.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX particle contact on a passive hinge — 1 November 2026

PASS for one actual contact exchange and one deliberate clear-control interval in each of two passive-hinge fixtures. This connects an actual Newton particle reaction to an articulated PhysX link and copies resulting rigid state back into Newton. It does not yet validate repeated jointed contact or natural separation. Checklist item 15 remains open.

The locally authored, near-origin fixed-base hinge scenes and passive joint settings match the prior interface check: identity and 90-degree yaw orientations, one moving 0.02 kg link, COM 0.01 m from the Z hinge, COM Z inertia 0.0001 kg m², and no joint drive, stiffness, damping, friction or gravity. CPU PhysX owns hinge motion and constraints. Visual geometry has no PhysX collisions. No robot, real blade, remote asset or cutting material was loaded.

A separate CUDA Newton model for each fixture owns one 0.01 kg particle and a kinematic box proxy of the moving link. The proxy has half-extents (0.01,0.005,0.002) m and a zero local COM matching the link. The particle begins at link-local (0.004,0.004,0) m, 1 mm inside the +Y side. Native shape/soft stiffnesses 2500/1000 N/m produce the actual fixed cache 1750 N/m; damping, friction, radius and margin are zero. The collision pipeline generated one native particle contact, not a manually inserted record.

At dt=1/2400 s, actual articulation link pose and world COM twist were staged from CPU and copied exactly into both actual CUDA Newton State body arrays. Newton solved the particle for 16 iterations while the externally owned proxy stayed frozen. The native contact helper collected the final force, projected point and world reaction torque using the actual solver caches and previous-particle state. That opposite force and COM torque were sent once to the selected moving link, with positions=None and world-frame input. PhysX advanced once, and its resulting link pose/twist copied back exactly into both Newton states.

Independent +Y-plane arithmetic checked final force, projected point, COM torque and soft particle position. A native force in local +Y acts on the particle, so its opposite drives negative hinge rotation. The generalized hinge effort includes both the COM force lever arm and COM torque. With world contact X lever 0.014 m in the identity fixture, effort is -0.014 times force magnitude. The measured articulation mass matrix matched effective inertia I_COM + m*r². Joint velocity/position were checked against the declared 16-substep TGS schedule. Particle linear impulse and total hinge-axis angular momentum (particle orbital contribution plus effective hinge inertia times joint velocity) were checked independently. Full free-body linear-momentum conservation is not applicable to a fixed-base constraint.

For the clear control, the particle was explicitly repositioned to current-link local (0.004,0.008,0) m and its velocity explicitly reset to zero in both Newton states. The existing pipeline regenerated zero contacts, the same solver advanced a clear soft step, and no new rigid wrench was submitted. The hinge then coasted one step with unchanged joint velocity. This is a deliberate outside-particle control, not natural contact separation. Impulse balance is not asserted across that externally imposed reposition/reset.

Exactly four Newton steps (two per fixture) and two shared CPU PhysX steps ran. Six link-state packet events (initial, after contact and after coast for each fixture) copied pose and COM twist exactly into both actual Newton states. All temporary worker processes exited.

'''
for c in m['cases']:
 s+=f"{c['id']}: native soft force N {c['native_contact']['force'][0]}; world reaction wrench N / N m {c['native_contact']['wrench'][0]}; hinge velocity {c['after_pulse']['joint_velocity'][0]:.12g} rad/s; joint position {c['after_pulse']['joint_position'][0]:.12g} rad; coast velocity change {c['coast_joint_velocity_change_rad_s']:.9g} rad/s.\n"
s+='\nMaximum errors across the two fixtures:\n'
for key,value in metrics.items():s+=f'  {key}: {value:.9g}\n'
s+='''
Retained gates: force 2e-5 N, projected point 1e-7 m, COM torque 2e-7 N m, effective hinge inertia 1e-8 kg m², joint position 1e-6 rad, pulse joint velocity 2e-5 rad/s, coast joint velocity change 2e-6 rad/s, particle impulse 2e-7 N s, particle position 1e-7 m, hinge-axis angular momentum 2e-8 N m s. No tolerance was relaxed. Four focused reference/guard-contract tests and nine supervisor tests passed, including rotated contact equivalence, hinge-axis angular balance and rejection of clear geometry as a penetrating contact.

'''
s+=f'''The protected worker completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. There were no memory warnings or monitor errors and no owned live processes remained. Source snapshots/hashes were saved. Original frozen production inputs and previously pinned installed dependencies remain unchanged.

Next bounded step: a repeated coupled hinge sequence with fresh collision records and natural separation, without repositioning the particle. Joint reset/replay, multi-joint dynamics, broader coordinates, contact work/energy, cutting material and the full blade collision backend remain unvalidated.
'''
(out/'newton-physx-hinge-contact-check-20261101.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(i for i in d['items'] if i['id']==15)
i['progress']='Actual Newton particle reaction drives both passive hinges correctly; joint impulse, hinge-axis angular balance and actual Newton-state echo pass. Explicit outside-particle clearing passes. Next: repeated jointed contact and natural separation; full coupling remains open.'
i['evidence']='newton-physx-hinge-contact-check-20261101.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — native particle-to-hinge contact: newton-physx-hinge-contact-check-20261101.txt\nOne actual contact exchange and deliberate clear control pass in both orientations. Next: repeated hinge contact with natural separation. Item 15 remains open.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Connect particle contact to a jointed link','Repeat jointed contact and check separation').replace('Jointed-link force input and clearing pass in two orientations. Next: drive the link with an actual Newton particle contact.','Actual Newton contact drives the hinge correctly in both orientations. Next: repeat the exchange and check natural separation.');p.write_text(s)
print(json.dumps(metrics,indent=2))
