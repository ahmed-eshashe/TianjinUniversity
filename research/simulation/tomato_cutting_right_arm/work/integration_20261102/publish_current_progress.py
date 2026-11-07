from pathlib import Path
import json,datetime,runpy
r=Path(__file__).resolve().parents[2];o=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');p=o/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());b={x['id']:x for x in d['items']}
b[16]['progress']='Partial: moving-frame mixed-mode force, fracture potential and exact tangent pass independent checks on all 47 patches. Full-surface closure contact passes 18 geometry/force cases and 48 short gravity steps with replay. Partial-fracture/reclosure, blade eligibility and convergence remain open.'
b[16]['checks']=['PASS — independent mixed-loading, rigid-rotation and material tangent references','PASS — full-surface contact operator and short full-model gravity/replay component checks','OPEN — sustained dynamics, partial-fracture/reclosure, swept current-geometry eligibility and convergence']
b[20]['progress']='Partial: ten-second gravity test failed settling; missing cut-face contact allowed the cap to pass through the remainder. Checked volume updates fix a separate rounding defect. Replacement contact passes short motion checks; sustained support is not yet qualified.'
b[20]['checks']=['PASS — 25 remainder fixture nodes; cap nodes remain free','PASS — board force/potential positive control and checked-volume regression','FAILED — previous ten-second settling test; evidence retained','OPEN — long support with new full-surface contact and bounded load challenge']
d['updated']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['current_next_step']=16
d['integration'].update(objective_force_run='objective_force_20261102_05',objective_model_run='objective_model_20261102_01',embedding_contact_run='embedding_contact_20261102_04',short_contact_dynamics_run='contact_dynamics_20261102_01',failed_support_run='sustained_support_20261102_08');d['integration'].pop('support_run_in_progress',None);p.write_text(json.dumps(d,indent=2)+'\n')
(o/'integration-progress-20261102.txt').write_text('''INTEGRATION EVIDENCE — 2 November 2026

Fixed knife mount retained. Experimental tomato validation remains pending.
Counts unchanged: 18 scoped passes, four open milestones, ten upcoming.
No full separation or training is authorized by these component passes.

VERIFIED
- P0: versioned nonfracturing benchmark contract, nominal 10 mm end cap, predeclared numerical gates and unresolved hardware limits.
- mounted_contact_20261102_03: actual articulated fixed-mount robot with synthetic elastic coupon; 24 Newton/24 PhysX exchanges. Passive/driven response, off-center moment, contact clearing and exact loaded replay pass. Peak force 0.18178 N, maximum particle impulse residual 4.13e-8 N s. This is not a whole-tomato or whole-system work qualification.
- Material: seven host reference tests; 188 actual-patch loading/rotation cases; 282 explicit-force comparisons. objective_force_20261102_05 independently verifies force, incremental fracture potential and 54 colored tangent columns over all 47 patches. Maximum tangent error 1.85e-12 N/m. objective_model_20261102_01 passes four no-contact full-model rest steps/reset.
- checked_volume_20261102_02 reproduces old rounded-coordinate J=0.099994 failure and avoids it by checking actual stored trial coordinates. Original J>0.1 floor and bulk constitutive laws unchanged. 100,000 independent perturbed-cell roundoff checks show no false fast-path acceptance.
- embedding_contact_20261102_04: 18 whole-surface operator cases at 100/50/25 micrometre proxy resolutions. Rest/clear, compression, rotation, force/moment and virtual-work mapping pass. Current-geometry potential-gradient checks pass for normal, sliding and random perturbations. Collision proxies use positive barycentric embedding into unchanged mechanical cells. This is an explicit numerical regularization, not experimental calibration or full IPC qualification.
- contact_dynamics_20261102_01: actual 4,032-node model with objective material, unchanged bulk law and complete embedded self-contact; two 24-step gravity episodes pass short-state validity, zero damage, fixture checks and loaded replay. Only 0.01 simulated second per episode: no sustained-support claim.

FAILED / INCONCLUSIVE EVIDENCE RETAINED
- sustained_support_20261102_08 completed its first ten simulated seconds and failed the predeclared settling gate: maximum speed 0.01752 m/s versus 0.001 m/s. Cap nodes crossed through the remainder because that candidate lacked normal cut-face contact. The second episode was not run. This is not a pass.
- contact_dynamics_20261102_02 was intentionally stopped for profiling/optimization. It is incomplete evidence, not a dynamic pass or physical failure.
- Earlier diagnostic failures and all original evidence remain preserved.

CURRENT WORK / OPEN GATES
Independent verification of a cheaper positive solver preconditioner, then longer full-model contact/support runs. Material forces stay unchanged; solver iteration/convergence claims require new checks.
Still open: sustained support and bounded load challenge, partial/failed interface reclosure, current-deformation swept blade eligibility, whole-tomato mounted feedback with an independent work ledger, coupled cutting, and post-fracture loaded reset. Experimental validation stays pending. Full separation and training remain behind the roadmap gates.

Evidence root: '''+str(r/'runs/native')+'\nBenchmark: '+str(r/'runs/offline/integration_contract_20261102_01/contract.json')+'\n')
runpy.run_path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py')
print('Updated checklist with verified short checks and failed long support test; counts unchanged.')
