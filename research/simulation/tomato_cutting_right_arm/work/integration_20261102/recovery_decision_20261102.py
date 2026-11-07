"""Read-only evidence consolidation; writes only a new recovery report and UI metadata."""
from pathlib import Path
import json, hashlib
import numpy as np
from scipy.spatial.transform import Rotation
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
W=R/'work/integration_20261102'
D=W/'recovery_decision_20261102'
D.mkdir(exist_ok=False)
def read(p): return json.loads((R/p).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
refs={
 'moving_audit':'runs/offline/joint_state_interface_pgs_work_20261102_01/measurements.json',
 'preload_work':'runs/offline/preload_contact_work_r128_20261102_02/measurements.json',
 'preload_refinement':'runs/offline/mounted_com_refinement_20261102_01/measurements.json',
 'preload_readback':'runs/offline/mounted_com_readback_r128_20261102_02/measurements.json',
 'parameters':'runs/native/robot_body_parameters_20261102_01/body_parameters.json',
 'parameters_supervisor':'runs/native/robot_body_parameters_20261102_01/supervisor_result.json',
 'moving_supervisor':'runs/native/joint_state_interface_pgs_20261102_01/supervisor_result.json',
 'preload_supervisor':'runs/native/mounted_target_com_r128_20261102_02/supervisor_result.json',
 'down_readback':'runs/offline/load_down_readback_20261102_01/measurements.json',
 'twist_readback':'runs/offline/load_twist_readback_20261102_01/measurements.json',
}
data={k:read(p)for k,p in refs.items()}
# Verify referenced inputs without rerunning successful simulation suites.
integrity={}
for name in ['moving_audit','preload_work','preload_refinement','preload_readback','down_readback','twist_readback']:
 h=data[name].get('source_sha256',{}); failures=[]
 for path,expected in h.items():
  p=Path(path)
  if not p.exists() or sha(p)!=expected: failures.append(path)
 integrity[name]={'checked':len(h),'mismatches':failures}
old=read('work/integration_20261102/preserved_source_recheck_contact_latest.json')
for group in ['fixed_mount_inputs','frozen_production','installed_dependencies']:
 failures=[]
 for item in old[group]['files']:
  p=Path(item['path'])
  if not p.exists()or sha(p)!=item['expected']: failures.append(str(p))
 integrity[group]={'checked':len(old[group]['files']),'mismatches_against_original':failures}
(D/'integrity.json').write_text(json.dumps(integrity,indent=2)+'\n')
# Conditional scale calculation, NOT a fitted damping coefficient or corrected pass.
run=R/'runs/native/joint_state_interface_pgs_20261102_01'
b=np.load(run/'robot_energy_binding_inputs.npz');I=b['inertia_com_link_axes'].astype(float)
scope=json.loads((run/'robot_energy_binding_scope.json').read_text());tool=scope['body_names'].index('MountedKnife')
m=json.loads((run/'input_manifest.json').read_text());dt=m['dt_s'];conditional=[]
for case in m['cases']:
 all_work=knife_work=0.
 for i in range(m['intervals_per_case']):
  p=run/f'{case}_interval{i}.npz';z=np.load(p)
  def spin(which):
   rot=Rotation.from_quat(z[f'robot_body_link_pose_{which}'][:,3:]).as_matrix()
   omega=np.einsum('bji,bj->bi',rot,z[f'robot_body_com_velocity_{which}'][:,3:])
   return .5*np.einsum('bi,bij,bj->b',omega,I,omega)
  k=.5*(spin('before')+spin('after'))
  all_work+=float(-2*.05*k.sum()*dt);knife_work+=float(-2*.05*k[tool]*dt)
 conditional.append({'case':case,'conditional_all_bodies_angular_drag_work_j':all_work,'known_knife_coefficient_only_angular_drag_work_j':knife_work})
unknown=[b['body']for b in data['parameters']['bodies']if b['properties']['GetAngularDampingAttr']['value']is None]
report={
 'decision':'Moving mounted-contact qualification blocked; preserve qualified components.',
 'native_runs_launched_in_recovery':0,
 'damping_test_decision':'Not justified as an independent causal test within the recovery scope: effective damping remains unresolved for 45 bodies. A decay fit would confound numerical/constraint losses with drag; a separately controlled identification campaign would exceed this directive.',
 'damping_hypothesis':'Unresolved; conditional scale compatible with some pJ residuals is not validation.',
 'unknown_angular_damping_bodies':unknown,
 'conditional_estimates':conditional,
 'conditional_scope':'Trapezoidal angular kinetic energy times -2*0.05*dt. Hypothetical scalar drag, not a validated installed-runtime discrete force law. No coefficients fitted, no ledger corrected, no verdict changed.',
 'original_moving_verdict':data['moving_audit']['moving_measurement_passed'],
 'refs':{k:str(R/p)for k,p in refs.items()},
 'source_sha256':{str(R/p):sha(R/p)for p in refs.values()},
 'supervisor_cleanup':{k:data[k].get('remaining_live_group_members')for k in ['parameters_supervisor','moving_supervisor','preload_supervisor']},
 'integrity':integrity,
}
(D/'decision.json').write_text(json.dumps(report,indent=2)+'\n')
a=data['moving_audit'];up=next(c for c in a['cases']if c['case']=='up_profile');clear=next(c for c in a['cases']if c['case']=='up_clear')
rows=[('Per-step knife force residual',a['maximum_independent_errors']['knife_force_balance_n'],'N',1e-6),('Per-step knife moment residual',a['maximum_independent_errors']['knife_moment_balance_nm'],'Nm',1e-7),('Up-profile cumulative work residual',up['maximum_robot_energy_work_defect_j'],'J',.01*up['contact_work_scale_j']+1e-14),('Up-clear cumulative work residual',clear['maximum_robot_energy_work_defect_j'],'J',1e-6*clear['initial_robot_kinetic_energy_j']+1e-15)]
text='''INTEGRATION RECOVERY DECISION — 2 November 2026

DECISION
Moving mounted-blade qualification is blocked. Completed components remain useful.
No new native simulation was launched. No physical parameters, thresholds or historical verdicts were changed. Fixed mount retained; experimental validation pending; no cutting or training started.

VERIFIED SCOPE
- Benchmark/evaluator: the existing curved nominal 10 mm end-cap contract remains the reference, not a uniform slice.
- Material/frame/contact/history operators and prepared damaged states are component checks; accepted live coupled fracture remains unqualified.
- Saved support evidence covers two synchronized ten-second holds and the specific 0.01 N force/twist pulses, not the full cutting-load envelope.
- Stationary preload: protected 4096-interval run, independent readback and finest-pair refinement passed. Maximum pose change is exactly zero at this scale. Its 0.77% energy result does not qualify a moving blade.
- Moving robot-only known-wrench replay completed 192 steps. Independent channel reconstruction and pose-versus-velocity work pass, but force/moment and some energy checks fail. Worker completion is not qualification.

UNRESOLVED MEASUREMENTS (original gates retained)
'''
for label,value,unit,budget in rows:text+=f'- {label}: {value:.9g} {unit}; budget {budget:.9g} {unit}; FAIL.\n'
text+='''Force readout rounding allowance adds at most 2.235 microN to the original 1 microN limit; the approximately 15 microN maximum still fails. This is a Newton–Euler balance residual, not a measured contact-force peak.
Loaded robot-only contact work is about 1.12 nJ; its 1% budget is about 11.2 pJ. Clear-case initial kinetic energy is 9.24 microJ; its one-part-per-million budget is about 9.24 pJ. Gravity and motor work each approach 80 microJ, so this is a demanding subtraction of large terms. The existing traces do not establish that these full-ledger precision requirements are achievable. That is a measurement limitation to resolve, not permission to increase limits.
Cumulative knife linear impulse residuals are 0.196–0.367 nNs over 0.833 ms, below the prior 1 nNs impulse bound; this scoped observation cannot erase failing per-step force requirements or establish moving contact. Signed cancellation must also be checked in any future windowed measurement.

DAMPING ASSESSMENT AND RUN DECISION
The source capture establishes angular damping 0.0500000007/s for the mounted knife. Forty-five robot bodies have absent API/property values; these are UNKNOWN effective runtime coefficients, not zero. Joint-drive gains being zero does not resolve body drag. The capture took zero physical steps and is not a force calibration.
The conditional all-body 0.05/s estimate below is a scale check only. It uses measured angular kinetic energies and an assumed scalar drag model, excludes possible other loss terms and does not establish the installed solver's discrete force law. The known knife coefficient alone does not close the full-robot ledger.
'''
for c in conditional:text+=f"- {c['case']}: hypothetical all-body drag {c['conditional_all_bodies_angular_drag_work_j']:.6g} J; knife-only coefficient contribution {c['known_knife_coefficient_only_angular_drag_work_j']:.6g} J.\n"
text+='''Damping would remove energy under this model, with scale of order 10 pJ per short episode. Agreement in order of magnitude with an observed negative residual does not identify its cause. An unforced decay run with unknown effective coefficients would mix physical damping, constraint losses and numerical errors. Establishing them independently requires another identification branch, which section 9 disallows. Therefore no new native invocation is justified here. The hypothesis remains unresolved; no corrected ledger or pass is issued.

MEASUREMENT CONTRACT REVIEW
Physical stop limits (force/moment/penetration/volume/domain bounds) remain distinct from readout precision and convergence targets. A future force controller needs a stated sampling period, latency and worst-case transient load resolution. A block impulse can assess momentum transfer; it cannot certify unobserved peaks. Accumulated work is needed for the cutting energy evaluator and requires explicit actuator/support/damping terms. Pose-work agreement alone does not prove whole-system conservation.
The original per-step force gate still fails, including its declared floating-point rounding allowance. No windowed sensor contract is adopted. A prospective alternative must specify window, latency, cumulative and within-window residual limits, positive/negative/clear controls and independent held-out loads before results, with uncertainty derived independently rather than fitted to these failures.

RECOMMENDATION FOR USER DECISION — NOT IMPLEMENTED
Temporarily separate the next research deliverables:
1. A robot-only force-transfer benchmark with explicit measurement resolution and bandwidth.
2. A prescribed-blade nonfracturing whole-target material experiment, retaining board/support, physical contact and existing stop criteria.
These establish separate capabilities, not two-way robot cutting. Do not carry this scoped result into shallow cuts or claim robot cutting qualification. Experimental validation and loaded/post-cut reset remain pending. Returning to cutting requires a defensible mounted-moving-contact qualification.
Proposed finite next package after user agrees to this scope: one frozen measurement/experiment specification, one serialized robot-only held-out load run, and one prescribed-blade nonfracturing run; no solver sweep or material retuning. Budget at most two native invocations, provisionally 20 minutes robot-only and 30 minutes material wall time including setup/cleanup; shorten physical duration or return incomplete if needed, never relax gates to meet time. These are ceilings rather than throughput forecasts; confirm costs from the saved timed runs before launch. Exit is two reproducible component verdicts (pass, fail or incomplete) and a clear statement of which original gates remain open. Stop after this package and review; a failure does not authorize another branch.

EVIDENCE AND PRESERVATION
'''
for k,p in report['refs'].items():text+=f'{k}: {p}\n'
text+=f'Integrity details and conditional calculation: {D}\n'
text+='All old evidence remains in place. Current supervisor records report no remaining owned live group members. Hash rechecks are recorded in integrity.json; the startup guard is the documented intentional change against the original fixed-mount wrapper set. No historical failed audit is relabelled.\n'
(D/'INTEGRATION_RECOVERY_DECISION_20261102.txt').write_text(text)
print(json.dumps({'report':str(D/'INTEGRATION_RECOVERY_DECISION_20261102.txt'),'integrity':integrity,'conditional':conditional},indent=2))
