from pathlib import Path
import json,datetime,shutil,re,hashlib
W=Path(__file__).resolve().parents[1];now=datetime.datetime.now().astimezone().isoformat()
def save(name,data): (W/name).write_text(json.dumps(data,indent=2)+'\n')
report='''ISOLATED APIC REPAIR v03 — IMPLEMENTED; PHYSICAL REVALIDATION FAILED
10 November 2026

Decision
The approved single repair attempt is complete. Stop this candidate before further cutting. The original unresolved-velocity mode is removed in the independent control, and localized deformation now agrees with the stored strain within the declared screens. However, the repaired mechanics still fail timestep consistency. Gate 3 remains unqualified. No v03 physical cut, complete slice, robot integration or RL suitability is claimed.

What changed
A separate current-spatial-grid APIC backend replaces fixed-reference pure FLIP. Position and constitutive strain use the same grid motion; external contact impulses use its adjoint instead of direct particle kicks. Affine momentum is included in diagnostics and snapshots. Numerical transfer and support losses are logged separately from material/fracture work. Proposed persistent-history keys include both local cut-side codes and reference-connected fragment IDs; that extension has only CPU/GPU consistency coverage, not full moving-fragment qualification.

Existing material/constants/stops retained: E=100 kPa, nu=0.4, rho=1000 kg/m³, synthetic Gc=80 J/m², existing blade CAD/contact parameters, 2 N force stop, 0.1 mm whole-material penetration limit, and reconstructed/stored admissible volume ratios 0.1–10. The CAD and guards are preserved but were not reached in a new integrated cutting run. This is our isolated prototype, not an official CRESSim release or a calibrated tomato.

Verified results
• Independent null-mode fixture: old update moved material 0.25 µm while strain was effectively unchanged. APIC particle motion is zero to recorded precision; residual mode velocity is 5.87e-16 of its initial value. Removed energy is explicitly accounted for.
• CPU/GPU float64 agreement passes intact, partial-code and supported five-step cases, including the fragment-key extension. These are algebra/component controls.
• Rest, translation, rotation/affine controls, mass and linear/angular momentum checks pass in their tested scopes. Internal force agrees with an independent energy derivative.
• Localized 512-particle load/unload at 0.78125 / 0.390625 µs passes reconstructed-volume/strain consistency and energy accounting. Maximum deformation-gradient differences are 0.000822 / 0.000563; the declared limit is 0.02. These small localized tests do not certify knife contact.
• The 64,000-particle, 60 mm elastic compression/release test still fails. At shared t=0.02 s the final maximum velocity difference is 23.129 mm/s against the predeclared 5 mm/s screen. RMS difference is 9.216 mm/s; 75.55% of samples exceed 5 mm/s. Position difference is 0.03178 mm, within 0.1 mm. A position pass does not erase the velocity failure.
• At the initial 12.5 / 6.25 µs pair, velocity disagreement was 25.939 mm/s. One prospectively declared 16× timestep reduction did not resolve it. No further timestep search was made.
• The refined compression tests record 87.64% / 87.74% of initial elastic energy as numerical loss within 20 ms. Accounted-energy residuals are only 0.304% / 0.186%, but an accurately balanced dissipative ledger does not establish accurate elastic motion. No physical viscosity was introduced or calibrated. Damping is a substantial limitation, not fracture work.

Gate disposition
v01 Gates 0–2 remain historical component evidence only.
v02 Gate 3 failure is preserved.
v03 freeze/formulation/null-mode controls: pass within component scope.
v03 intact mechanics: FAIL (timestep consistency; substantial numerical damping disclosed).
v03 persistent-cut, CAD/recontact and paid crack-front requalification: NOT RUN after mechanics failure.
Gate 3 overall: BLOCKED; Gate 4 tomato, training and production adoption: NOT STARTED.

Cost and limits
The refined compression pilots took 101.33 and 203.44 wall seconds for 0.02 simulated seconds (5,067 and 10,172 wall seconds per simulated second). This is the verification harness, including frequent state copies, checks and saved traces, not an optimized pure-solver benchmark. Tracked backend arrays were 124.4 MB; this is not total peak GPU/host memory. Each pilot stayed below the 600-second cap. These results do not establish RL performance or the speed of official CRESSim/APIC implementations.

Recommended next action
Do not run another long cut, reduce the timestep again blindly, soften the material, or relax the physical stops. If further numerical development is authorized, first use the saved intact compression fixture to audit timestep-dependent transfer damping and the spatial stress/strain discretization against an independent mechanical reference. Require converged motion and an explicitly acceptable numerical-dissipation model before another contact test. Whether a revised transfer/integrator or spatial discretization is required is unresolved; this report does not claim a selected replacement. A further formulation change is outside this completed single repair attempt and needs a revised scope. Existing Isaac/DiSECt remains the preserved working setup.

Evidence
contract.json; configs/time_refinement_attempt.json; physical_model.md
formulation_controls.json; gpu_equivalence.json
mechanics_controls.json; mechanics_refined_controls.json
reports/refined_pair_saved_audit.json; reports/saved_damping_audit.json
reports/repair_outcome.png; runs/mechanics*/ (raw traces and snapshots)
preservation_check.json; manifest.json

Preservation
All 706 files covered by the frozen manifest match their original hashes. No dependencies were installed; no production simulator, robot, kitchen, grip or prior solver evidence was altered. Status/checklist metadata is updated separately, with before-copies in reports/checklist_before_v03. No v03 simulation worker remains running.
'''
(W/'REPORT.txt').write_text(report)
state={'updated':now,'status':'repair_complete_revalidation_failed','simulation_running':False,'adopted':False,'existing_setup_changed':False,'original_null_mode':'pass_independent_control','localized_geometry_strain':'pass_refined_test_scope','mechanics':'fail_timestep_consistency','gate3':'blocked','next_action':'Review saved compression damping and discretization before authorizing another formulation; no automatic further simulation.','evidence':['REPORT.txt','mechanics_refined_controls.json','reports/refined_pair_saved_audit.json','preservation_check.json']};save('status.json',state)
save('contact_fracture_controls.json',{'updated':now,'status':'not_run_mechanics_prerequisite_failed','adopted':False,'gate3_passed':False,'cut_created':False,'inherited_v02_qualification':False,'reason':'APIC mechanics failed predeclared timestep screen before contact requalification','force_stop_N':2,'whole_material_penetration_limit_m':.0001,'next':'Revised scope required for another numerical formulation; keep production unchanged'})
save('force_work_ledger.json',{'updated':now,'scope':'No v03 CAD cutting run; only intact mechanical tests','cutting_force_N':None,'paid_fracture_work_J':0,'new_fracture_area_m2':0,'numerical_damping_is_fracture':False,'ledger_status':'not_exercised_by_physical_cut','localized_external_work_evidence':'runs/mechanics_refined/localized.json','compression_damping_evidence':'reports/saved_damping_audit.json'})
audit=json.loads((W/'reports/saved_damping_audit.json').read_text());save('runtime_forecast.json',{'updated':now,'status':'not_RL_qualified','cases':audit['cases'],'scope':'Measured intact verification harness includes state-copy/check/trace overhead, not isolated kernel throughput or full contact; no extrapolated completion promise','peak_total_memory':'not_measured','full_contact_throughput':'not_measured_v03','physical_qualification_failed':True})
p=W/'physical_model.md';s=p.read_text().replace('This adjacency construction is initially qualified on regular block fixtures only.','This adjacency construction is restricted to regular block fixtures; moving-fragment and intact-bridge requalification was not reached because mechanics failed.').replace('The independent CPU algebra and GPU comparisons, rather than that citation alone, qualify the modified history/support/contact coupling.','Independent CPU algebra and GPU comparisons provide component evidence, not qualification of the modified history/support/contact coupling.');s+='\nFinal disposition: the null-mode and localized-strain controls pass, but mechanics timestep consistency fails. See REPORT.txt. The algorithm is implemented, not adopted or physically qualified.\n';p.write_text(s)
statuspath=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json');backup=W/'reports/checklist_before_v03';shutil.copy2(statuspath,backup/statuspath.name);s=json.loads(statuspath.read_text());s.update(status='gate3_blocked_after_approved_repair_revalidation',updated=now,candidate_directory=str(W),execution_status_path=str(W/'status.json'),simulation_running=False,next_action=str(W/'REPORT.txt'),runtime_qualification='Unqualified: intact mechanics refinement failed; verification costs recorded separately from RL throughput')
s['repair_authorization']={'decision':'Repair the isolated backend and revalidate','scope':str(W/'reports/approved_recovery_proposal.md'),'result':'implemented; revalidation failed; stopped'}
s['active_candidate_qualification']={'version':'v03','gate0':'freeze_pass','gate1':'fail_timestep_consistency','gate2':'not_requalified','gate3':'blocked_not_run','physical_cut':False,'component_evidence':str(W/'formulation_controls.json'),'mechanics_evidence':str(W/'mechanics_refined_controls.json')}
for gate in s['gates']:
 if gate['id']==3:
  gate['status']='blocked_after_repair_mechanics_failure';gate['evidence']+= [str(W/'REPORT.txt'),str(W/'mechanics_refined_controls.json')]
