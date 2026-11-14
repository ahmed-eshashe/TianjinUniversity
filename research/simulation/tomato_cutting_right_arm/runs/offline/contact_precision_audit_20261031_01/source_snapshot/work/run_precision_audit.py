from pathlib import Path
import json,hashlib,shutil
from tomato_contact_precision_audit import replay_stationary_axis_contact
from tomato_contact_snapshot import _digest
root=Path.cwd(); source=root/'runs/native/analytic_force_reaction_20261031_02'
output=root/'runs/offline/contact_precision_audit_20261031_01';output.mkdir(exist_ok=False,parents=True)
results=[];pins={}
for path in sorted(source.glob('*_force_comparison.json')):
 name=path.name.removesuffix('_force_comparison.json');comparison=json.loads(path.read_text())
 cap=source/(name+'_capture.json')
 if not cap.exists():cap=root/'runs/native/analytic_collision_contacts_20261031_01'/(name+'_capture.json')
 envelope=json.loads(cap.read_text());assert _digest(envelope['payload'])==envelope['sha256']
 for p in (path,cap):
  pins[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
  dest=output/'input_snapshot'/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 fused=replay_stationary_axis_contact(envelope['payload'],comparison,fused=True)
 separate=replay_stationary_axis_contact(envelope['payload'],comparison,fused=False)
 assert fused['matches_recorded_force_exactly']
 results.append({'case':name,'capture_origin_run':cap.parent.name,'fused':fused,'separate':separate,
                 'original_geometry_comparison_error_n':comparison['force_error_n']})
assert len(results)==4
trans=next(x for x in results if x['case']=='transformed_face_inside')
assert not trans['separate']['matches_recorded_force_exactly']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
for name in ('rl/tomato_contact_precision_audit.py','rl/tests/test_tomato_contact_precision_audit.py','work/run_precision_audit.py'):
 p=root/name;pins[name]=hashlib.sha256(p.read_bytes()).hexdigest();dest=output/'source_snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
assessment={'result':'All four saved native contact forces reproduced exactly by independent rational binary32 replay with fused interpolation.',
 'native_launches':0,'mechanical_steps':0,'new_native_force_evaluations':0,'saved_contact_replays':4,
 'tests_passed':4,'cases':results,'source_and_input_sha256':pins,
 'finding':'Fused multiply-add interpolation explains the transformed-case discrepancy with the host geometric calculation. Fused and separately rounded interpolation differ by 7.450580596923828e-9 m along the contact normal.',
 'original_gate':'The original 1e-5 N geometry-to-native force comparison remains FAILED; no threshold or native physics changed.',
 'qualification':'This closes the arithmetic explanation, not a physical force/coupling acceptance gate.',
 'limits':['Native interpolation intermediates were not recorded; matching the force is replay evidence, not direct observation of GPU instruction execution.',
           'Replay uses recorded native rigid world point, axis-aligned unit normals, zero radius/margin and stationary frictionless fixtures only.',
           'Transformed input capture came from the preceding collision run; all compared corners, weights, normals and host interpolated state match the force-run record exactly.',
           'No general binary32 contact-error bound, translation invariance guarantee, moving-contact or real-blade qualification.'],
 'next_step':'Separate geometric accuracy and contact-law arithmetic checks in the diagnostic reference, then recheck their relationship before motion.',
 'original_pinned_sources_unchanged':True}
(output/'assessment.json').write_text(json.dumps(assessment,indent=2)+'\n')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
(out/'contact-force-precision-audit-20261031.json').write_text(json.dumps(assessment,indent=2)+'\n')
(out/'contact-force-precision-audit-20261031.txt').write_text('''Contact force precision audit — 31 October 2026

All four saved native forces are reproduced exactly by an independent float32 arithmetic replay using fused multiply-add interpolation. Four focused rounding tests passed. No native simulation or new native force evaluation was run.

In the transformed face fixture, separately rounded interpolation gives x = 0.10700002312660217 m, while fused interpolation gives x = 0.10700001567602158 m. This 7.45-nanometre change reproduces the observed native force of 1.749977469444275 N exactly when using its recorded rigid point and 1750 N/m stiffness. The host geometric reference uses higher-precision interpolation and a geometric surface calculation, so it is a different comparison.

The earlier 0.0000122334 N discrepancy is explained by these arithmetic choices. Its original 0.000010 N gate remains failed; no tolerance, material law or native solver was changed. The arithmetic explanation is complete, but physical force acceptance remains separate.

Scope: stationary, frictionless analytic box cases with axis-unit normals and zero particle radius/margin. The native rigid point is an input to the replay. GPU intermediates were not recorded, so this does not prove individual GPU instructions. The transformed state was reused from the earlier collision capture and checked against the force-run record. Original pinned project files are unchanged.

Next: separate geometry accuracy from contact-law arithmetic in the diagnostic, then compare both explicitly before moving on to the real-blade contact problem. Robot motion, two-way coupling and cutting remain unvalidated.
''')
print(assessment['result'])
