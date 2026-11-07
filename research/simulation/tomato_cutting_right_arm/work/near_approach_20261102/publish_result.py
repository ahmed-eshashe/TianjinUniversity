from pathlib import Path
import json,shutil,hashlib
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');W=R/'work/near_approach_20261102';O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=R/'runs/native/near_approach_20261102_01';plan=R/'runs/offline/near_approach_plan_20261102_02'
m=json.loads((run/'measurements.json').read_text());a=json.loads((W/'independent_readback01/measurements.json').read_text());s=json.loads((run/'supervisor_result.json').read_text());h=json.loads((plan/'measurements.json').read_text());assert a['passed']and s['passed']and not s['remaining_live_group_members']and all(m['checks'].values())and h['host_preflight_passed']
report=f'''NEAR-TARGET DRY APPROACH — 2 November 2026

VERDICT: PASS within this nearer, noncontact approach scope. No contact or cut attempted.

Executed in visible Isaac Sim: reposition from the original home to a reachable high pose aligned with the existing host candidate's prepared-plane orientation; lower to a planned20mm gap above the highest saved tomato-envelope point; withdraw; return to original home; settle. The corrected controller (per-step interpolated position, consistent velocity target, bounded native arm gravity feedforward) and existing gains/physical parameters are unchanged.

This is a NEW route, not a rerun of the original90mm-offset stroke. It uses481 samples,8physics substeps per sample,dt1/240s:16.033seconds plus1second settling. Its purpose is to verify reach and tracking above the target, not exercise the old130mm stroke-amplitude check. Near-stop reach and explicit positive vertical clearance replace that inapplicable route-specific amplitude criterion; all original tracking,15mm target-separation,4mm board, mount, speed, arm-limit and monitored-contact limits are retained. The predeclared1mm peak/0.25mm settled tracking engineering targets also remain unchanged.

Planning evidence and failure preservation
The first host-only plan was rejected at an unreachable high repositioning pose, before any native launch. Version02 changes that high pose from80mm to40mm above the target envelope, retains the20mm stop and all IK/clearance requirements, and passes3848 commanded-interpolation-state checks. Its maximum IK position error is {h['maximum_ik_position_error_m']:.9g}m and orientation error {h['maximum_ik_orientation_error_rad']:.9g}rad. The failed01 report/source remains preserved. Only the passed02 route was executed natively; there was no controller or solver sweep.

The conservative clearance envelope is the union of original reference tomato nodes at the scene offset and the saved supported equilibrium nodes. Neither target is physically stepped in this test. The displayed tomato remains the original stationary scene visual. The planning orientation comes from the previous host candidate and does not grant that candidate contact qualification.

Measured results (independent raw readback PASS)
Near-stop blade minimum-z minus target envelope maximum-z: {m['near_stop_vertical_gap_m']*1000:.6f}mm.
Minimum blade/target AABB axis separation across all recorded route/settling steps: {m['minimum_target_aabb_gap_m']*1000:.6f}mm >15mm.
Maximum tool-position tracking error: {m['maximum_tool_tracking_position_m']*1000:.6f}mm <1mm engineering target.
Settled tool-position tracking error: {m['final_tool_tracking_position_m']*1000:.6f}mm <0.25mm engineering target.
Maximum tool orientation tracking error: {m['maximum_tool_tracking_angle_rad']:.9g}rad <0.002rad.
Maximum right joint tracking error: {m['maximum_right_tracking_rad']:.9g}rad <original0.03rad.
Maximum left arm hold deviation: {m['maximum_left_arm_tracking_rad']:.9g}rad <0.002rad.
Maximum joint speed: {m['maximum_joint_speed_rad_s']:.9g}rad/s <original3rad/s.
Final joint speed: {m['final_joint_speed_rad_s']:.9g}rad/s <0.002rad/s settling criterion.
Minimum blade height above board plane: {m['minimum_board_height_m']*1000:.6f}mm.
Minimum blade/fixture AABB axis separation: {m['minimum_fixture_aabb_gap_m']*1000:.6f}mm.
Minimum blade/other-robot-body AABB separation, excluding own body/directly mounted hand: {a['independently_reconstructed_minimum_blade_body_gap_m']*1000:.6f}mm.
Minimum2mm-inflated other robot-body/target AABB gap: {a['minimum_inflated_other_body_target_gap_m']*1000:.6f}mm.
Maximum knife/hand transform error: {m['maximum_mount_position_error_m']*1e6:.6f}micrometres and {m['maximum_mount_angle_error_rad']:.9g}rad.
No monitored forbidden rigid-contact force during route/settling; positive probe/floor and reset/clear controls separately pass. Arm joint limits pass. Peak arm gravity feedforward {a['maximum_gravity_effort_nm']:.6f}Nm with no clipping needed under unchanged effort limits.

Actual joint directions and all four tool-motion phases match their commands. All recorded position/velocity/effort schedules match the declared route interpolation and bounded gravity feedforward. Actual Native tool pose agrees with FK of actual joints within {a['maximum_tool_fk_position_difference_m']*1e6:.6f}micrometres in sampled cross-checks. These values describe simulation tracking; they do not certify physical sensing or hardware accuracy. The independent audit's inherited labels “half_speed_command_sequence” and “stroke down” refer to the8-substep interpolation clock and the dry descent, respectively; they do not assert the old spatial route or a cutting stroke.

Preservation and limits
The ideal fixed knife constraint remains selected, with no physical bracket or finger grasp. No model/material, damping, mass, gravity, joint-limit or original asset change. No joint-state/tool-pose overwrite during executed motion. Clearance checks use sampled authored-bound AABBs and the board plane; these are not general swept/mesh-distance contact qualification. A visually overlapping camera projection does not override the independently measured positive gap.
4091 PhysX steps =3 monitor setup +3848 route +240 settling;0Newton/deformable steps. The route and final paused viewport were visually inspected through native viewport stills. No video, target contact, cutting, training or renewed force/energy investigation. Protected runtime {s['elapsed_wall_s']:.2f}s; owned-process cleanup complete. The bounded paused inspection window ended and the saved scene is retained.

Status and next decision
Closer scripted approach/retraction is now verified at20mm nominal standoff. This does not qualify the actual contact pose, deeper stroke, blade-board interaction, mounted moving-contact force/work, live fracture or separation. Experimental validation17 and loaded/post-cut reset22 remain pending. The next stage should specify one bounded nonfracturing contact experiment and its fixture-specific measurements before running it; it must resolve or explicitly redesign the still-open mounted-contact gate without treating this dry pass as a substitute. Do not continue lowering the knife into the tomato in this task.

Evidence
Host preflight: {plan/'measurements.json'}
Rejected high-pose plan: {R/'runs/offline/near_approach_plan_20261102_01/failure.json'}
Native measurements: {run/'measurements.json'}
Raw measured states/commands: {run/'measured_motion.npz'}
Independent readback: {W/'independent_readback01/measurements.json'}
Protected completion/cleanup: {run/'supervisor_result.json'}
Saved scene: {run/'inspection_scene.usda'}
Near-stop viewport: {run/'240_route_detail.png'}
'''
(W/'NEAR_TARGET_DRY_APPROACH_20261102.txt').write_text(report);shutil.copy2(W/'NEAR_TARGET_DRY_APPROACH_20261102.txt',O/'near-target-dry-approach-20261102.txt')
p=R/'work/integration_20261102/publish_integration_gates.py';t=p.read_text();shutil.copy2(p,W/'publish_integration_gates_before_approach.py');marker="d['updated']=datetime.now";assert marker in t
block='''# Latest verified motion: closer approach with positive clearance, no contact.
d['integration_focus']={'title':'Closer approach verified · stopped above tomato','text':'One visible approach/withdraw/return cycle passes independent readback. Blade stopped19.98mm above the target envelope; maximum tool error0.066mm. The ideal mount stayed rigid. No target contact or cutting; mounted-contact qualification remains open.'}
items[21]['progress']='Original offset dry-route and corrected-controller evidence preserved. A new reachable approach aligned with the prepared-plane host orientation passes:20mm nominal standoff, measured19.98mm vertical gap, maximum tool error0.066mm and settled0.005mm. All measured commands, mount, joint and sampled clearance checks pass. This is a dry approach only; actual contact/deeper stroke remains unqualified.'
items[21]['checks']=['PASS — corrected controller and right-arm approach/withdraw/return; no joint-state overwrites during motion','PASS — measured19.98mm blade/target-envelope gap; board height76.98mm','PASS — peak tool error0.066mm and settled0.005mm; independent raw command/geometry readback','PASS — fixed knife, arm limits, separate collision-monitor positive/clear controls','SCOPE — static tomato display; sampled authored bounds; no contact/deeper stroke qualification']
if not any(x['title']=='Near-target dry approach' for x in d['integration_checkpoints']):
 d['integration_checkpoints'].insert(2,{'status':'done','title':'Near-target dry approach','detail':'New16-second approach/withdraw/return passes independent measured-state/geometry checks. Stopped19.98mm above conservative tomato envelope, peak tracking error0.066mm. No target dynamics/contact or cutting.'})
d['near_approach_review']={'report':'near-target-dry-approach-20261102.txt','native_run':'near_approach_20261102_01','passed':True,'contact_qualified':False,'near_stop_vertical_gap_mm':19.98263353950651}
'''
p.write_text(t.replace(marker,block+'\n'+marker,1))
builder=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');t=builder.read_text();shutil.copy2(builder,W/'build_progress_view_before_approach.py');t=t.replace('href="dry-tracking-correction-20261102.txt">Read the corrected robot motion results','href="near-target-dry-approach-20261102.txt">Read the near-target approach results',1);builder.write_text(t)
with (R/'work/integration_20261102/WORKING_STATE.txt').open('a')as f:f.write('\nNEAR-TARGET DRY APPROACH COMPLETE: hostplan01rejectedunreachablehigh80mm beforeNative; plan02onlyhigh40mm retained20mmstop/allIK/clearancegates PASS3848interpolatedstates. Native near_approach01PASS4091PhysX0Newton +independentrawallgeometry/command/velocity/ffreadbackPASS. Samecorrectedcontroller/gains/mechanics, NEW481sample16.033sroute planned20mm standoffalignedhostpreparedplaneorientation; actualstop19.98263mm, peaktool65.71um/final5.14um; maxorientation95.96urad; rigidmount.162um/.383urad. Board76.9799mm/fixture55.2637mm/otherbody63.1087mm/inflatedotherbodytarget131.6204mm allpositive; noforbiddencontacts. Protectedcleanup[]. Originalnative15mmtargetgateunchanged; noold130mmstrokeamplitudeclaim. Targetunionreference/prepared STATIC; no dynamics/contact/fracture/video/training/energybranch. Nextoneboundednonfracturingcontactspecificationbeforeanytouch;23Bforceworkgate/remainopen,17pending22postcutpending. Report '+str(W/'NEAR_TARGET_DRY_APPROACH_20261102.txt')+'\n')
print('Saved near-approach report and checklist update.')
