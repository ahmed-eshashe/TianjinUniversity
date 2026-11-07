"""Save final fixed-mount evidence and update the existing progress tracker."""
from pathlib import Path
import hashlib,json,shutil
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');N=R/'runs/native/fixed_mount_20261101_06';A=R/'runs/offline/fixed_mount_scene_20261101_01'
sup=json.loads((N/'supervisor_result.json').read_text());m=json.loads((N/'fixed_mount_measurements.json').read_text());g=json.loads((N/'mounted_target_checks.json').read_text());c=json.loads((N/'collision_positive_control.json').read_text());f=json.loads((N/'target_fixture.json').read_text());plan=json.loads((A/'fixed_mount_plan.json').read_text())
assert sup['passed'] and all(m['checks'].values()) and all(g['checks'].values()) and all(f['checks'].values())
pins=json.loads((N/'input_manifest.json').read_text())['source_sha256'];assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items())
frozen=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
deps=json.loads((R/'runs/native/bent_replay_20261101_01/source_integrity.json').read_text())['sha256'];deps={p:h for p,h in deps.items() if Path(p).is_absolute() and not p.startswith(str(R))};assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in deps.items())
E=O/'fixed-mount-robot-scene-20261101-evidence';E.mkdir(exist_ok=True)
for path in N.iterdir():
 if path.is_file() and path.suffix in ['.json','.jsonl','.log','.usda']:shutil.copy2(path,E/path.name)
for path in [A/'fixed_mount_plan.json',A/'fixed_mount_scene.usda']:shutil.copy2(path,E/path.name)
for name in ['rl/tomato_fixed_mount_scene.py','rl/tomato_fixed_mount_worker.py','rl/tomato_fixed_mount_target.py','rl/tomato_robot_scene_fixture.py','rl/tomato_robot_scene_audit.py','rl/tomato_isaac_startup_guard.py','rl/tests/test_tomato_isaac_startup_guard.py']:
 target=E/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,target)
# Include exact execution dependencies and the prior audit; large original assets
# remain at their verified paths instead of duplicating the project asset tree.
for name in ['rl/tomato_native_full_model.py','rl/tomato_native_full_gather.py','rl/tomato_native_volume_steps.py','rl/tomato_native_group_cohesion.py','rl/tomato_exact_blade_coverage.py','rl/tomato_exact_blade_queries.py','rl/tomato_mesh_weighted_contact.py','scripts/reach_kinematics.py','work/exact_blade_cells.json','runs/offline/robot_scene_20261101_01/scene_audit.json','runs/offline/robot_scene_20261101_01/local_cutting_scene.usda']:
 target=E/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,target)
summary=dict(date='2026-11-01',robot_scene_section='complete within bounded fixed-mount diagnostic scope',knife_connection='User-selected ideal fixed mount',
 source_unchanged=True,pinned_dependency_files_unchanged=len(deps),guard_tests=13,final_native_run=str(N),
 physx_steps=sup['worker']['controlled_steps'],newton_steps=sup['worker']['newton_steps'],elapsed_wall_s=sup['elapsed_wall_s'],
 minimum_target_separation_mm=min(e['minimum_target_aabb_separation_m'] for e in m['episodes'])*1000,
 minimum_blade_board_clearance_mm=min(e['minimum_blade_board_clearance_m'] for e in m['episodes'])*1000,
 maximum_mount_position_error_m=max(e['maximum_mount_position_error_m'] for e in m['episodes']),
 maximum_joint_speed_rad_s=max(e['maximum_joint_speed_rad_s'] for e in m['episodes']),
 maximum_joint_tracking_error_rad=max(e['maximum_right_tracking_error_rad'] for e in m['episodes']),
 replay_joint_error_rad=m['replay_joint_error_rad'],replay_tool_pose_error=m['replay_tool_pose_error'],
 collision_positive_control_n=c['overlap_force_n'],collision_clear_control_n=c['reset_clear_forces_n'],
 dirty_blade_contacts=g['dirty_generated_contacts'],cleared_blade_contacts=g['cleared_generated_contacts'],
 gravity_fixture_duration_s=g['simulated_duration_s'],gravity_weight_n=g['load_weight_n'],
 limitations=['Ideal massless, rigid bracket with 150 mm palm-to-handle vertical offset; no physical finger grip or hardware mount validation.',
 'Robot dry motion spans two 8.02 s cycles; the target is visual/rest-state geometry during that dry motion. Newton fixture gravity is checked separately for 5 ms per replay.',
 'No settled/long-term target support, Newton board contact, cutting loads, post-cut reset, fracture or robot cutting force feedback is qualified by this run.',
 'Measured 6.01 mm blade/board clearance reflects gravity/tracking deflection; it is lower than the planned 12 mm clearance.',
 'Blade/robot forbidden contact gate is 0.1 N; actual reported peak during the final dry routes is zero.',
 'Generated blade contacts are deliberately created by shifting target positions and reset without integrating cutting forces; this qualifies contact-stream reset, not loaded cutting reset.',
 'Experimental material validation remains pending at user request.'],next_step=23)
