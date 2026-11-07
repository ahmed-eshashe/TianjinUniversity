from pathlib import Path
import json,shutil
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');W=R/'work/live_clear_assembly_20261102';O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=R/'runs/native/live_clear_assembly_20261102_01';m=json.loads((run/'measurements.json').read_text());a=json.loads((W/'independent_readback02/measurements.json').read_text());s=json.loads((run/'supervisor_result.json').read_text());assert a['passed']and s['passed']and all(m['checks'].values())and not s['remaining_live_group_members']
text=f'''LIVE CORRECTED ROBOT + SUPPORTED TOMATO —0.1s clear assembly,2November2026

VERDICT: PASS within the short contact-free assembly hold scope. Touch launch remains NOT READY.

One protected visible Isaac Sim run initialized the real articulated robot at the verified near-stop joint configuration and the full4032-node Newton target at its previously qualified supported equilibrium. It advanced24actual PhysX hold steps at1/240s and240actual custom target-solver steps at1/2400s,10target substeps per robot step, to matching0.1s endpoints. Three rigid-contact monitor setup steps were separately counted, giving27total PhysX steps. Stock Newton VBD calls remain0; target dynamics use the existing custom float64 implicit solver on the Newton model/registry. There was no continuously coupled home-to-target approach in this test.

The same corrected controller holds the arm using position/zero-velocity targets and bounded native arm gravity feedforward. Original physical assets, drive gains, mass/inertia, damping, gravity, fixed knife mount, target constitutive rest data and25-node remainder fixture remain unchanged. Cap nodes remain unpinned. Damage/history/eligibility remain zero. No tool or joint pose writes were used after initialization/reset to manufacture hold accuracy.

Live state display
The old /CuttingTargetVisual is deactivated in the new scene layer. /LiveNewtonTomato displays the actual full target node coordinates and original5504triangles, updated/read back after every accepted target step. It has no extra PhysX collider or rigid-body API. Maximum live display-coordinate rounding difference {a['maximum_display_error_m']:.9g}m; exported final USD points agree within {a['maximum_exported_scene_error_m']:.9g}m. Both are below the declared1e-7m display tolerance. Independent readback verifies all240coordinate arrays and the exported scene.
The supported equilibrium remains unchanged within the solver's resolution: recorded target displacement and velocity are exactly zero. That is a stable supported-state result, not visible deformation under load or a general deformation-display response qualification. No artificial wiggle or displacement was added for appearance.

Physical and synchronization checks
Minimum actual CAD blade/actual target vertical separation: {a['minimum_vertical_blade_target_gap_m']*1000:.6f}mm >15mm. This differs from the earlier19.98mm conservative-envelope gap because the live prepared target is lower than the union/reference envelope. All target and robot endpoints are checked.
All CAD vertices lie in the blade bounds and all target triangles in their node bounds. Strict positive separating-axis distance therefore certifies empty contact for these sampled states; zero generated contact/wrench is justified by geometry. No populated blade pressure/feedback adapter is executed in this clear case, and this is not a force-transfer pass. Within-interval general CCD is not inferred.
Minimum target volume ratio {a['minimum_volume_ratio']:.9g} >0.1.
Maximum board penetration {a['maximum_board_penetration_m']*1e6:.6f}micrometres <100micrometres.
Final gravity/board/fixture vertical forces: -1.193595N /0.920415N /0.273181N. Board and original fixture support the weight; the cap is not secretly fixed.
Maximum target linear/angular impulse residuals {a['maximum_linear_impulse_residual_ns']:.9g}Ns /{a['maximum_angular_impulse_residual_nms']:.9g}Nms. Original support/local/energy/volume/board bounds hold, with no energy increase.
Final robot tool-position error from its hold reference {m['final_tool_position_tracking_m']*1000:.6f}mm <0.25mm dry-controller target. Existing mount, joint-limit, speed, other-arm hold and monitored forbidden rigid-contact checks hold. Separate monitor positive/clear controls pass.
Target and robot clocks match at all24shared endpoints; no extra physical steps are hidden in rendering. This is not a robot energy/work qualification or a loaded reset/replay test.

Preservation and audit
Protected process finished in {s['elapsed_wall_s']:.2f}s, with no remaining owned group members. All{a['verified_source_files']}captured source/input hashes match. Existing evidence is preserved. The original launch guard is intentionally extended for the new worker/count contract; frozen model/scene sources were not altered.
Independent audit01's reference assertion failed because it compared reconstructed world fixture coordinates bit-for-bit with pre-origin-translation world coordinates. The difference was3.47e-18m, while time-dependent fixture displacement was exactly0. Audit02 compares exact temporal invariance and exactly identical origin round-trip arithmetic; it passes without relaxing a physical fixture tolerance. Audit01and its failure note remain preserved. No simulation rerun was needed.

Touch readiness decision
Clear assembly entry stage PASSED. The next implementation is a populated actual-CAD pressure/reaction adapter for the corrected controller, with correct once-only wrench origin, motion bounds and independent accepted traces. Do not lower the knife merely because the clear mesh is now live. The prior moving-contact force/work gate remains failed/unresolved; resolve a complete fixture-specific measurement contract before a touch launch. Do not reopen a broad damping/solver sweep or repeat passed suites. This result does not change experimental validation17, live fracture/separation, loaded/post-cut reset22, full23B or training readiness.

Evidence
Native result: {run/'measurements.json'}
Protected completion: {run/'supervisor_result.json'}
Independent readback02: {W/'independent_readback02/measurements.json'}
Preserved readback01 failure: {W/'independent_readback01/failure.json'}
Target/mesh/pose trace: {run/'live_target_trace.npz'}
Robot trace: {run/'robot_trace.json'}
Saved live scene: {run/'live_clear_inspection_scene.usda'}
Actual live-clear viewport: {run/'01_live_final.png'}
'''
(W/'LIVE_CLEAR_ASSEMBLY_20261102.txt').write_text(text);shutil.copy2(W/'LIVE_CLEAR_ASSEMBLY_20261102.txt',O/'live-clear-assembly-20261102.txt')
p=R/'work/integration_20261102/publish_integration_gates.py';t=p.read_text();shutil.copy2(p,W/'publisher_before_live_assembly.py');marker="d['updated']=datetime.now";assert marker in t
block='''# Verified short live clear assembly, distinct from loaded contact.
d['integration_focus']={'title':'Live robot + tomato verified · no touch yet','text':'0.1s clear hold passes:24robot and240live target steps with matching clocks. The tomato display uses actual Newton nodes; old static visual hidden. Blade stays24.15mm above the supported target. Populated contact/force-work qualification remains open.'}
if not any(x['title']=='Live robot + target clear hold' for x in d['integration_checkpoints']):
 d['integration_checkpoints'].insert(3,{'status':'done','title':'Live robot + target clear hold','detail':'0.1s:24robot/240target steps, matching clocks; independent node/display/geometry readback passes. Stable supported equilibrium,24.15mm blade gap, original fixture/free cap. No populated contact forces or cutting.'})
for point in d['integration_checkpoints']:
 if point['title']=='Live contact test specification':point['detail']='Clear assembly entry check PASSED. Actual pressure/reaction adapter and fixture-specific moving force/work gates still required before touch. No contact run or cutting qualification.'
items[20]['progress']='Existing sustained support and synthetic-load evidence preserved. Added0.1s live target + corrected robot clear hold: matching clocks, actual node-driven display, original fixture/free cap and24.15mm actual blade gap verified. Populated contact and full cutting-load envelope remain open.'
d['nonfracturing_contact_design'].update(status='clear_entry_passed_touch_not_ready',clear_entry_run='live_clear_assembly_20261102_01',new_native_runs=1,touch_launch_ready=False)
d['live_clear_review']={'report':'live-clear-assembly-20261102.txt','passed':True,'duration_s':0.1,'target_steps':240,'robot_steps':24,'touch_qualified':False}
'''
p.write_text(t.replace(marker,block+'\n'+marker,1))
builder=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');t=builder.read_text();shutil.copy2(builder,W/'builder_before_live_assembly.py');t=t.replace('href="nonfracturing-contact-test-20261102.txt">Read the next contact-test specification','href="live-clear-assembly-20261102.txt">Read the live robot and tomato results',1);builder.write_text(t)
with(R/'work/integration_20261102/WORKING_STATE.txt').open('a')as f:f.write('\nLIVE CLEAR ASSEMBLY COMPLETE: live_clear_assembly01protectedPASS49.87s,27totalPhysX=3setup+24hold;240actualcustomtargetstepsdt1/2400 to0.1s,robotdt1/24010subcycles. Original equilibrium/masses/rest/model/G/stiffness/fixed25/freecap preserved; initializeddirectlyatnearstopNOTexecutedapproach. ActualnodeMesh /LiveNewtonTomato4032points5504tris updatedeverytargetstep, static /CuttingTargetVisual inactive,no duplicatecollider. Target equilibriumexactzero recordedmotion/v; no fakewiggle or loadeddeformationclaim. Displayerr1.86nm/export3.62nm. ActualCADverticalgap24.1501mm (differentfromprior19.98union/referenceenvelope); boundsproveemptycontact, no populatedpressureadapterqualified. minJ.3919278,board4.864um,Fboard.9204+Ffixture.27318=weight1.1936. Finalrobottracking.486um. Independent02all240states/24clockendpoints/display/CSVUSD/geometry/momentumPASS76sourcehashes. Audit01referencefixedcomparisonfailed3.47e-18worldroundtrip; temporalmotionexact0;02usesexactsameoriginroundtripandtemporalinvariance;failure01preserved,noNativeRerun. Source '+str(W/'LIVE_CLEAR_ASSEMBLY_20261102.txt')+'. NEXTpopulatedcorrectedcontrollerCADreactionadapter+existingworkcontractentrybeforeanytouch;noforce/dampingsweep,17pending22postcutpending.\n')
print('Published verified live-clear assembly result; touch readiness remains false.')
