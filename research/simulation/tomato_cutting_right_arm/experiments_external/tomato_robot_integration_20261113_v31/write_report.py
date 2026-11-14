from pathlib import Path
import json,hashlib,datetime
W=Path(__file__).resolve().parent;r=W/'runs/cut03_margin';result=json.loads((r/'integration_result.json').read_text());assert result['pass'];native=json.loads((r/'native_metrics.json').read_text());contact=json.loads((W/'runs/contact02/integration_result.json').read_text());replay=json.loads((W/'runs/cut01/actual_pose_replay.json').read_text());expected=json.loads((W/'preserved_sources.json').read_text());unchanged={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in expected.items()};assert all(unchanged.values())
report={'status':'approximate_robot_integration_demonstrated','updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete_native_cycle_pass':True,'result':result,'native_metrics':native,'nonfracturing_contact':contact,'independent_actual_pose_replay':replay,'original_sources_unchanged':unchanged,'renderer_check':'pending','launcher':str(W/'launch_integrated.sh'),'scope':{'scripted':True,'fixed_knife_attachment':True,'original_handle_grip_robot_kitchen_preserved':True,'visible_tested_straight_blade':True,'kinematic_retracting_pickup_cradle':True,'fixed_tomato_bottom_layer':True,'approximate_material':True,'real_tomato_calibration':False,'motor_work_validated':False,'full_robot_RL_throughput_qualified':False,'force_convergence_qualified':False,'trained_policy':False},'notes':['The first complete cut/withdrawal failed only its short settling check; it is retained as a failed overall run.','A 1ms feedback trial exposed native board contact from within the oversized speculative-contact range. The corrected version retains identical geometry and zero rest offset, uses0.25mm detection margins on blade and board, and preserves the1mm geometric clearance stop.','The corrected1ms run completed without a stop. Force accuracy is approximate; older exchange trials varied by about5–8% in peak load and were not all identically configured.','Material replay reproduced the same broken bonds with1.43% peak-load difference and0.0947mm maximum position difference.','Coupled phase39.225 simulated seconds took366 wall seconds, excluding pickup/startup. The standalone137 batched task transitions/s must not be quoted as full-robot performance.']}
(W/'RESULT.json').write_text(json.dumps(report,indent=2));(W/'reports/source_preservation.json').write_text(json.dumps({'all_unchanged':True,'files':unchanged},indent=2))
text='''APPROXIMATE TOMATO IN THE ORIGINAL ROBOT / KITCHEN — v31

COMPLETE NATIVE CYCLE: PASSED (runs/cut03_margin)
- The hand closes on the original handle before lift; ideal fixed attachment.
- The tested straight blade is visibly fitted, as authorized.
- Measured native blade motion drives the same approximate tomato material.
- The material reaction force and moment are applied once to the native tool COM,
  one1ms interval later. No desired-pose-only cutting animation is used.
- The cut broke1857 bonds and created two disconnected pieces, with46.0% of
  total mass in the smaller piece. Horizontal withdrawal and settling passed.
- Peak summed simulated blade load:1.3505N (2N stop retained).
- Peak particle penetration:0.0081mm (0.1mm stop retained).
- Final knife/material clearance:48.44mm; minimum native blade/board gap:2.759mm.
- Maximum fixed-mount translation drift:0.00198mm.
- No training, real-tomato calibration or motor-work qualification is claimed.

OTHER VERIFIED COMPONENTS
The full dry route passed. A separate contact test with cutting disabled had no
broken bonds or fracture work; it measured0.07749N and applied up to0.07608N to
the native tool. Independent replay of saved actual robot blade poses created
the same broken bonds and two pieces. All material-state arrays restored exactly.
Robot restart uses a fresh process; an in-place loaded robot reset is not claimed.

ENVIRONMENT CHANGE IN THIS SEPARATE VERSION
The empty pickup cradle retracts110mm after the knife is lifted. Visible posts
and native kinematic collision bodies move together. This is an ideal support
mechanism, not a force-driven actuator. The original robot, kitchen, grip and
source files remain unchanged. The tomato is still held by its bottom layer.
The original0.25kg knife mass, COM and inertia are retained as an explicit tool
approximation even though the visible blade is shorter.

NUMERICAL LIMITS AND FAILED EVIDENCE
The initial2ms run separated and withdrew successfully but was not quiet enough
after1s, so its overall result remains failed. A longer unchanged-law settlement
probe resolved that condition. The final controller permits up to20s settlement
and requires0.5s continuously below the existing speed/support threshold.
The corrected successful run needed about1.365s of final settlement.

The first1ms trial hit a native board-contact problem during withdrawal despite
positive clearance on the preceding step. The prior native contact envelope
was4mm combined; the corrected envelope is0.5mm combined, with zero rest offset
and the existing1mm geometric clearance stop. Blade/board geometry and tomato
laws were not changed. No collision pair or physical stop was disabled to pass.

Force convergence is not established. Peak-load differences across exchange
trials were about5–8%, and their native contact settings were not all identical.
Saved-pose replay differed by1.43% in peak load and0.0947mm in maximum position.
The material is explicitly approximate and uncalibrated. Cosmetic skin, calyx
and cut flesh do not establish anatomical or experimental material realism.

PERFORMANCE
The successful coupled phase took366 wall seconds for39.225 simulated seconds.
Startup, pickup and approach are additional. This is an operational robot/kitchen
demonstration, not a qualified fast articulated-robot RL training environment.
The earlier137 batched material task transitions/s excludes the native robot,
kitchen rendering and policy inference. No learned policy has been trained.

RUN
bash /home/omen/Documents/Codex/experiments/tomato_robot_integration_20261113_v31/launch_integrated.sh
Press Play in Isaac Sim for pickup, cut and horizontal withdrawal. Pause pauses
the controller. Close the window and launch again for a fresh episode. Opening
the USD file alone does not run the live tomato solver/controller.

Evidence is preserved in runs/, reports/, RESULT.json and each checked_sources
archive. Failed runs remain available. Existing reference research gates remain
pending, including experimental validation and strict motor-work qualification.
'''
# Readable spacing in the report without changing identifiers/paths.
for old,new in [('one1ms','one 1 ms'),('broke1857','broke 1857'),('with46.0%','with 46.0%'),(':1.3505N',': 1.3505 N'),('(2N','(2 N'),(':0.0081mm',': 0.0081 mm'),('(0.1mm','(0.1 mm'),(':48.44mm',': 48.44 mm'),(':2.759mm',': 2.759 mm'),(':0.00198mm',': 0.00198 mm'),('measured0.07749N','measured 0.07749 N'),('to0.07608N','to 0.07608 N'),('retracts110mm','retracts 110 mm'),('original0.25kg','original 0.25 kg'),('initial2ms','initial 2 ms'),('after1s','after 1 s'),('to20s','to 20 s'),('requires0.5s','requires 0.5 s'),('about1.365s','about 1.365 s'),('first1ms','first 1 ms'),('was4mm','was 4 mm'),('is0.5mm','is 0.5 mm'),('existing1mm','existing 1 mm'),('about5–8%','about 5–8%'),('by1.43%','by 1.43%'),('and0.0947mm','and 0.0947 mm'),('took366','took 366'),('for39.225','for 39.225'),('earlier137','earlier 137')]:text=text.replace(old,new)
(W/'RESULT.txt').write_text(text)
p=W/'README.txt';s=p.read_text().replace('A 2 ms exchange interval is used initially.','The validated demo uses a 1 ms exchange interval.').replace('Launch after the final report confirms completion:','Verified complete cycle: see RESULT.txt and runs/cut03_margin.\nLaunch:');p.write_text(s)
print('Report written; reference sources verified unchanged.')
