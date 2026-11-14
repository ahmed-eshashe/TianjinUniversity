from pathlib import Path
import json,datetime
from zoneinfo import ZoneInfo
w=Path(__file__).resolve().parent
stages=[
('Completed components',[
('done','Preserve the original simulation and checkpoint 6,925.','Original robot, kitchen, grip and motion interface remain unchanged.'),
('done','Profile the original solver and compare candidate engines.','Recorded component timings and differences in models/resolution; no equal-accuracy speedup claim.'),
('done','Get DiSECt examples running with clean exits.','Two corrected-candidate prism repeats complete normally; forward-only qualification.'),
('done','Repair and independently validate prism cut surfaces.','No duplicate/degenerate cut faces, full section coverage, physical spring arrays preserved.'),
('done','Build and validate the separate tomato FEM mesh.','Original exterior, total mass, cut location and 25 support coordinates retained; internal resolution changed.'),
('done','Identify the explicit timestep limit and correct hydrostatic damping.','Relative-velocity correction is isolated and versioned; coefficients were not reduced to pass.'),
('done','Verify translation and resolved-signal damping controls.','Low-signal affine precision remains failed and must not be inferred from these scoped passes.'),
('done','Complete a one-second finite tomato gravity hold.','No NaNs or collapsed sampled cells; complete settling FAILED, so contact is still gated.')]),
('Next: numerical consistency and speed',[
('planned','Fix tiny movements being lost during position updates.','Use an isolated numerical version; preserve material, support and geometry.'),
('planned','Verify the fix against independent motion references and resets.','Check rigid translation, free fall and a damped oscillator against a float64 reference; clear any added numerical state on reset.'),
('planned','Establish trustworthy small-force precision.','Preserve the failed low-signal control; quantify the usable signal range and absolute error floor independently.'),
('planned','Establish a stable, sufficiently fast integration method.','Assess one damping-aware route if needed. Compare against a consistent reference under prospectively specified limits; retain 0.1mm/5% requirements where applicable. Measure setup, stepping, output and memory separately; stop with a cost/implementation decision before expanding.')]),
('Before blade contact',[
('planned','Pass the complete unloaded settling check.','Retain sampled finite/volume/support/contact limits and speed <=1mm/s for the final 0.1s; current run has not passed.'),
('planned','Validate board contact and sustained target support.','Distinguish the infinite-plane proxy from the original finite board; document load paths and any remaining limitations.'),
('planned','Prepare and validate the tomato cutting interface.','Check paired geometry, mass accounting and every material connection across the proposed slice; an intact bulk hold is not a prepared cutting-assembly pass.'),
('planned','Define the fracture law and its timestep dependence.','Document differences from original skin/pulp/cohesion and normalize/validate per-step damage interpretation before refinement; no calibration claim.'),
('planned','Verify knife representation, nonfracturing contact and force reporting.','Use the original blade through a checked adapter, or explicitly disclose an approved proxy. Disable fracture for indentation/unloading; distinguish net reaction from summed contact-force magnitudes.')]),
('First genuine slice and reliability',[
('planned','Pass a shallow scripted cut and controlled stop.','Use progressive contact-driven material failure, saved force/deformation/geometry traces and declared stops.'),
('planned','Execute the full stroke and withdraw horizontally toward the robot.','No upward withdrawal through the target; preserve intended blade orientation and clearance.'),
('planned','Prove actual material separation.','No surviving load-bearing material ties; two intended substantial pieces, not a visible gap or isolated fragments.'),
('planned','Verify post-withdrawal stability, mass and slice shape.','Observe at least one simulated second after blade clearance; stable board/cut-face contact and no healing.'),
('planned','Repeat and test resolution, size and path changes.','Repeat from fresh/reset state; refine once, change size once and path once. Distinguish precomputed new interfaces from deviations after preparation; use negative controls for the success evaluator.'),
('planned','Demonstrate multiple successive slices.','Separate extension requiring supported interface/topology updates and valid remaining-fruit state; one detached cap does not establish repeated slicing.')]),
('Connect the candidate to the robot',[
('planned','Connect through the existing motion and reaction interface.','Preserve robot, kitchen and disclosed fixed attachment; no engine adoption before evidence review.'),
('planned','Recheck actual robot tracking, grip, posture and clearance.','Correct arm motion, natural handle grip and backward/outward elbow; no per-frame teleportation to manufacture tracking.'),
('planned','Validate mounted-blade feedback and loaded support.','Verify reaction signs, origins, clocks and native articulation response; strict force/work qualification remains a separate open research gate.'),
('planned','Pass clean loaded, failed-episode and post-cut resets.','Clear both engine states, numerical compensation, material history, contact/wrench queues, clocks and observations; compare to fresh launch.')]),
('Learning, after the baseline qualifies',[
('planned','Freeze observations, actions, rewards, stops and success evaluation.','Same API/evaluator for scripted and learned methods; evaluator-only fracture/connectivity truth must not leak into actor inputs.'),
('planned','Collect successful scripted demonstrations and split the data.','Record action labels and provenance; keep independent development/held-out cases separate.'),
('planned','Train and evaluate imitation of the verified baseline.','Start with the narrow supported task; measure closed-loop success and runtime before expansion.'),
('planned','Train bounded learned corrections and compare fairly.','Constrain supported path deviations; pair with scripted baselines on held-out cases, report uncertainty, forces, geometry, failures and compute cost.')]),
('Experimental validation — intentionally pending',[
('pending','Compare against independent measured tomato experiments.','Remains pending by user decision; synthetic simulation development must not be described as experimental validation.')]),
('Later dual-arm extension',[
('deferred','Qualify contact-based left-hand support.','Test load retention/slip first; remove hidden rigid-fixture support before claiming hand stabilization.'),
('deferred','Coordinate both arms with verified clearance and failure handling.','Support -> cut -> horizontal withdrawal -> release; stop safely on support loss and verify reset.'),
('deferred','Compare dual-arm and fixed-fixture cutting.','Use matched cases and report force, slip, drift, clearance, cut quality, reliability and cost.')])]
items=[i for _,a in stages for i in a];counts={status:sum(i[0]==status for i in items) for status in ['done','planned','pending','deferred']};data={'title':'DiSECt to reliable robot slicing and learning — execution checklist','updated':datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'scope':'Component passes are distinct from settled tomato, successful cutting, robot integration and training. Original run remains paused.','counts':counts,'total':len(items),'stages':[{'title':title,'items':[{'status':status,'task':task,'acceptance_or_limit':note} for status,task,note in a]} for title,a in stages]}
(w/'EXECUTION_CHECKLIST.json').write_text(json.dumps(data,indent=2));lines=[data['title'],'Updated 8 November 2026 (Asia/Shanghai)',f"{len(items)} checks: {counts['done']} verified component checks; {counts['planned']} planned; {counts['pending']} experimentally pending; {counts['deferred']} later dual-arm checks.",'Counts are not percentages of engineering effort. Full separation, settling and robot-integrated cutting are not qualified.','']
for title,a in stages:
 lines.extend([title,''])
 for status,task,note in a:lines.extend([f"[{'x' if status=='done' else ' '}] {task}"+(f' [{status}]' if status in ['pending','deferred'] else ''),'    '+note])
 lines.append('')
(w/'EXECUTION_CHECKLIST.txt').write_text('\n'.join(lines));out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');
import shutil
shutil.copy2(w/'EXECUTION_CHECKLIST.txt',out/'disect-execution-checklist.txt');shutil.copy2(w/'EXECUTION_CHECKLIST.json',out/'disect-execution-checklist.json');print(json.dumps(data['counts']));print('Total',data['total'])
