from pathlib import Path
import json,shutil,hashlib
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');W=R/'work/dry_tracking_20261102';O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=R/'runs/native/dry_tracking_corrected_20261102_01'
m=json.loads((run/'measurements.json').read_text());a=json.loads((W/'independent_readback01/measurements.json').read_text());s=json.loads((run/'supervisor_result.json').read_text());assert a['passed']and s['passed']and not s['remaining_live_group_members']and all(m['checks'].values())
old=R/'runs/native/visible_dry_motion_20261102_01';b=json.loads((old/'measurements.json').read_text());ba=json.loads((R/'work/dry_motion_20261102/independent_readback01/measurements.json').read_text())
report=f'''DRY ROBOT TRACKING CORRECTION — 2 November 2026

VERDICT: PASS — one corrected 16.033-second scripted dry route, measured in visible Isaac Sim, independently checked from saved raw states and commands. Stop before target contact.

What changed
A separate worker uses the same 481 route waypoints and half-speed clock. Consecutive joint waypoints are linearly interpolated at each physics step, instead of holding and jumping to each sample. Right-arm velocity targets follow that interpolation. Native gravity-compensation effort is added only on arm joints, bounded by the unchanged existing effort limits. The left arm retains its constant position/zero velocity reference. Drive gains, joint limits, mass/inertia, gravity, body damping, blade geometry, fixed knife constraint, original scene and target/material parameters are unchanged. No effort, gravity or force-measurement precision investigation was performed. This test evaluates the combined focused controller correction; it does not attribute improvement separately to each change.

No joint-state or tool-pose overwrites occur during the executed route or settling. State writes are confined to setup/reset before the route. Motor target commands drive the actual articulation dynamics. The desired Cartesian pose is FK of the commanded joint reference; the actual pose is the Native measured link pose. Actual-state FK cross-check agrees within {a['maximum_tool_fk_position_difference_m']*1e6:.3f} micrometres in sampled readback controls. These are simulated relative tracking measurements, not physical sensor or hardware accuracy claims.

Before -> after, same offset dry route
Maximum tool-position tracking error: {b['maximum_tool_tracking_position_m']*1000:.6f} -> {m['maximum_tool_tracking_position_m']*1000:.6f} mm.
Settled tool-position tracking error: {ba['final_tool_tracking_m']*1000:.6f} -> {m['final_tool_tracking_position_m']*1000:.6f} mm.
Maximum right joint tracking error: {b['maximum_right_tracking_rad']:.9g} -> {m['maximum_right_tracking_rad']:.9g} rad.
Maximum tool orientation tracking error: {b['maximum_tool_tracking_angle_rad']:.9g} -> {m['maximum_tool_tracking_angle_rad']:.9g} rad.
Maximum left arm joint deviation from hold reference: {b['maximum_left_arm_tracking_rad']:.9g} -> {m['maximum_left_arm_tracking_rad']:.9g} rad.
Maximum joint speed: {b['maximum_joint_speed_rad_s']:.9g} -> {m['maximum_joint_speed_rad_s']:.9g} rad/s.
Minimum blade height above board plane: {b['minimum_board_height_m']*1000:.6f} -> {m['minimum_board_height_m']*1000:.6f} mm.

Prospective engineering targets (written in protocol.json before launch)
Maximum tool-position error <=1mm: PASS.
Settled tool-position error <=0.25mm: PASS.
Maximum tool orientation error <=0.002rad: PASS.
Maximum left arm joint deviation <=0.002rad: PASS.
These scoped controller targets were chosen before results. The1mm target is under one sixth of the prior approximately6mm board clearance. They are not cutting, sensor or hardware safety certification. Original geometric/speed/rigid-mount/contact/arm-limit stops were retained.

Motion, mount and clearance
All seven right-arm joint motions match command directions; each four-phase tool height displacement has the commanded sign. Independent actual/command joint correlations exceed0.9999999. The reference velocity and per-physics-step position command schedules exactly match the declared interpolation, including zero velocity during the initial hold and final settling. Arm gravity feedforward peak {a['maximum_gravity_effort_nm']:.6f} Nm, with no clipping required. No feedforward is applied to hand/follower DOFs.
Minimum blade/target authored AABB axis separation {m['minimum_target_aabb_gap_m']*1000:.6f} mm (original15mm gate).
Minimum blade/fixture authored AABB axis separation {m['minimum_fixture_aabb_gap_m']*1000:.6f} mm.
Minimum blade/other robot body AABB separation {a['minimum_blade_to_other_body_aabb_gap_m']*1000:.6f} mm, excluding knife itself and directly constrained hand.
Minimum blade height above board top plane {m['minimum_board_height_m']*1000:.6f} mm (original4mm gate).
Maximum hand/knife relative-position error {m['maximum_mount_position_error_m']*1e6:.6f} micrometres; relative angle error {m['maximum_mount_angle_error_rad']:.9g} rad.
No monitored forbidden rigid-contact force during route/settling. Separate positive probe/floor control and reset/clear checks pass. Arm joint limits and original3rad/s speed stop pass.
Final maximum joint speed {m['final_joint_speed_rad_s']:.9g} rad/s <0.002rad/s settling criterion; no final velocity overwrite is used to make this pass.
Clearance numbers are sampled authored-geometry AABB/board-plane checks at every executed physics interval. No arbitrary swept CCD, near-contact mesh-distance or cutting-route qualification is inferred. The ideal knife constraint has no physical bracket; the visible offset below the hand remains disclosed.

Execution and evidence
4091 PhysX steps =3 independent monitor-control setup steps +3848 route steps +240 settling steps. One route only; no hidden physical settling or time refinement cohort. Zero Newton target/deformable steps. The tomato in the rendered scene is a stationary visual. No tomato contact, fracture, video, training or material change. Rendering stills show the actual moving simulated robot at route endpoints and the lowest stroke sample.
Protected wall runtime {s['elapsed_wall_s']:.2f} seconds; cleanup reports no remaining owned group members. Scene paused for a bounded inspection interval, then the owned app closed. Saved scene remains available.
Native measurements: {run/'measurements.json'}
Raw actual/command states and efforts: {run/'measured_motion.npz'}
Independent audit: {W/'independent_readback01/measurements.json'}
Predeclared protocol: {W/'protocol.json'}
Protected completion: {run/'supervisor_result.json'}
Saved scene: {run/'inspection_scene.usda'}
Lowest-stroke actual viewport: {run/'240_route_detail.png'}

Next proposed step
Plan and check a reachable approach nearer the tomato that ends with a measured positive clearance, using this corrected controller and explicit uncertainty/stop margins. Run it as a new dry route before attempting contact. The current successful motion stays on the original offset path; it does not close the actual cutting-route gate or the older moving mounted-contact force/work gate. Experimental validation17 and coupled loaded/post-cut reset22 remain pending. Do not start a cutting stroke based solely on the new dry tracking result.
'''
(W/'DRY_TRACKING_CORRECTION_20261102.txt').write_text(report);shutil.copy2(W/'DRY_TRACKING_CORRECTION_20261102.txt',O/'dry-tracking-correction-20261102.txt')
p=R/'work/integration_20261102/publish_integration_gates.py';t=p.read_text();shutil.copy2(p,W/'publish_integration_gates_before_tracking.py');marker="d['updated']=datetime.now";assert marker in t
block='''# Verified focused controller correction; target contact remains a separate gate.
d['integration_focus']={'title':'Dry tracking corrected · ready to plan the next route','text':'Same offset dry route: maximum simulated tool error improved from9.73mm to0.029mm; settled error0.006mm. Independent readback, fixed mount and clearances pass. Actual approach/contact qualification remains next; no cutting.'}
items[21]['progress']='Original dry-route evidence preserved. A separate controller version adds consistent velocity targets, per-step interpolation and bounded arm gravity compensation, with unchanged drive gains and mechanics. One visible16-second route +independent readback passes prospective dry targets: peak tool error0.029mm, settled0.006mm, board height12.0mm, target gap32.4mm. Actual cutting approach remains unqualified.'
items[21]['checks']=['PASS — all seven right-arm joints and four tool-motion phases follow commands','PASS — independent raw position/velocity command and bounded gravity-feedforward checks','PASS — maximum tool error0.029mm<1mm and settled0.006mm<0.25mm predeclared dry targets','PASS — rigid fixed knife, arm limits, collision positive/clear controls; no target contact','SCOPE — original offset route; no physical bracket, hardware accuracy or cutting claim']
for point in d['integration_checkpoints']:
 if point['title']=='Slow scripted dry motion':
  point['detail']='Original16-second cycle preserved. Corrected controller passes independent readback: peak simulated tool error0.029mm, settled0.006mm; rigid mount, target gap32.4mm and board height12.0mm. Actual cutting approach still needs its own dry check.'
d['dry_motion_review'].update(report='dry-tracking-correction-20261102.txt',native_run='dry_tracking_corrected_20261102_01',maximum_tool_tracking_error_mm=0.02865373566253116,settled_tool_tracking_error_mm=0.006094212283938403,tracking_correction_passed=True,contact_ready=False)
'''
p.write_text(t.replace(marker,block+'\n'+marker,1))
builder=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');t=builder.read_text();shutil.copy2(builder,W/'build_progress_view_before_tracking.py');t=t.replace('href="slow-robot-motion-review-20261102.txt">Read the robot motion results','href="dry-tracking-correction-20261102.txt">Read the corrected robot motion results',1);builder.write_text(t)
with (R/'work/integration_20261102/WORKING_STATE.txt').open('a')as f:f.write('\nFOCUSED DRY TRACKING CORRECTION COMPLETE: dry_tracking_corrected01PASS4091PhysX/0Newton one visible16.033sroute +1ssettling. Separateworker_v02 samewaypoints/timing/gains/mechanics; linearpersteps q+consistentqd+nativearmgravityff boundedunchangedeffortlimits. Predeclared1mmmax/.25mmsettled/.002radorientation/lefthold allPASS. Measuredpeaktool28.65um/final6.09um vsold9.73mm/6.74mm; maxorientation52.35urad; maxjoint.00037265rad; board11.9948mm/target32.4064mm/fixture34.9117mm/otherbody74.1813mm; rigidmount.168um/.378urad; noforbiddencontacts. Independentrawcommand/velocity/ff/stateauditPASS. Protectedcleanup[]. No force/workcampaign, targetcontact/cutting/video/training. Next proposed closer dry approach only; actualrouteand23Bremainopen. Report '+str(W/'DRY_TRACKING_CORRECTION_20261102.txt')+'\n')
print('Published corrected dry tracking evidence.')
