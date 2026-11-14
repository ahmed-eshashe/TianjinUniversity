"""Freeze an image-only candidate after validation, before independent tests."""
from pathlib import Path
import argparse,json,hashlib,datetime
W=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--script',required=True);a.add_argument('--checkpoint',type=Path,required=True);a.add_argument('--validation-tag',required=True);a.add_argument('--image-report',type=Path,required=True);a.add_argument('--ablation',type=Path,required=True);a.add_argument('--override',type=Path);args=a.parse_args()
assert not (W/'FROZEN_CANDIDATE.json').exists(),'Preserve previous freeze'
manifest=json.loads((W/'generalization_curriculum_v01.json').read_text());episodes={x['id']:x for x in manifest['episodes']}
rows=json.loads((W/'datasets'/args.validation_tag/'results.json').read_text())
assert len(rows)==6 and all(x['success'] and not x['teacher'] and x['split']=='validation' for x in rows),rows
assert {(x['family'],x['face']) for x in rows}=={(f,face) for f in ['short','wide','medium'] for face in [0,180]}
contract_keys=['physics_hz','solver','velocity_iterations','hand_damping','control_hz','close_seconds','balance_timeout','lift','lift_seconds','hold_seconds','finger_extra_flex','thumb_effort','finger_effort','goal_force','thumb_force','grasp','neutral_start'];contracts=[]
for row in rows:
 p=W/'datasets'/args.validation_tag/row['id'];c=json.loads((p/'configuration.json').read_text())['args'];assert not c['teacher_target'] and c['teacher_along_shift']==0. and c['teacher_wrist_yaw_deg']==0.;contracts.append({k:c[k] for k in contract_keys})
assert all(c==contracts[0] for c in contracts),'Validation execution settings differ'
assert json.loads(args.image_report.read_text())['blank_image_rejected']
assert not json.loads((args.ablation/'visual_prediction.json').read_text())['accepted']
assert 'Visual grasp rejected before approach' in (args.ablation/'failure.txt').read_text()
assert all(x['phase']=='settle' for x in json.loads((args.ablation/'trajectory.json').read_text()))
for ep in episodes.values():
 if ep['split']=='test':assert not list((W/'datasets').glob('*/'+ep['id'])),'Independent test already consumed'
paths=[W/args.script,args.checkpoint.resolve(),W/'run_curriculum_v33.py',W/'generalization_curriculum_v01.json',W/'visual_grasp_v02.py',W/'grasp_vision_v02.py',W/'vision_policy.py',W/'grasp_calibration_v02.json',W/'hybrid_calibration_v01.json',W/'pickup_criteria.json',W/'contact_budget.py',W/'scene_config.json',W/'reports/pinch_geometry02.json',W/'reports/neutral_start.json',W/'grasp_targets_v02_candidate.json']
if args.override:paths.append(args.override.resolve())
if 'head_camera_readiness' in (W/args.script).read_text():paths.append(W/'head_camera_readiness.py')
import torch
trained=torch.load(args.checkpoint,map_location='cpu',weights_only=False);data=Path(trained['data']);meta=data/'metadata.json';labels=data/'labels.npz';assert hashlib.sha256(labels.read_bytes()).hexdigest()==trained['data_sha256'];paths += [meta,labels,Path(json.loads(meta.read_text())['targets'])]
paths += sorted(set(Path(ep['scene']) for ep in episodes.values()))
hashes={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
frozen=dict(created=datetime.datetime.now().astimezone().isoformat(),script=str((W/args.script).resolve()),checkpoint=str(args.checkpoint.resolve()),validation_tag=args.validation_tag,image_report=str(args.image_report.resolve()),ablation=str(args.ablation.resolve()),hashes=hashes,execution_contract=contracts[0],execution_override=str(args.override.resolve()) if args.override else None,test_gate=manifest['proposed_test_gate'],scope=manifest['scope'])
(W/'FROZEN_CANDIDATE.json').write_text(json.dumps(frozen,indent=2));print('Candidate frozen; independent evaluation may start.')
