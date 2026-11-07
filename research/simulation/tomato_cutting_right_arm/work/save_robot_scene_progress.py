from pathlib import Path
import hashlib,json,shutil
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');N=R/'runs/native/robot_scene_frames_20261101_03';A=R/'runs/offline/robot_scene_20261101_01'
sup=json.loads((N/'supervisor_result.json').read_text());audit=json.loads((A/'scene_audit.json').read_text());frames=json.loads((N/'robot_scene_frames.json').read_text());fixture=json.loads((N/'target_fixture.json').read_text());pins=json.loads((N/'input_manifest.json').read_text())['source_sha256']
assert sup['passed'] and audit['passed'] and all(frames['checks'].values()) and all(fixture['checks'].values())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items())
frozen=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
evidence=O/'robot-scene-progress-20261101-evidence';evidence.mkdir(exist_ok=True)
for p in [N/'supervisor_result.json',N/'worker_result.json',N/'input_manifest.json',N/'robot_scene_frames.json',N/'target_fixture.json',N/'resources.jsonl',A/'scene_audit.json',A/'local_cutting_scene.usda']:
 shutil.copy2(p,evidence/p.name)
for p in ['rl/tomato_robot_scene_audit.py','rl/tomato_robot_scene_frames_worker.py','rl/tomato_robot_scene_fixture.py','rl/tomato_isaac_startup_guard.py','scripts/reach_kinematics.py','rl/tests/test_tomato_isaac_startup_guard.py']:
 dst=evidence/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/p,dst)
summary=dict(date='2026-11-01',scope='Robot and scene section in progress; not complete',
 robot_joints=frames['num_joints'],maximum_frame_position_error_m=max(r['position_error_m'] for r in frames['errors']),maximum_frame_rotation_error_rad=max(r['rotation_error_rad'] for r in frames['errors']),
 fixed_fixture_nodes=len(fixture['fixture_node_ids']),fixture_checks=fixture['checks'],
 maximum_fixture_displacement_m=max(r['fixed_error_m'] for t in fixture['sequences'] for r in t),
 free_response_maximum_displacement_m=max(r['maximum_displacement_m'] for r in fixture['sequences'][0]),
 source_preservation=True,native_run=str(N),elapsed_wall_s=sup['elapsed_wall_s'],
 pending=['Knife mounting choice: fixed tool mount or physical finger grasp. Neither was newly introduced.',
 'Combined blade/robot/target collision checks, contact-free approach/cutting/retreat and assembled-scene contact reset.',
 'Fixed fixture is only probed at 0.001 N tension with zero gravity; realistic support/cutting loads remain untested.'],
 experimental_validation='Pending at user request; unchanged')
(O/'robot-scene-progress-20261101.json').write_text(json.dumps(summary,indent=2)+'\n')
text=f"""ROBOT & SCENE — 1 November 2026
Section in progress; not yet complete.

PASSED
- Actual 36-joint robot loads in a separate local-origin scene with the board and original knife.
- Units are metres, Z is up, and relative source frames survive rebasing exactly to numerical precision.
- Runtime right-arm frame error: {summary['maximum_frame_position_error_m']:.3g} m and {summary['maximum_frame_rotation_error_rad']:.3g} rad.
- Original blade triangle topology and float32 USD vertex representation match. The saved decimal export differs from USD by at most {audit['blade_float64_export_to_usd_max_error_m']:.3g} m; this is disclosed, not claimed bit-identical float64 geometry.
- Robot and knife rigid reset restore positions, zero velocities and clear both dirty wrench queues.
- The authored 25 bulk-side support nodes stay fixed; all slice nodes remain free under a 0.001 N tensile pulse. Zero gravity is used in this fixture check.
- Both target state buffers, force accumulators, eligibility and material history clear after deliberate contamination. Three-step replay is exact.
- Final protected run completes 2 PhysX and 6 Newton steps in {sup['elapsed_wall_s']:.2f} s. Normal exit, no surviving owned process, no memory warnings.
- Frozen original production inputs and source assets remain unchanged.

REMAINING
- Choose fixed knife mount versus physical finger grasp before attaching or driving the tool.
- Verify the assembled robot/blade/target collision path and run approach, cutting and retreat without target contact.
- Recheck contact clearing and full reset after the tool connection is implemented.
- Test fixed support under realistic gravity/cutting loads. The 0.001 N pulse is a narrow numerical test.

No cutting, training, left-hand holding, or hardware/material calibration is claimed. Experimental validation remains pending at the user's request.

Evidence: {evidence}
"""
(O/'robot-scene-progress-20261101.txt').write_text(text)
p=O/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text())
changes={19:dict(status='done',progress='The actual robot, board and original blade pass SI units, relative placement and runtime right-arm frame checks in a separate local-origin scene.',checks=['PASS — actual 36-joint robot and frame comparisons','PASS — original USD blade representation and source preservation']),
20:dict(status='open',progress='The authored 25-node fixed support passes a small tensile pulse. Knife connection and combined collision checks are still needed.',checks=['PASS — support nodes remain fixed; slice nodes remain free','PENDING — assembled tool collisions and realistic support loads']),
21:dict(status='open',progress='Choose a fixed knife mount or physical finger grasp before connecting the tool and testing approach, cutting and retreat.',checks=['PENDING — knife holding method and contact-free robot/tool motion']),
22:dict(status='open',progress='Robot/knife rigid reset and dirty material reset/replay pass. Contact clearing must be checked again after the tool is connected.',checks=['PASS — poses, velocities, wrench queues and material replay','PENDING — complete assembled-scene contact reset'])}
for i in d['items']:
 if i['id'] in changes:i.update(changes[i['id']]);i['evidence']='robot-scene-progress-20261101.txt'
d['updated']='2026-11-01';d['current_next_step']=21;d['counts']={s:sum(i['status']==s for i in d['items']) for s in ['done','open','todo']};d['robot_knife_connection_user_choice']='Awaiting fixed mount or physical finger grasp choice'
p.write_text(json.dumps(d,indent=2)+'\n');(O/'isaac-sim-progress-checklist.txt').write_text('Updated 1 November 2026. Completed checks apply to stated fixtures.\n\n'+''.join(f"{i['id']:02} [{i['status'].upper()}] {i['title']}\n"+i.get('progress','')+'\n' for i in d['items']))
print(json.dumps(summary,indent=2));print(d['counts'])
