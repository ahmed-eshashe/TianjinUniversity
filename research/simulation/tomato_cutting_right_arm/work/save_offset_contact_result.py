from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/offset_contact_20261031_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'offset_contact_measurements.json').read_text());assert sup['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
previous=json.loads((root/'runs/native/contact_feedback_20261031_02/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in previous.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_offset_contact_worker.py','tomato_offset_contact_reference.py','tomato_contact_feedback_worker.py','tomato_physx_proxy_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_offset_contact_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,installed_dependencies_unchanged=True),indent=2)+'\n')
metrics={}
for section in ('wrench_check','pulse_check','motion_checks'):
 for name,value in m['cases'][0][section].items():
  if isinstance(value,(int,float)) and 'error' in name:
   metrics[name]=max(c[section][name] for c in m['cases'])
report=dict(supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=14,
 original_frozen_sources_unchanged=True,installed_dependencies_unchanged=True)
(out/'newton-physx-offset-contact-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX off-centre contact check — 31 October 2026

PASS for two one-interval off-centre analytic contact fixtures. Full checklist item 15 remains in progress; this is not yet repeated rotating-contact or robot coupling qualification.

Fixture 1 used an identity-oriented box with zero COM offset. Fixture 2 rotated the box 90 degrees about Y and set its local COM to (0.002, -0.001, 0.0005) m. Both particles began at body-local (0.004, 0.003, 0.001) m; the box top was at local z=0.002 m. Thus the generated contact was away from the COM and produced a nonzero reaction torque. The rotated fixture transformed the normal from local +Z to world +X. Newton and CPU PhysX used matching read-back local COM offsets and xyzw pose/COM-velocity conventions.

Two Newton steps and one shared CPU PhysX step were executed at dt=1/1200 s. Newton solved each 0.01 kg particle against a frozen, kinematic box proxy for 16 iterations. PhysX exclusively owned each 0.02 kg rigid body. Bodies were initially at rest with gravity, damping, friction and PhysX collisions disabled. The synthetic isotropic inertia was explicitly set/read back to 0.0001 kg m²; it is a diagnostic choice, not the physical inertia of the box geometry. Contact stiffness was the native fixed cache 1750 N/m; radius and margin were zero. The proxy COM was locked against shape mass recomputation.

Each contact was collision-generated, not manually inserted. Its final native force and contact point were collected through the native contact helper using the actual solver cache and previous-particle state. The reaction torque was computed in world coordinates about the transformed COM. The wrench was delivered once with positions=None and is_global=True, avoiding a second positional moment. Both Newton body states stayed frozen during the soft solve and then copied the resulting PhysX pose/twist back exactly.

Independent host plane-contact arithmetic checked force, projected point, and lever-arm cross reaction about the COM. Checks also compared particle motion, PhysX COM linear/angular impulse, COM position, and world rotation increment. The rotation reference uses the declared 16 TGS force substeps (17/32 of dt times final angular velocity for initially stationary isotropic bodies). Total angular momentum includes particle orbital, rigid COM orbital and rigid spin contributions about the initial COM. Body translational/rotational work is checked against kinetic energy with TGS numerical loss; this is not a full rotating-contact potential-energy qualification.

'''
for c in m['cases']:
 s+=f"{c['id']}:\n  soft force N = {c['native_contact']['force'][0]}\n  world COM reaction wrench N / N m = {c['native_contact']['wrench'][0]}\n  final world COM velocity m/s and angular velocity rad/s = {c['final_physx']['velocity']}\n  world rotation increment rad = {c['motion_checks']['world_rotation_increment_rad']}\n\n"
s+='Maximum errors over both fixtures:\n'
for key,value in metrics.items():s+=f'  {key}: {value:.9g}\n'
s+=f'''
Gates: force/reaction 2e-5 N; contact point and particle/COM position 1e-7 m; torque 2e-7 N m; linear velocity 2e-5 m/s; angular velocity 2e-6 rad/s; linear momentum/impulse 2e-7 kg m/s; angular momentum 2e-8 kg m²/s; rotation increment 1e-6 rad; body work identity 2e-8 J. No tolerances were relaxed. Five focused tests plus nine existing supervisor tests passed; the tests reject torque calculated about the link origin instead of the shifted COM.

The protected worker completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. It exited normally, with no owned live processes, no memory warning and no monitor errors. Original frozen project inputs and pinned installed dependencies remain unchanged. Snapshots/hashes and full measurements are saved.

Next bounded step: repeat contact exchange while the body rotates, checking fresh normals, updated COM/lever arms and angular impulse accumulation, including contact clearing. Anisotropic inertia, articulated links, reset/history restoration, long-duration stability and the real blade's full-surface contact path remain unvalidated. No robot or blade was loaded.
'''
(out/'newton-physx-offset-contact-check-20261031.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['progress']='Repeated head-on exchange/clearing passes. Off-centre contact force and turning impulse pass for identity and 90° rotated/offset-COM bodies, including linear/angular momentum. Next: repeated rotating contact. Full coupling validation remains open.'
i['evidence']='newton-physx-offset-contact-check-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nOff-centre reaction: newton-physx-offset-contact-check-20261031.txt\nItem 15: off-centre force/torque passes in rotated and shifted-COM fixtures. Next: repeated rotating contact.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check off-centre contact forces','Repeat contact while turning').replace('16 contact exchanges pass; forces clear when contact ends. Next: verify off-centre forces, torque and rotated body frames.','Off-centre forces and turning effects pass, including a rotated body and shifted centre of mass. Next: repeat contact while the body turns.');p.write_text(s)
print(json.dumps(metrics,indent=2))
