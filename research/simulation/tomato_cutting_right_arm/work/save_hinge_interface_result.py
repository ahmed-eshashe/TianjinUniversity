from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/hinge_interface_20261101_03';sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'hinge_interface_measurements.json').read_text());assert sup['passed']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/anisotropic_sequence_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_hinge_interface_worker.py','tomato_hinge_reference.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_hinge_reference.py')]+[Path(n) for n in installed]
files.extend([Path('/home/omen/IsaacLab/source/isaaclab_physx/isaaclab_physx/assets/articulation')/n for n in ('articulation.py','articulation_data.py')]);files.append(Path('/home/omen/IsaacLab/source/isaaclab/isaaclab/utils/wrench_composer.py'))
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={k:max(c['pulse_check'][k] for c in m['cases']) for k in m['cases'][0]['pulse_check']}
metrics['coast_joint_velocity_change_rad_s']=max(c['coast_joint_velocity_change_rad_s'] for c in m['cases'])
report=dict(passed=True,supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=13,
 preflight_runs_preserved=[str(root/f'runs/native/hinge_interface_20261101_0{i}') for i in (1,2)],
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/'physx-jointed-link-interface-check-20261101.json').write_text(json.dumps(report,indent=2)+'\n')
s='''CPU PhysX jointed-link force interface — 1 November 2026

PASS for a prescribed world-wrench pulse and zero-input coast on two isolated passive hinges. This is an articulation interface check; no Newton contact force was connected and no Newton solver step ran. Checklist item 15 remains open.

The installed articulation writer accepts world wrenches through its instantaneous composer, composes them into each link's body frame, handles body ordering when configured, and calls the backend force/torque API with positions=None and is_global=False. The input side of this test explicitly uses is_global=True and positions=None, so the composer performs the single required frame conversion. Only the selected moving link receives a wrench; the fixed base does not.

The synthetic USD scenes were authored locally without remote assets. Each has a fixed base, one unbounded Z-axis revolute joint and one 0.02 kg moving link with its COM 0.01 m from the hinge. COM inertia about Z was explicitly authored as 0.0001 kg m². Joint stiffness, damping and static/dynamic/viscous friction were zero; actuators were intentionally absent. Gravity and collisions were disabled. Visual scale was put on child geometry so the rigid-body and joint local frames retained unit scale. Fixture 1 used identity orientation; fixture 2 rotated the assembly 90 degrees about Z. Both are near the origin.

A world force of (0,3,0) N was applied at the first link's COM, plus world COM torque (0,0,0.0012) N m. The rotated fixture used world force (-3,0,0) N and the same world COM torque. Both therefore produce the same positive hinge effort: r cross F contributes 0.03 N m and the COM torque adds 0.0012 N m. The effective joint inertia is I_COM + m*r² = 0.000102 kg m². The installed articulation mass matrix independently matched that value. At dt=1/2400 s the expected joint velocity increment is approximately 0.12745098 rad/s. Position is compared against the 16-substep TGS schedule, dt times final velocity times 17/32. This fixture contains fixed-base constraint reactions, so the free-body linear-momentum identity is not an appropriate acceptance check.

Exactly two shared PhysX steps ran: one pulse and one coast. No new wrench was submitted for the coast step. Both joint velocities stayed within the 2e-6 rad/s clearing gate. Four measured moving-link pose/world-COM-velocity packets copied exactly from staged CPU arrays to CUDA Warp buffers. This is a packet/format echo, not an actual Newton State or articulated two-way coupling proof.

'''
for c in m['cases']:
 s+=f"{c['id']}: joint velocity after pulse {c['after_pulse']['joint_velocity'][0]:.12g} rad/s; joint position {c['after_pulse']['joint_position'][0]:.12g} rad; effective inertia {c['mass_matrix_kg_m2']:.12g} kg m²; coast velocity change {c['coast_joint_velocity_change_rad_s']:.9g} rad/s.\n"
s+='\nMaximum errors:\n'
for k,v in metrics.items():s+=f'  {k}: {v:.9g}\n'
s+='''
Gates: effective inertia 1e-8 kg m²; pulse joint position 1e-6 rad; pulse joint velocity 2e-5 rad/s; coast velocity change 2e-6 rad/s. No tolerance was relaxed. Four focused reference/guard-contract tests and nine supervisor tests passed, including a negative check that omits the COM force's hinge moment.

Two preliminary launches stopped before any simulation step. The first did not recognise the intended fixed-base topology when articulation-root metadata was on the base body; placing it on the world-anchor fixed joint produced the intended fixed-base/two-body/one-joint topology. The second rejected scalar friction values in the installed kernel despite the Python signature allowing floats; explicit (1,1) float32 tensors were accepted. These fixture/API corrections are confined to the diagnostic worker. The failed launch logs, hashes and authored USD scenes are preserved. Installed libraries were not edited.

'''
s+=f'''The passing protected run finished in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. There were no resource warnings or monitor errors and no owned live processes remained. Source snapshots/hashes include articulation state, wrench-composer and writer interfaces. Original frozen production inputs and previously pinned installed dependencies remain unchanged.

Next bounded step: generate one actual Newton particle contact against the moving hinge link, send the collected reaction to that link, and check generalized hinge impulse with fixed-base constraints accounted for. Repeated jointed contact, multi-joint robots, joint reset/history, contact work/energy, cutting material and the real blade collision backend remain unvalidated. No robot or real blade was loaded.
'''
(out/'physx-jointed-link-interface-check-20261101.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(i for i in d['items'] if i['id']==15)
i['progress']='Prescribed link wrench passes on identity and yaw-rotated passive hinges: effective joint inertia, joint impulse, packet echo and zero-input coast. Next: actual Newton particle-contact reaction on the hinge. Articulated two-way coupling remains open.'
i['evidence']='physx-jointed-link-interface-check-20261101.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — jointed-link interface: physx-jointed-link-interface-check-20261101.txt\nPrescribed pulse/coast passes on two passive hinges. Next: connect actual Newton contact to the moving link. Item 15 remains open.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check force transfer through a joint','Connect particle contact to a jointed link').replace('Repeated contact with unequal turning resistance passes for both test bodies. Next: check force transfer on a simple jointed link.','Jointed-link force input and clearing pass in two orientations. Next: drive the link with an actual Newton particle contact.');p.write_text(s)
print(json.dumps(metrics,indent=2))