statuspath.write_text(json.dumps(s,indent=2)+'\n')
outputs=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
for name in ['disect-checklist.html','learning-roadmap.html']:
 p=outputs/name;shutil.copy2(p,backup/name);html=p.read_text();banner='''<aside id="mpm-gate3-status" style="margin:16px auto;padding:16px 20px;max-width:1150px;border:1px solid #f1b35b;border-left:5px solid #d99122;border-radius:12px;background:#fff7e8;color:#302319;font:15px/1.55 system-ui,sans-serif"><strong>Separate material prototype · Repair tested; Gate 3 remains blocked</strong><br>The repair removes the reproduced invisible-deformation mode and passes the localized strain checks. It still fails motion consistency when the timestep is halved, with substantial numerical damping. Further cutting tests stopped. No simulation is running; the existing Isaac/DiSECt setup and its milestone counts are unchanged.<br><a href="mpm-v03-repair-status-20261110.txt" style="color:#854900;text-decoration:underline">Verified repair results</a> · <a href="mpm-v03-repair-outcome-20261110.png" style="color:#854900;text-decoration:underline">Comparison chart</a></aside>'''
 html,n=re.subn(r'<aside id="mpm-gate3-status".*?</aside>',lambda _:banner,html,count=1,flags=re.S);assert n==1,p;p.write_text(html)
shutil.copy2(W/'REPORT.txt',outputs/'mpm-v03-repair-status-20261110.txt');shutil.copy2(W/'reports/repair_outcome.png',outputs/'mpm-v03-repair-outcome-20261110.png')
# Record the finalized evidence without including the hash inventory itself or caches.
hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(W.rglob('*')) if p.is_file() and 'cache' not in p.parts and '__pycache__' not in p.parts and p.name!='evidence_hashes.json'};save('evidence_hashes.json',hashes)
print(json.dumps({'updated':now,'status':state['status'],'report':str(W/'REPORT.txt'),'checklists_updated':2,'evidence_files':len(hashes)},indent=2))
