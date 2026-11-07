from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,shutil,runpy
r=Path(__file__).resolve().parents[2];o=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');p=o/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());b={x['id']:x for x in d['items']}
for name in ['isaac-sim-progress-checklist.json','integration-progress-20261102.txt']:
 old=o/name;backup=o/(old.stem+'-before-precision-20261102'+old.suffix)
 if old.exists() and not backup.exists():shutil.copy2(old,backup)
b[16]['progress']='Partial: material force, tangent, irreversible history and reclosure operators pass. Full-surface short motion/replay passes, but refinement exposed position-storage precision loss. A displacement-based correction passes force and geometry checks; motion accuracy is being evaluated.'
b[16]['checks']=['PASS — moving-frame forces, mixed loading and independent tangents','PASS — partial/failed interface reclosure, rejected-trial isolation and reset operators','PASS — complete contact surface and short replay component checks','PASS — isolated precision correction and full-model force/volume operators','OPEN — accurate sustained dynamics, contact refinement and swept blade eligibility']
b[20]['progress']='Partial: the previous ten-second test failed settling and let the cap cross the remainder. New closure contact and safer volume steps pass short tests. A numerical precision correction is under evaluation before the replacement long support test.'
b[22]['progress']='Partial: actual mounted-robot elastic-coupon reset/replay passes exactly. Material-history/reclosure operator reset also passes. Reset after a coupled tomato cut remains pending until cutting is available.'
d['updated']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat();d['current_next_step']=16
d['integration_focus']={'title':'Accuracy gate · support next','text':'The mounted robot reacts correctly to an elastic test piece. Material and contact operators pass; motion accuracy is being checked before the long tomato support test.'}
d['integration_checkpoints']=[{'status':'done','title':'Benchmark defined','detail':'Case, limits and open physical inputs recorded.'},{'status':'done','title':'Mounted robot contact','detail':'Elastic test piece: force response and replay pass.'},{'status':'done','title':'Material and damage operators','detail':'Rotation, mixed loading, history and reclosure pass.'},{'status':'done','title':'Full-surface contact operators','detail':'Geometry, force mapping and short replay pass.'},{'status':'done','title':'Precision fix: component checks','detail':'Gravity fixture and full-model force checks pass.'},{'status':'open','title':'Motion accuracy','detail':'Comparing time steps and solver iterations.'},{'status':'open','title':'Sustained target support','detail':'Replacement long gravity test awaits the accuracy check.'},{'status':'todo','title':'Whole-tomato robot work and reset','detail':'Follow after the integration gates pass.'}]
d['integration'].update(material_history_run='material_history_20261102_02',contact_operator_run='embedding_contact_20261102_07',world_storage_short_replay_run='contact_dynamics_20261102_06',precision_fixture_run='position_precision_20261102_01',precision_operator_run='relative_operator_20261102_03',accuracy_study='relative_sensitivity_20261102_01');p.write_text(json.dumps(d,indent=2)+'\n')
old=(o/'integration-progress-20261102-before-precision-20261102.txt').read_text()
current='''CURRENT STATUS — precision and accuracy gate, 2 November 2026

The fixed knife mount is retained. Experimental validation stays pending.
Milestone counts remain 18 scoped passes / four open / ten upcoming.
Component checks below do not qualify a complete tomato cut.

NEW VERIFIED RESULTS
- material_history_20261102_02: six full-registry prescribed loading/unloading/reclosure/reset cases. Committed history matches an independent reference; rejected failure trials do not damage it. Failed material still carries compression through contact. Zero mechanical steps; no performed cut.
- objective_gn_20261102_04: eight independent full-registry solver-block comparisons, including nonuniform deformation. These positive blocks are a solver preconditioner; the material forces are unchanged.
- embedding_contact_20261102_07: 18 contact operator fixtures, with full-versus-color-gated force/stiffness equivalence and finite-work checks. Safer motion bounds retain interaction coverage between queries.
- contact_dynamics_20261102_06: two 0.1-second gravity/replay component tests pass. Those tests used the earlier world-position storage. Later refinement exposed an accuracy limitation, so they do not close sustained support or cutting qualification.
- position_precision_20261102_01: 624 native freefall steps isolate velocity errors from world-position cancellation, without any material or contact forces. Displacement-based storage passes the analytic numerical budgets at three time steps.
- relative_operator_20261102_03: six full-model force/energy, geometry mapping and safe-volume operator checks pass with displacement storage and double-precision physical geometry. Original geometry, topology and material values are retained; no retuning. Zero mechanical steps. The complete collision surface stays enabled.
- Original material topology audit: no bulk spring, volume cell or skin triangle bridges the cut; two material components remain when all cohesive ties are removed. All 25 fixture nodes belong to the remainder. This is a topology check, not an executed separation.

ACCURACY WORK
The earlier world-position candidate did not converge cleanly under time-step refinement; finer settings also missed the independent impulse budget. These results are retained. The simple native gravity fixture reproduced the precision issue independently. The replacement stores deformation relative to the reference shape, evaluates physical geometry in double precision and refreshes contact queries during solver iterations. Its dynamic refinement study is being evaluated. No replacement long support pass is claimed.

OPEN GATES
Accurate longer dynamics, sustained gravity/support and load challenge, contact regularization refinement, swept eligibility on the deforming cut surface, whole-tomato mounted force/work reconciliation, and reset after coupled cutting. No full separation or training has started.

Evidence root: '''+str(r/'runs/native')+'\n\n--- EARLIER INTEGRATION EVIDENCE (preserved) ---\n'+old
(o/'integration-progress-20261102.txt').write_text(current)
runpy.run_path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py')
