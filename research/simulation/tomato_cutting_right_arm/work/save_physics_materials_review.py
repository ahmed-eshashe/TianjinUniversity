from pathlib import Path
import json,hashlib,shutil
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=read(R/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json')['source_sha256']
assert all(sha(R/n)==h for n,h in frozen.items())
installed={n:h for n,h in read(R/'runs/native/bent_replay_20261101_01/source_integrity.json')['sha256'].items() if not n.startswith(str(R))}
assert all(sha(Path(n))==h for n,h in installed.items())
cases=[('material_operator_20261101_04','material_operator_measurements.json'),('material_coupon_20261101_03','material_coupon_measurements.json'),('group_material_20261101_02','group_material_measurements.json'),('material_contact_20261101_01','material_contact_measurements.json'),('volume_coupon_20261101_04','volumetric_coupon_measurements.json')]
reports={};provenance={}
for name,measurement in cases:
 run=R/'runs/native'/name;s=read(run/'supervisor_result.json');assert s['passed'] and s['child_exit_code']==0 and not s['remaining_live_group_members']
 manifest=read(run/'launch_manifest.json');pins=manifest['source_sha256'];matches={}
 for n,h in pins.items():
  p=Path(n);matches[n]=sha(p)==h
  # Additive supervisor modes changed between launches. Preserve launch-time hashes separately.
  if not matches[n]:assert p.name=='tomato_isaac_startup_guard.py', (name,n)
 snap=run/'qualification_source_snapshot';snap.mkdir(exist_ok=True)
 for i,n in enumerate(pins):
  p=Path(n);dest=snap/str(i)/p.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
 integrity=dict(launch_time_sha256=pins,current_snapshot_sha256={n:sha(Path(n)) for n in pins},matches_launch_time=matches,supervisor_note='Only additional diagnostic modes were added between earlier launches; mismatching current supervisor is not claimed as the launch-time source.',original_frozen_sources_unchanged=True,pinned_installed_dependencies_unchanged=True)
 (run/'qualification_source_integrity.json').write_text(json.dumps(integrity,indent=2)+'\n')
 reports[name]=dict(supervisor=s,measurements=read(run/measurement));provenance[name]=integrity
energy=read(R/'work/coupled_energy_audit.json');ledger=read(R/'work/closed_coupled_energy_ledger.json');reference=read(R/'work/material_reference_assessment.json');figure=read(R/'work/tomato_digitized_reference_assessment.json')
report=dict(date='2026-11-01',section_complete=False,small_coupon_milestone_passed=True,native_runs=reports,source_provenance=provenance,coupled_work_audit=energy,closed_energy_ledger=ledger,published_reference=reference,provisional_figure_assessment=figure,host_tests_passed=33,original_frozen_sources_unchanged=True,pinned_installed_dependencies_unchanged=True,remaining=['Target-model two-way coupling qualification (item 15).','Full target-model cohesive integration and a suitable moving material frame (item 16).','Matched specimen/protocol and independent numeric experimental tomato validation (item 17).'],recommendation='Use the published tomato figure provisionally; do not substitute simulated DiSECt fruit data for experimental validation. Obtain raw data/specimen details or collect matched trials before closing item 17.')
name='physics-materials-review-20261101'
(O/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
text='''Physics and materials review — 1 November 2026

The numerical component checks below pass. The full section is NOT complete: production-model coupling, cohesive integration and independent experimental material validation remain open. These checks use synthetic parameters and small diagnostic geometries. Existing frozen production files and pinned installed dependencies are unchanged.

Coupled work and energy (item 15)
The saved actual Newton/PhysX bent-chain exchange passes the work audit and a closed contact-potential/kinetic-energy ledger in identity and 90-degree yaw orientations. Numerical losses, partitioned coupling defects and residuals are recorded separately. The residuals are approximately 3.83e-9 J and 2.33e-9 J, respectively; neither partition defects nor numerical losses are hidden as material fracture. A deliberately reversed particle force fails the regression check. This extends the previous minimal joint exchange/reset/replay qualification; it does not qualify the full robot and cutting model.

Native cohesive operator (item 16)
A diagnostic SolverVBD extension adds cohesive force and a consistent softening diagonal Hessian to the installed solver's particle iteration. Installed source is untouched. Host AST comparison verifies that removing the one cohesive hook reproduces the original iteration. Six native implicit cases cover elastic response, softening, unloading, complete failure, ineligible loading and normal compression, with independent scalar implicit references. Seven constitutive probes check forces/Hessians and refusal of unsupported compression with shear. History remains unchanged during trial solves and is committed explicitly. Position and velocity gates remain 1e-7 m and 2e-5 m/s; finite-difference diagonal-block comparison uses 1e-3 N/m.

A second native extension supports multiple quadrature points sharing ONE patch energy and damage history. The loading tangent includes shared-history derivatives. A two-point implicit case checks the coupled nonlinear equilibrium; four constitutive probes check force and diagonal Hessian. Explicit patch-clique coloring prevents simultaneous updates of coupled nodes. Two further cases generate actual Newton box contact to enable damage, or verify that absent contact leaves damage frozen. These are fixed-frame synthetic diagnostics; general rotating-frame behavior, production registries and real-blade integration remain unqualified.

Small coupon (item 18: PASS within this stated scope)
A one-pair interface coupon traverses 401 controlled opening states twice, before and after reset. Integrated work is 0.000199998601 J against a 0.0002 J budget. Complete failure leaves zero cohesive force. Independent release, actual Newton reclosure, no healing, cleared-contact control and exact opening replay pass.

A separate solid coupon contains two tetrahedra, eight boundary triangles and three equally weighted interface pairs with one shared patch. Bulk Neo-Hookean parameters lambda=mu=12000 Pa, node masses and Gc=80 J/m² are synthetic. Prescribed rigid-piece opening samples 401 constitutive states, giving work 0.003999972401 J against a 0.004 J shared fracture budget (relative error 6.90e-6). Three native steps test independent release, explicit reclosure using native mesh self-contact, and a clear control. Release velocity error is 5.42e-7 m/s. Reclosure records 18 vertex/triangle candidates, positive right-piece mean velocity 0.0460 m/s, minimum face gap 7.54e-5 m and volume ratios 1.0/0.9974. Damage remains complete. Clear-control velocity error is 1.26e-8 m/s with no candidates. Buffers are checked for saturation. Candidate counts are not unique physical contact counts; the triangle-to-vertex reverse array is not recorded by this backend. Opening is prescribed, not a freely evolving crack or actual knife cut. This is a coarse two-element check; no mesh convergence, objective material-frame or whole-tomato claim follows.

Published tomato reference and recommended route (item 17: OPEN)
Use Jamdagni and Jia (2019), Robotic Cutting of Solids Based on Fracture Mechanics and FEM, as a provisional experimental benchmark:
https://faculty.sites.iastate.edu/jia/files/inline-files/IROS19.pdf
The paper supplies a plotted tomato cutting experiment, but numeric instrument data and specimen scan were not obtained. Its printed modulus unit is dimensionally inconsistent for a three-dimensional Young modulus. The model's current synthetic coefficients have not been calibrated. A vector-path extraction of the measured tomato trace gives an approximate 48.8 N peak near 15.6 mm depth. The declared extraction resolution corresponds to roughly 0.13 N and 0.079 mm; these are extraction assumptions, not biological uncertainty. A descriptive curve fit is not our native material model. Alternating points from the same trace cannot provide independent experimental validation.

DiSECt's public dataset is generated in Ansys LS-DYNA for apple, potato and cucumber. It is useful for simulation comparison, not experimental tomato validation:
https://github.com/NVlabs/DiSECt/blob/main/dataset/README.md
The inspected repository inventory is retained internally. No author was contacted. No tomato material parameters were retuned to force a passing comparison.

For a defensible validation gate, obtain numeric force histories plus specimen geometry and loading protocol, resolve tissue scope and units, calibrate on declared data, and test a separate specimen or loading condition. Record both measurement uncertainty and model discrepancy. The provisional literature comparison supports progress while this evidence is missing, but does not close item 17.

Verification and preserved failures
Five final native diagnostic runs pass with exit code zero, no owned live processes and no monitoring errors. Resource protections and the 180-second independent watchdog remain in force. Thirty-three focused host tests pass: six input/count contracts, sixteen cohesive tests, two energy regressions and nine supervisor tests. Earlier failed attempts remain preserved, including observer/serialization issues in the solid coupon; final run 04 fixes serialization without relaxing a mechanical gate. Each final run retains measurements, launch hashes and a current source snapshot. Earlier launch-time supervisor hashes differ only because additional diagnostic modes were added later; the current snapshot is explicitly distinguished from the recorded launch-time source.

Evidence is retained under /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native:
'''
text+=''.join('  '+x+'\n' for x,_ in cases)
text+='\nThe accompanying JSON includes measurements, resource summaries, hashes, reference limitations and the remaining section gates.\n'
(O/(name+'.txt')).write_text(text)
(O/'tomato-reference-provisional-20261101.json').write_text(json.dumps(dict(reference=reference,figure_assessment=figure,recommended_route=report['recommendation']),indent=2)+'\n')
p=O/'isaac-sim-progress-checklist.json';d=read(p);d['current_next_step']=16
for i in d['items']:
 if 15<=i['id']<=18:i['evidence']=name+'.txt'
 if i['id']==17:i['progress']='Recommended route: published tomato curve as a provisional benchmark. Approximate peak extracted; no native material calibration or independent experimental validation. Numeric data and specimen/protocol matching are still needed.'
 if i['id']==18:
  i['status']='done';i['progress']='Synthetic interface and two-tetrahedron coupons pass fracture work, independent release, irreversible failure, reclosure and cleared-contact controls. Interface opening reset/replay matches exactly. Prescribed opening; no real blade or whole-tomato validation.'
  i['checks']=['PASS — shared fracture budget and irreversible failure','PASS — independent release and native mesh reclosure','PASS — cleared contact and interface reset/replay']
d['counts']={k:sum(i['status']==k for i in d['items']) for k in ['done','open','todo']};p.write_text(json.dumps(d,indent=2)+'\n')
(O/'isaac-sim-progress-checklist.txt').write_text('Updated 1 November 2026. Counts are milestones, not time estimates.\n\n'+''.join(f"{i['id']:02} [{i['status'].upper()}] {i['title']}\n"+(i.get('progress','')+'\n' if i.get('progress') else '') for i in d['items'])+'\nEvidence: '+name+'.txt\n')
print(json.dumps(dict(native_runs=5,host_tests=33,counts=d['counts'],section_complete=False)))
