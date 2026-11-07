"""Zero-step native COM/Jacobian/mass bindings for independent q references."""
import argparse,json,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;robot=app=None;passed=False;cases=[]
 def stop(*args):raise InterruptedError('Kinematic binding capture stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  parent=ROOT/'runs/native/joint_recenter_v03_20261102_01';plan_path=parent/'fixed_mount_recenter_plan.json';proof=ROOT/'runs/offline/recenter_interface_readback_20261102_01/measurements.json';plan=json.loads(plan_path.read_text());d=json.loads(proof.read_text())
  if not d['passed']or not sources_unchanged(d['source_sha256']):raise ValueError('Qualified coordinate parent required')
  pins=capture_sources(out,[Path(__file__)],inputs=[plan_path,proof,parent/'robot_kinematic_snapshot_recenter.json',Path(plan['scene'])]+[Path(x)for x in plan['source_sha256']])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch
  from tomato_moving_contact_robot import MovingContactRobot
  torch.set_num_threads(1);robot=MovingContactRobot(out,plan,1/38400,np.zeros(7));r=robot.robot
  for label in ['home','contact']:
   robot.reset()if label=='home'else robot.reset_contact();state=robot.read();np.savez(out/(label+'_kinematic_binding.npz'),q=state['q'],mass=state['mass'],inertia_com_link_axes=r.data.body_inertia.torch[0].cpu().numpy().reshape(-1,3,3),body_com_pose_local=r.data.body_com_pose_b.torch[0].cpu().numpy(),body_link_pose_world=state['body_link_pose'],body_com_pose_world=state['body_com_pose'],body_com_jacobian_world=r.data.body_com_jacobian_w.torch[0].cpu().numpy(),native_mass_matrix=state['mass_matrix'],native_gravity=state['gravity'],armature=r.data.joint_armature.torch[0].cpu().numpy(),joint_effort_limits=r.data.joint_effort_limits.torch[0].cpu().numpy());cases.append(label)
  write(out,'binding_scope.json',dict(body_names=r.body_names,joint_names=r.joint_names,right_joint_ids=robot.ids,local_COM_position_axes='Link-local; COM orientation does not rotate the full link-axis inertia tensor.',native_mass_matrix='Body terms only; unchanged armature separately retained.',scope='Static native data capture only; independent analytic body/Jacobian/work references required. Zero actual physics steps.'))
  if robot.steps!=0 or not sources_unchanged(pins):raise ValueError('Binding capture unexpectedly advanced physics or changed inputs')
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,robot_kinematic_binding_captured=passed,controlled_steps=0 if robot is None else robot.steps,newton_steps=0,deformable_steps=0,cases_completed=len(cases)))
  if robot is not None:robot.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
