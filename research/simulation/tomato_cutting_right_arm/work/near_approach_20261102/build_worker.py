from pathlib import Path
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');s=(R/'rl/tomato_dry_tracking_worker_v02.py').read_text()
s=s.replace('Focused dry controller correction: interpolated commands, desired velocity, arm gravity feedforward.','Reachable near-target dry approach, stop above target, withdraw and return. No contact.')
s=s.replace("ROOT/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json'", "ROOT/'runs/offline/near_approach_plan_20261102_02/near_approach_plan.json'",1)
s=s.replace("prior=ROOT/'runs/native/fixed_mount_20261101_06/fixed_mount_measurements.json'", "prior=ROOT/'runs/native/dry_tracking_corrected_20261102_01/measurements.json'",1)
s=s.replace("  snapshot_path=", "  preflight=ROOT/'runs/offline/near_approach_plan_20261102_02/measurements.json'\n  if not json.loads(preflight.read_text())['host_preflight_passed']:raise ValueError('Near approach host preflight missing')\n  snapshot_path=",1)
s=s.replace('plan_path,Path(plan[\'scene\']),prior,snapshot_path,Path(__file__)',"plan_path,Path(plan['scene']),prior,preflight,snapshot_path,Path(__file__)",1)
s=s.replace("original_substeps_per_sample=4,", "clock_reference='Same1/240s physics and8substeps/sample as corrected dry controller',",1)
s=s.replace("scope='GUI rendered dry motion. Original 90mm-offset route, half speed, scripted joint targets. No contact/deformation/fracture/video/training. Initial-state writes only before executed route.'", "scope='GUI rendered closer dry approach,20mm planned stop above union of reference and prepared tomato bounds, withdrawal and home return. No contact/target dynamics/fracture/video/training. Initialization only before executed route.'",1)
s=s.replace("target=np.array([n['position_m']for n in target_json['nodes']])+[0.,0.,.002]", "target=np.array(plan['clearance_target_world_m']);target_lo=target.min(0);target_hi=target.max(0)",1)
s=s.replace('target.min(0)','target_lo').replace('target.max(0)','target_hi')
# Fix cached-bounds initialization after the global replacement.
s=s.replace('target_lo=target_lo;target_hi=target_hi','target_lo=target.min(0);target_hi=target.max(0)',1)
s=s.replace('original_route_half_speed=True','declared_near_approach_route=True',1)
s=s.replace('right_arm_moves=bool(np.all(right_ranges>.01))', 'right_arm_moves=bool(np.max(right_ranges)>.05)',1)
old="stroke_executed=max(x['tool_pose'][2]for x in rows)-min(x['tool_pose'][2]for x in rows)>.13"
new="near_stop_reached=bool(np.linalg.norm(actual_tool[240*8+7][:3,3]-command_tool[240*8+7][:3,3])<=.001),near_stop_above_target=bool(rows[240*8+7]['blade_board_height_m']-target_hi[2]>=.015)"
assert old in s;s=s.replace(old,new,1)
s=s.replace('minimum_target_aabb_gap_m=min',"near_stop_tool_pose=rows[240*8+7]['tool_pose'],near_stop_vertical_gap_m=rows[240*8+7]['blade_board_height_m']-target_hi[2],minimum_target_aabb_gap_m=min",1)
s=s.replace('dry_tracking_corrected_passed=passed','near_approach_passed=passed',1)
s=s.replace("scope='One slow scripted dry route; stationary visual tomato; no Newton target stepping/contact/cutting/training.","scope='One closer scripted dry approach with static reference/prepared clearance envelope; stationary visual tomato; no Newton target stepping/contact/cutting/training.",1)
(R/'rl/tomato_near_approach_worker.py').write_text(s)
