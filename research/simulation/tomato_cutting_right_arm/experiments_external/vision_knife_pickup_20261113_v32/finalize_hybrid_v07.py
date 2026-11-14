"""Publish completed evidence, without promoting narrow tests to broad coverage."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

W = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(W / 'audit_current_pickup.py')], check=True)
r = json.loads((W / 'reports/hybrid_v07_campaign.json').read_text())
assert r['limited_curriculum_physical_gate_passed']
blank = json.loads((W / 'reports/hybrid_v07_blank_guard.json').read_text())
assert blank['prediction_rejected'] and blank['no_approach']
sources = json.loads((W / 'preserved_sources.json').read_text())
preserved = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in sources.items()}
assert all(preserved.values())
(W / 'reports/hybrid_source_preservation.json').write_text(json.dumps(preserved, indent=2))
tests = [x for x in r['rows'] if x['dataset'] == 'hybrid_v07_test']
failed_tests = [x['id'] for x in tests if not x['success']]
geometry = [x for x in r['rows'] if x['dataset'].startswith('hybrid_v07_geometry_')]
assert len(geometry) == 2 and all(x['complete'] for x in geometry)
rest_path = W / 'datasets/rest_pose_probe_v01/opposite_face_000'
rest = None
if (rest_path / 'result.json').exists():
    rest = dict(success=json.loads((rest_path / 'result.json').read_text())['success'])
elif (rest_path / 'failure.txt').exists():
    rest = dict(success=False, failure=(rest_path / 'failure.txt').read_text().splitlines()[-1])
now = datetime.datetime.now().astimezone().isoformat()
summary = (f"First vision-guided pickup passed: {r['validation_successes']}/3 validation and "
           f"{r['test_successes']}/8 fresh tests. The head camera learns the handle position/orientation; "
           "engineered motion closes the fingers and lifts with real contact, no attachment. "
           "Short knife and bounded flat-rest placements only. Blank images rejected before approach.")
geometry_notes = []
for x in geometry:
    label = 'wider handle' if x['dataset'].endswith('_compact') else 'longer/heavier blade'
    if x['success']:
        note = '1/1 passed'
    elif 'Opposed handle support lost' in x.get('failure', ''):
        note = '0/1; stopped before lift because grip stability was not sustained'
    elif x.get('min_height_m', 1.) <= .003:
        note = f"0/1; whole-tool clearance {x['min_height_m'] * 1000:.2f} mm, below the 3 mm requirement"
    else:
        note = '0/1; no sustained unsupported hold'
    geometry_notes.append(label + ': ' + note)
geometry_summary = '; '.join(geometry_notes)
rest_summary = ('not run' if rest is None else 'passed one opposite-face probe' if rest['success'] else
                'opposite-face probe failed; no sustained unsupported hold')
if rest and not rest['success'] and 'Contact stop' in rest.get('failure', ''):
    stop = json.loads((rest_path / 'stop_state.json').read_text())
    peak = max(x[-1] for x in stop['bad'] if isinstance(x[-1], (int, float)))
    rest_summary = f'opposite-face probe stopped at {peak:.2f} N contact load (50 N limit)'
status = json.loads((W / 'STATUS.json').read_text())
status.update(updated_local=now, status='first_vision_guided_pickup_qualified_limited_scope',
              active_simulation=False, active_training=False, latest_result=summary,
              hybrid_validation_passes=r['validation_successes'], hybrid_validation_attempts=3,
              hybrid_test_passes=r['test_successes'], hybrid_test_attempts=8,
              limited_curriculum_qualified=True, generalization_qualified=False,
              full_motion_policy_qualified=False, learned_pickup_verified=True,
              current_candidate='hybrid_pickup_v07.py', original_sources_unchanged=True,
              real_grasp_scope='Short knife; learned visual grasp target and engineered contact-guided pickup.',
              heldout_geometry_probes=geometry_summary, rest_pose_probe=rest_summary,
              report=str(W / 'reports/HYBRID_V07_RESULT.txt'))
(W / 'STATUS.json').write_text(json.dumps(status, indent=2))
p = Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/learning-roadmap.json')
d = json.loads(p.read_text())
s = next(x for x in d['stages'] if x['id'] == 10)
s['phase'] = 'First vision-guided pickup verified; broader shapes and resting poses remain open'
items = {x['id']: x for x in s['items']}
items['10.6'].update(text='Train and verify learned visual grasp selection with the contact pickup controller.',
                     status='complete', evidence=summary)
items['10.4'].update(status='in_progress', evidence='Short knife flat-rest curriculum verified. Held-out probes: ' + geometry_summary + '. Rest pose: ' + rest_summary + '. These isolated probes do not establish broad coverage.')
items['10.5'].update(status='in_progress', evidence='Audited one-time resets, image-only grasp estimation, contact outcomes and blank-image rejection. Native headless runs take about four minutes per pickup on this laptop. Large-scale RL throughput remains unqualified.')
items['10.7'].update(status='in_progress', evidence='Independent placement tests completed for the initial scope; held-out geometry probes: ' + geometry_summary + '. Wider board coverage, knife families, resting poses and occlusion still require independent tests.')
items['10.8'].update(status='pending', evidence='Verified native Isaac Sim pickups and rendered images saved. A live window for the user has not yet been opened for the qualified v07 controller.')
d['updated'] = now
d['latest_progress']['learning'] = summary
tmp = p.with_suffix('.json.tmp'); tmp.write_text(json.dumps(d, indent=2)); tmp.replace(p)
slips = [x['slip_m'] * 1000 for x in tests if x['success']]
report = f'''VISION-GUIDED KNIFE PICKUP — VERIFIED FIRST VERSION
Updated: {now}

{summary}

Evidence
- Validation: {r['validation_successes']}/3; fresh independent tests: {r['test_successes']}/8.
- Failed test placements (retained, never silently retried): {failed_tests}.
- Test success Wilson 95% interval: {r['wilson_95_interval']}; eight tests are a small sample.
- Maximum final relative slip among successful test holds: {max(slips):.3f} mm.
- Three seconds continuous unsupported hold; includes the latter part of lifting.
- Whole knife clear of board; opposed thumb/finger contact; unchanged load/blade/joint stops.
- Live blank-image check rejected before approach; no ground-truth fallback.
- Held-out geometry probes: {geometry_summary}.
- Other resting pose: {rest_summary}.

What is learned
Two handle landmarks from actual robot-head RGB-D. Fixed calibration and a flat-rest
height prior convert these to grasp position/yaw. No sampled knife pose or reset
parameters enter the predictor or its grasp target.

What remains engineered
Approach, descent, contact-guided finger closure, supported pinch balancing, lift,
and hold. Simulated contact sensing informs grip readiness and safety checks.
This is not learned full motion, an RL policy, or hardware-ready control.

Scope and limits
The main gate used a 305 mm / 175 g shortened knife, original handle, bounded planar
placement/yaw. Single variant/rest probes do not establish any-knife/any-pose ability.
Friction, mass distribution and finger/contact models remain uncalibrated to hardware.
The next phase expands real-contact demonstrations and visual grasp training to wider
positions, geometry and stable resting faces, with fresh held-out tests. Full motion
learning and cutting-grip adjustment remain separate later skills.

Evidence preservation
Earlier full-motion students and failed v01-v06 controllers remain in their original
folders. The earlier v03 test gate failed 2/4 and is not counted in this fresh test set.
All frozen v07 source/checkpoint/asset/criteria hashes and four monitored original
project source hashes match. Changes are isolated to this experiment and checklist.

Documentation correction
The frozen contract's older 'transition' field says the holding ramp begins at lift.
The actual frozen v07 source and its 'closing_sequence' field correctly implement
the 1.5 s supported balancing phase BEFORE lifting. No evaluation code was changed.

Detailed evidence: reports/hybrid_v07_campaign.json; reports/hybrid_v07_blank_guard.json;
datasets/hybrid_v07_validation; datasets/hybrid_v07_test; HYBRID_NOTES.txt.
'''
(W / 'reports/HYBRID_V07_RESULT.txt').write_text(report)
(W / 'README.txt').write_text('Head-vision knife pickup — isolated v32\n\n' + summary + '\n\nSee reports/HYBRID_V07_RESULT.txt and STATUS.json for current results. Full-motion learning and broad geometry/rest-pose qualification remain open. Earlier decisions and failures are preserved; DECISION_BRIEF.txt is historical. The original cutting setup is unchanged.\n')
print(summary)
print(geometry_summary)
print(rest_summary)
