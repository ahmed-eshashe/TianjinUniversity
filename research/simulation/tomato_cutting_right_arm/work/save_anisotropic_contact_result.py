from pathlib import Path
import json,hashlib,shutil,math
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/anisotropic_contact_20261031_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'anisotropic_contact_measurements.json').read_text());assert sup['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
previous=json.loads((root/'runs/native/reset_replay_20261031_01/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in previous.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_anisotropic_contact_worker.py','tomato_anisotropic_reference.py','tomato_contact_feedback_worker.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_anisotropic_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={}
for section in ('wrench_check','pulse_check','motion_checks'):
 for name,value in m['cases'][0][section].items():
  if isinstance(value,(int,float)) and 'error' in name:metrics[name]=max(c[section][name] for c in m['cases'])
report=dict(supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=14,
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/'newton-physx-anisotropic-contact-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX unequal-inertia contact check — 31 October 2026

PASS for two initially stationary, one-interval analytic contact fixtures with unequal principal inertia. Checklist item 15 remains in progress. This checks initial response and coordinate mapping, not general anisotropic spinning dynamics.

Both 0.02 kg CPU PhysX bodies used explicitly specified/read-back principal moments (0.0001, 0.0002, 0.00025) kg m², which satisfy the inertia triangle inequality. These are synthetic diagnostic inertias, not the inertia inferred from the displayed box geometry. Fixture 1 used identity orientation and zero local COM offset. Fixture 2 used a 60-degree rotation about the normalized (1,2,3) axis, with local COM (0.002, -0.001, 0.0005) m. This oblique orientation produces non-diagonal world inertia; treating body principal axes as fixed world axes gives a distinguishably wrong prediction. Both started with zero velocity. PhysX gyroscopic forces were explicitly enabled and read back, but their nonzero-spin behavior was not exercised by this initially resting test.

A 0.01 kg CUDA Newton particle began at body-local (0.004, 0.003, 0.001) m. The analytic box top was at local z=0.002 m. The native collision pipeline generated one off-centre contact per fixture. The frozen Newton proxy carried the same body-local COM and inertia, locked against shape recomputation; PhysX exclusively owned rigid motion. Native mixed contact stiffness was 1750 N/m, damping/friction/radius/margin zero. Gravity and PhysX collisions were disabled. Newton used 16 soft iterations; CPU PhysX used TGS with 16 force substeps and zero velocity iterations. Exactly two Newton steps and one shared PhysX step ran at dt=1/1200 s.

Actual native contact force and projected point were checked against independent plane-contact arithmetic. The body reaction was the opposite force with the world torque about the transformed COM. The wrench was delivered once with positions=None and is_global=True. Newton proxy poses/twists stayed frozen during the particle solve, and both Newton body states copied the resulting PhysX pose/twist back exactly.

The host reference transforms a world torque into body principal axes, divides by each principal moment and transforms back. Expected initial angular impulse is dt * R * diag(1/I) * R^T * torque. This is an initial-tensor, small-rotation approximation: the test requires rotation below 0.001 rad, and the existing angular tolerance includes tensor evolution over that interval. Final spin angular momentum uses the measured final orientation and R_final * diag(I) * R_final^T * omega_final. Particle/rigid linear impulses and total orbital-plus-spin angular momentum are also checked. Rotation and body work use the same small-interval approximation; this is not a full energy or Euler-equation qualification for arbitrary spinning bodies.

'''
for c in m['cases']:
 s+=f"{c['id']}:\n  world reaction torque N m = {c['native_contact']['wrench'][0][3:]}\n  predicted angular velocity rad/s = {c['pulse_check']['initial_tensor_expected_angular_velocity']}\n  measured angular velocity rad/s = {c['final_physx']['velocity'][3:]}\n  rotation magnitude rad = {math.hypot(*c['motion_checks']['world_rotation_increment_rad']):.9g}\n"
 if 'wrong_world_axes_velocity_difference_rad_s' in c:s+=f"  error induced by treating principal axes as world axes rad/s = {c['wrong_world_axes_velocity_difference_rad_s']:.9g}\n"
 s+='\n'
s+='Maximum errors over both fixtures:\n'
for key,value in metrics.items():s+=f'  {key}: {value:.9g}\n'
s+=f'''
No tolerances were relaxed. Force/reaction gate 2e-5 N; point and particle/COM position 1e-7 m; torque 2e-7 N m; linear velocity 2e-5 m/s; angular velocity 2e-6 rad/s; linear momentum/impulse 2e-7 kg m/s; angular momentum 2e-8 kg m²/s; rotation 1e-6 rad; small-interval body work residual 2e-8 J. The oblique fixture also had to differ from the wrong world-axis angular prediction by more than 0.001 rad/s. Five focused reference/guard-contract tests plus nine supervisor tests passed, including rejection of the wrong inertia frame and invalid principal moments.

The protected run completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No memory warning or resource-monitor error occurred; no owned live processes remained. Source snapshots/hashes were saved; original frozen project inputs and previously pinned installed dependencies are unchanged.

Next bounded step: a short unequal-inertia spin/coast check with nonzero initial angular velocity and gyroscopic forces, before qualifying sustained unequal-inertia contact. Articulated robot links, general rotating-contact work, time-step/long-run stability, material cutting and the real blade collision-generated full-surface backend remain unvalidated. No robot or blade was loaded.
'''
(out/'newton-physx-anisotropic-contact-check-20261031.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['progress']='Turning exchange and reset/replay pass. One-step unequal-inertia contact passes for identity and oblique/offset-COM bodies; world inertia mapping and initial spin impulse checked. Next: nonzero-spin gyroscopic coast. Full coupling validation remains open.'
i['evidence']='newton-physx-anisotropic-contact-check-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nUnequal-inertia initial contact response: newton-physx-anisotropic-contact-check-20261031.txt\nItem 15 remains in progress. Next: nonzero-spin gyroscopic coast check.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check turning resistance by axis','Check spinning and coasting').replace('Reset and replay match exactly, including reset during contact. Next: check a body that resists turning differently around each axis.','Unequal turning resistance passes the initial contact check. Next: check how the body spins and coasts with no applied force.');p.write_text(s)
print(json.dumps(metrics,indent=2))
