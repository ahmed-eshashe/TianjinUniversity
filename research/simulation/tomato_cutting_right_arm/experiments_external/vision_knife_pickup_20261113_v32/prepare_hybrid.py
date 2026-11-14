from pathlib import Path
import json,hashlib,datetime
import numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent
c=json.loads((W/'scene_config.json').read_text());cam=json.loads((W/'runs/camera01/result.json').read_text());g=json.loads((W/'reports/pinch_geometry02.json').read_text())
def mat(p):
 t=np.eye(4);t[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();t[:3,3]=p[:3];return t
nominal=mat(min(json.loads((W/'runs/pickup18_control20/trajectory.json').read_text()),key=lambda r:abs(r['sim_s']-.5))['knife_pose'])
landmarks=np.array([[-.13,.0076461609,.001586524],[-.045,.0076461609,.001586524]])
cal=dict(camera_world_matrix=c['camera_world_matrix'],intrinsics=cam['intrinsics'],nominal_landmarks_world=(landmarks@nominal[:3,:3].T+nominal[:3,3]).tolist(),nominal_hand_target_world=(mat(cam['knife_pose'])@np.array(g['hand_from_knife'])).tolist(),board_world_bounds=c['board_world_bounds'],scope='Fixed head camera and nominal flat-rest height prior; no per-episode truth.')
assert not (W/'hybrid_calibration_v01.json').exists()
(W/'hybrid_calibration_v01.json').write_text(json.dumps(cal,indent=2))
s=(W/'physical_pickup.py').read_text()
s=s.replace('Contact-driven pickup feasibility from a reset pregrasp. State-informed teacher; no learning claim.','Learned head RGB-D grasp targets with a tested engineered contact pickup controller.')
s=s.replace("args=a.parse_args();out=args.output", "a.add_argument('--visual-checkpoint',type=Path,default=W/'policies/handle_vision_v01/best.pt');args=a.parse_args();assert args.neutral_start and args.joint_space_approach and args.control_hz==20 and not args.policy;out=args.output")
s=s.replace('enable_cameras=bool(args.render or args.record_demo or args.policy)','enable_cameras=True')
s=s.replace("kin=ArmKinematics(sim.stage);K=matrix(pose);contact_T=K@relative;", "kin=ArmKinematics(sim.stage);contact_T=np.array(json.loads((W/'hybrid_calibration_v01.json').read_text())['nominal_hand_target_world']);")
s=s.replace('if args.render or args.record_demo or args.policy:', 'if True:')
s=s.replace(" capture('start')\n if args.policy:", """ capture('start')
 from visual_grasp import VisualGrasp
 torch.set_num_threads(2)
 estimator=VisualGrasp(args.visual_checkpoint,W/'hybrid_calibration_v01.json')
 rgb,depth=current_images()
 Image.fromarray(rgb).save(out/'vision_input_rgb.png');np.save(out/'vision_input_depth.npy',depth)
 prediction=estimator.predict(rgb,depth,blank=args.vision_ablation=='blank')
 prediction['checkpoint_sha256']=hashlib.sha256(args.visual_checkpoint.read_bytes()).hexdigest()
 prediction['vision_ablation']=args.vision_ablation
 (out/'visual_prediction.json').write_text(json.dumps(prediction,indent=2))
 for name in ['visual_grasp.py','handle_vision.py','hybrid_calibration_v01.json']:(out/name).write_bytes((W/name).read_bytes())
 if not prediction['accepted']:raise ValueError(('Visual grasp rejected before approach',prediction['reasons']))
 contact_T=np.array(prediction['hand_target_world']);pre=contact_T.copy();pre[2,3]+=.045
 q,pe,re=kin.solve(pre[:3,3]+pre[:3,:3]@PALM_OFFSET,pre[:3,:3],row['q'])
 if pe>.0002 or re>.002:raise ValueError(('Visual pregrasp unreachable',pe,re))
 (out/'visual_pregrasp.json').write_text(json.dumps(dict(q=q.tolist(),position_error=pe,orientation_error=re),indent=2))
 if args.policy:""")
s=s.replace("scope='Learned image actor; ground truth used only for reset/evaluation.' if args.policy else 'State-informed scripted pickup from fixed task start; not learned.' if args.neutral_start else 'State-informed reset-pregrasp physical component; not learned.'", "scope='Learned RGB-D grasp selection, engineered motion and compliant contact pickup. Per-episode object truth used only for reset/outcome guards, not grasp targeting.'")
s=s.replace("scope='Closed-loop image/proprioception student with physical outcome checks.' if args.policy else 'Scripted pickup from a fixed task start; not vision-driven or learned.' if args.neutral_start else 'Secure lift from a reset pregrasp; not neutral-start, vision-based or learned.'", "scope='Learned RGB-D grasp target; engineered arm/hand controller. Real contact, no attachment. Fixed camera and flat-rest prior.'")
(W/'hybrid_pickup.py').write_text(s)
s=(W/'run_curriculum.py').read_text().replace("'physical_pickup.py'","'hybrid_pickup.py'").replace("'--compliant', '--thumb-effort'","'--joint-space-approach', '--vision-ablation', args.vision_ablation, '--compliant', '--thumb-effort'")
(W/'run_hybrid_curriculum.py').write_text(s)
contract=json.loads((W/'student_evaluation_contract.json').read_text());contract.update(status='User accepted hybrid approach; frozen before live hybrid validation',inputs=['head RGB-D for grasp landmarks','fixed head/board/flat-rest calibration','joint feedback and contacts for engineered control and guards'],learned_component='Two handle landmarks determine grasp position/yaw; arm approach/closure/lift are engineered.',forbidden=['per-episode object pose in visual prediction or grasp target','sampled reset parameters in grasp target','attachment or object teleport after reset'],vision_check='Blank-image live check must reject before approach; offline mismatched-image check must change grasp target. No ground-truth fallback.',physical_limits_unchanged=True)
(W/'hybrid_evaluation_contract_v01.json').write_text(json.dumps(contract,indent=2))
now=datetime.datetime.now().astimezone().isoformat();status=json.loads((W/'STATUS.json').read_text());status.update(updated_local=now,status='implementing_authorized_hybrid',pending_decision=None,power_note='ADP1 online; battery charging confirmed',learning_architecture='Learned visual grasp targeting with tested engineered motion controller',latest_result='User accepted staged approach; live hybrid qualification pending.');(W/'STATUS.json').write_text(json.dumps(status,indent=2))
path=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/learning-roadmap.json');d=json.loads(path.read_text());stage=next(x for x in d['stages'] if x['id']==10);stage['phase']='Learned visual grasp targeting accepted; live contact pickup tests underway';d['updated']=now;d['latest_progress']['learning']='Testing learned head-camera grasp estimates with the established contact pickup controller. Full-motion learning deferred; no attachment.';path.write_text(json.dumps(d,indent=2))
with (W/'PLAN.txt').open('a') as f:f.write('\n2026-11-14: User selected learned visual grasp target plus engineered motion first. Execute frozen hybrid validation, then independent tests and vision-dependence checks. Full motion learning remains later.\n')
print('Prepared hybrid files, calibration and evaluation contract.')