(O/'fixed-mount-robot-scene-20261101.json').write_text(json.dumps(summary,indent=2)+'\n')
text=f"""FIXED-MOUNT ROBOT & SCENE CHECKS — 1 November 2026

Result: checklist 19–22 complete within the bounded diagnostic scope below. First controlled cutting has not begun.

The original knife is referenced into the robot articulation and connected to the right hand base by an ideal fixed joint. The source knife instance is deactivated only in the derived scene, leaving one active knife. There are still 36 actuator joints; the fixed connection adds no control degree of freedom. Only the directly connected hand-base pair is excluded by this mount; the other source collision settings and robot self-collision remain enabled.

The mount is an ideal, massless rigid bracket with a 150 mm vertical palm-to-handle offset. Knife mass/inertia remain the existing provisional 0.25 kg configuration. This is neither a finger grasp nor a designed hardware bracket.

FINAL NATIVE RESULT
- 3,851 PhysX steps, 30 Newton steps; two 8.02 s commanded dry-motion cycles plus collision controls.
- Dry route is laterally offset 90 mm from the intended cutting plane. Minimum measured blade/target AABB separation: {summary['minimum_target_separation_mm']:.3f} mm.
- Minimum measured blade/board clearance: {summary['minimum_blade_board_clearance_mm']:.3f} mm. The plan's 12 mm clearance reduces under gravity/tracking deflection.
- Mount relative position error: at most {summary['maximum_mount_position_error_m']:.3g} m. Maximum joint speed: {summary['maximum_joint_speed_rad_s']:.4f} rad/s. Right-arm tracking error: at most {summary['maximum_joint_tracking_error_rad']:.5f} rad.
- Native monitored forbidden rigid contact forces during the dry routes: zero. Explicit gate: 0.1 N.
- Contact reporting is explicitly enabled after simulator initialization. A separate probe/floor impact measures {c['overlap_force_n']:.6f} N, then 0 N on both clearing steps after reset. Static floor filtering uses its actual collider path.
- Robot reset clears joint velocities and both deliberately contaminated wrench queues. Joint and tool-pose replay differences are exactly zero.
- Authored 25-node target fixture holds a 0.001 N tensile probe, with exact replay. A separate 5 ms, 9.81 m/s² gravity probe applies {g['load_weight_n']:.4f} N total weight, holds the constrained nodes and leaves the target above the board. Gravity replay is exact.
- A deliberate shifted-target reset challenge generates {g['dirty_generated_contacts']:,} blade contacts; restoring both target state buffers, forces and material/eligibility history clears the generated contact count to zero.
- Final guarded process exits normally in {sup['elapsed_wall_s']:.2f} s, with no owned processes left and no memory warning.
- All frozen original input/source hashes and {len(deps)} pinned installed-dependency hashes remain unchanged. 13 focused guard tests pass.

SCOPE LIMITS
The dry motion uses rest-state target geometry; Newton gravity support is checked separately for only 5 ms. Long-term settling/support, board contact in Newton, loaded cutting/force feedback, fracture and post-cut reset are later tests. The deliberate contact-reset challenge does not integrate contact forces. No training or physical grasp is claimed. Material calibration and independent experimental validation remain pending.

Historical diagnostics 01/02 predate the completed collision positive control and are not final qualification. 03 stopped on a settings-reader API mismatch. 04/05 exposed control filtering/impulse issues. All remain preserved; only run 06 is final.

Reproduce with the existing guarded fixed_mount mode using a fresh output directory. Fixed scene and plan: {A}
Final evidence: {E}
"""
(O/'fixed-mount-robot-scene-20261101.txt').write_text(text)
p=O/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text())
changes={19:dict(status='done',progress='The original knife is mounted in a separate robot scene using SI units. The ideal fixed joint preserves the checked frames and adds no actuator joint.',checks=['PASS — actual 36-joint robot; one active original knife','SCOPE — ideal massless mount; no finger-grasp claim']),
20:dict(status='done',progress='Fixed support and collision setup pass bounded fixture checks. Support holds a 5 ms gravity probe; long-term settling and cutting loads are later checks.',checks=['PASS — 25 support nodes; slice nodes remain free','PASS — collision monitor detects a deliberate impact and clearing']),
21:dict(status='done',progress='Two 8-second offset dry cycles pass approach, stroke and retreat under robot gravity. Minimum blade/target gap is 34.4 mm; blade/board clearance is 6.01 mm.',checks=['PASS — rigid mount, bounded speed and tracking','PASS — no monitored forbidden contact forces; exact replay']),
22:dict(status='done',progress='Robot rigid reset and target material reset/replay pass. A deliberate generated-contact challenge clears 11,439 blade contacts to zero. Loaded post-cut reset remains untested.',checks=['PASS — poses, velocities and both wrench queues','PASS — both target buffers, history and generated contact clearing'])}
for i in d['items']:
 if i['id'] in changes:i.update(changes[i['id']]);i['evidence']='fixed-mount-robot-scene-20261101.txt'
 if i['id']==23:i['progress']='Next: implement and check robot-mounted blade force feedback, then run a slow, bounded first cut with force and work logging.'
d['updated']='2026-11-01';d['current_next_step']=23;d['robot_knife_connection_user_choice']='Fixed mount — user selected 1 November 2026';d['counts']={s:sum(i['status']==s for i in d['items']) for s in ['done','open','todo']}
p.write_text(json.dumps(d,indent=2)+'\n');(O/'isaac-sim-progress-checklist.txt').write_text('Updated 1 November 2026. Completed checks apply to their stated bounded fixtures.\n\n'+''.join(f"{i['id']:02} [{i['status'].upper()}] {i['title']}\n"+i.get('progress','')+'\n' for i in d['items']))
print(json.dumps(summary,indent=2));print(d['counts'])
