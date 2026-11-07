from pathlib import Path
import json,hashlib,ast
root=Path.cwd();r=root/'runs/native/analytic_force_separated_reference_20261031_02'
m=json.loads((r/'analytic_force_measurements.json').read_text());supervisor=json.loads((r/'supervisor_result.json').read_text());assert supervisor['passed']
rows=[row for c in m['cases'] for row in c['records']];assert len(rows)==4
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
def native_ast(path):
 return ast.dump(next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_native'),include_attributes=False)
assert native_ast(root/'rl/tomato_analytic_force_worker.py')==native_ast(root/'runs/native/analytic_force_reaction_20261031_02/source_snapshot/rl/tomato_analytic_force_worker.py')
metrics={'exact_arithmetic_matches':sum(x['separated_checks']['arithmetic_passed'] for x in rows),
 'max_penetration_error_m':max(x['separated_checks']['penetration_error_m'] for x in rows),
 'max_surface_error_m':max(x['separated_checks']['surface_error_m'] for x in rows),
 'max_normal_error':max(x['separated_checks']['normal_error'] for x in rows),
 'max_reconstructed_reaction_error_n':max(x['reaction_error_n'] for x in rows),
 'max_reconstructed_moment_error_nm':max(x['moment_error_nm'] for x in rows),
 'max_hessian_error_n_m':max(x['hessian_error_n_m'] for x in rows)}
a={'result':'PASS: separated stationary analytic geometry and force-arithmetic references, version 2.',
 'reference_change':'Replaced one combined geometry-to-force acceptance test with explicit geometry accuracy and exact arithmetic replay gates. This is a new diagnostic policy, not a claim that the earlier policy passed.',
 'geometry_policy':{'surface_and_penetration_m':1e-7,'normal_vector_error':1e-6,'provenance':'Existing analytic-box contact geometry tolerances.'},
 'arithmetic_policy':'Exact equality to rational binary32 fused-interpolation replay, using independently mixed stiffness and recorded rigid point.',
 'reaction_hessian_policy':{'reaction_n':1e-5,'moment_nm':1e-6,'hessian_n_m':1e-4},
 'historical_geometry_force_gate_passed':m['historical_geometry_force_gate_passed'],
 'historical_failure_preserved':'runs/native/analytic_force_reaction_20261031_01 and _02',
 'metrics':metrics,'native_attempts_this_step':2,'first_attempt':'Stopped on tuple/list representation mismatch before force comparison; preserved. Reader normalized sequence representation; regression test added.',
 'passing_run_cases':6,'passing_run_force_evaluations':4,'mechanical_steps':0,'focused_tests_passed':25,
 'native_force_kernel_unchanged':True,'original_pinned_sources_unchanged':True,
 'limits':['Stationary, frictionless analytic boxes and axis-unit normals only; no dynamic qualification.',
 'Reconstructed opposite force and COM moment are bookkeeping, not independently measured body response.',
 'No real-blade mesh, two-way robot coupling, cutting or training validation.',
 'The replay uses the recorded native rigid point; geometry is separately checked against the independent box surface.'],
 'next_step':'Qualify the real-blade full-surface contact path: choose and validate a solver-integrated replacement for the failing thin-feature SDF path.',
 'supervisor':supervisor}
(r/'diagnostic_assessment.json').write_text(json.dumps(a,indent=2)+'\n')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');(out/'analytic-force-reference-recheck-20261031.json').write_text(json.dumps(a,indent=2)+'\n')
(out/'analytic-force-reference-recheck-20261031.txt').write_text('''Analytic force reference recheck — 31 October 2026

PASS under the revised, explicitly separated reference policy.

All six stationary analytic-box fixtures passed. Four positive contacts matched the independent binary32 arithmetic replay exactly; two clear fixtures generated no contacts. Geometry was checked separately using the existing 1e-7 m surface/penetration and 1e-6 normal-vector tolerances. Reconstructed reaction, moment and contact stiffness checks also passed.

Maximum penetration discrepancy: 6.99e-9 m. Maximum rigid-point surface error: 1.16e-9 m. Normal and contact-Hessian errors were zero. The passing run took 3.75 seconds, retained 25.59 GB available RAM and 7.68 GB free GPU memory, and left no owned worker processes. Zero mechanical integration steps occurred.

The diagnostic policy changed: geometry accuracy and exact force arithmetic are now independent checks. The old 1e-5 N geometry-to-native force comparison remains failed and is still reported as such. Its historical evidence was not changed. The native force evaluation kernel, physical parameters and original pinned project files are unchanged.

Two bounded attempts were made this step. The first stopped on tuple/list representation in the reference reader; that compatibility issue was fixed and covered by a regression test. The second passed. All 25 focused reference, geometry and guard tests passed.

Scope: stationary frictionless analytic boxes with axis-unit normals. The body reaction is reconstructed from the native force, not independently measured through body motion. This does not qualify the real blade, dynamic coupling or cutting.

Checklist item 11 is complete. Next: resolve the real-blade full-surface contact path (item 12).
''')
print(json.dumps(metrics,indent=2))
