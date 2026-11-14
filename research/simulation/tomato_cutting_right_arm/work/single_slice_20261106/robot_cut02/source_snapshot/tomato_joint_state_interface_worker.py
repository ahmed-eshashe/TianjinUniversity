"""Robot-only known-load replay through the actual-q precision interface.

Zero target steps. This cannot count as live tomato contact qualification.
PhysX owns joint motion; actual native and q-derived geometry are both saved.
"""
import argparse,json,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;robot=app=None;passed=False;cases=[]
 def stop(*args):raise InterruptedError('Actual-q interface diagnostic stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  parent=ROOT/'runs/native/joint_recenter_v03_20261102_01';proof=ROOT/'runs/offline/recenter_interface_readback_20261102_01/measurements.json';plan_path=parent/'fixed_mount_recenter_plan.json';snapshot=parent/'robot_kinematic_snapshot_recenter.json';profile_path=ROOT/'runs/offline/recorded_robot_wrench_profile_20261102_01/profile.json';velocity_path=ROOT/'runs/offline/moving_contact_protocol_20261102_01/initial_velocity.json';transport=ROOT/'runs/offline/kinematic_wrench_origin_operator_20261102_01/measurements.json';contract_path=ROOT/'runs/offline/integration_contract_20261102_44/contract.json'
  for path in [proof,transport]:
   d=json.loads(path.read_text())
   if not d['passed']or not sources_unchanged(d['source_sha256']):raise ValueError(('Required independent interface/origin parent missing',str(path)))
  if not json.loads((parent/'supervisor_result.json').read_text())['passed']or not sources_unchanged(json.loads(contract_path.read_text())['source_sha256']):raise ValueError('Qualified frozen coordinate/interface contract required')
  plan=json.loads(plan_path.read_text());plan['actual_q_kinematic_snapshot']=str(snapshot);profile=json.loads(profile_path.read_text());velocity=json.loads(velocity_path.read_text());pins=capture_sources(out,[Path(__file__)],inputs=[plan_path,snapshot,profile_path,velocity_path,proof,transport,contract_path,Path(plan['scene']),parent/'supervisor_result.json']+[Path(x)for x in plan['source_sha256']]);dt=1/38400
  write(out,'input_manifest.json',dict(dt_s=dt,intervals_per_case=32,cases=['down_profile','down_replay','down_clear','up_profile','up_replay','up_clear'],actual_physx_steps=192,target_steps=0,pose_source='Float64 FK of measured native q, no prescribed/commanded geometry. Native link/COM pose also recorded and bounded1um/1e-5rad. Wrench and velocity origins transported with virtual-work checks.',scope='Known external recorded-wrench robot-only replay, no live target. No automatic target/work/cutting qualification.'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch
  from tomato_joint_state_contact_robot import JointStateContactRobot
  torch.set_num_threads(1);robot=JointStateContactRobot(out,plan,dt,np.zeros(7));r=robot.robot;reference={};binding=False
  for direction in ['down','up']:
   factor=1 if direction=='down'else -1;robot.configure_initial_velocity(np.array(velocity['joint_velocity_rad_s'])*factor,np.array(velocity['expected_tool_twist_world'])*factor)
   for kind in ['profile','replay','clear']:
    label=f'{direction}_{kind}';before=robot.reset_moving_contact();initial_q=before['q'].copy();dq=np.zeros(36);rows=[]
    if not binding:
     np.savez(out/'robot_energy_binding_inputs.npz',mass=before['mass'],inertia_com_link_axes=r.data.body_inertia.torch[0].cpu().numpy().reshape(-1,3,3),armature=r.data.joint_armature.torch[0].cpu().numpy(),effort_limits=r.data.joint_effort_limits.torch[0].cpu().numpy(),joint_stiffness=r.data.joint_stiffness.torch[0].cpu().numpy(),joint_damping=r.data.joint_damping.torch[0].cpu().numpy());write(out,'robot_energy_binding_scope.json',dict(body_names=r.body_names,backend_incoming_joint_wrench_body_names=list(r.root_view.shared_metatype.link_names),inertia_axes='COM-centred link axes',initial_joint_velocity_abs_rad_s=abs(robot.initial_qd).tolist()));binding=True
    for i in range(32):
     if(out/'stop.request').exists():raise InterruptedError('Owned interface stop')
     before=robot.read();wrench=np.array(profile['wrench_n_nm'][i])if kind!='clear'else np.zeros(6);after,audit=robot.advance_contact(wrench,kind!='clear',before);dq+=dt*.5*(before['qd']+after['qd']);qerror=float(abs((after['q']-initial_q-dq)[robot.ids]).max())
     if qerror>1e-9:raise ValueError('Native relative joint integration lost pose/velocity consistency')
     incoming=r.root_view.get_link_incoming_joint_force().numpy()[0].copy();com=r.data.body_com_pose_b.torch[0,robot.tool,:3].cpu().numpy().astype(float)
     row=dict(interval=i,time_s=(i+1)*dt,q_before=before['q'].tolist(),q_after=after['q'].tolist(),qd_before=before['qd'].tolist(),qd_after=after['qd'].tolist(),kinematic_tool_pose_before=before['tool_pose'].tolist(),kinematic_tool_pose_after=after['tool_pose'].tolist(),native_tool_pose_before=before['native_tool_pose'].tolist(),native_tool_pose_after=after['native_tool_pose'].tolist(),kinematic_tool_velocity_before=before['tool_velocity'].tolist(),kinematic_tool_velocity_after=after['tool_velocity'].tolist(),native_tool_velocity_before=before['native_tool_velocity'].tolist(),native_tool_velocity_after=after['native_tool_velocity'].tolist(),kinematic_COM_world_before=before['kinematic_tool_com_world'].tolist(),kinematic_COM_world_after=after['kinematic_tool_com_world'].tolist(),native_COM_world_before=before['native_tool_com_world'].tolist(),native_COM_world_after=after['native_tool_com_world'].tolist(),kinematic_pressure_wrench_n_nm=wrench.tolist(),robot_audit=audit,robot_kinetic_energy_before_j=before['kinetic_energy_j'],robot_kinetic_energy_after_j=after['kinetic_energy_j'],right_joint_position_velocity_error_rad=qerror,native_kinematic_position_gap_m=after['native_kinematic_position_gap_m'],native_kinematic_rotation_gap_rad=after['native_kinematic_rotation_gap_rad']);rows.append(row)
     np.savez(out/f'{label}_interval{i}.npz',robot_body_link_pose_before=before['body_link_pose'],robot_body_link_pose_after=after['body_link_pose'],robot_body_com_pose_before=before['body_com_pose'],robot_body_com_pose_after=after['body_com_pose'],robot_body_com_velocity_before=before['body_com_velocity'],robot_body_com_velocity_after=after['body_com_velocity'],robot_incoming_joint_wrench_child_frame_backend_order=incoming,kinematic_tool_pose_before=before['tool_pose'],kinematic_tool_pose_after=after['tool_pose'],body_wrench=np.array(audit['requested_native_COM_wrench_n_nm']),kinematic_pressure_wrench=wrench,local_tool_com=com,dt=np.array([dt]));write(out,'interface_partial.json',dict(case=label,robot_steps=robot.steps,interval=i,last=row))
    current=(after['q'].copy(),after['qd'].copy(),after['tool_pose'].copy())
    if kind=='profile':reference[direction]=current
    if kind=='replay'and max(float(abs(x-y).max())for x,y in zip(reference[direction],current))>1e-9:raise ValueError('Actual-q interface loaded replay failed')
    write(out,label+'_robot_audit.json',rows);cases.append(dict(case=label,steps=32));write(out,'cases_partial.json',dict(cases=cases))
  if robot.steps!=192 or not sources_unchanged(pins):raise ValueError('Interface step/source identity failed')
  write(out,'joint_state_interface_measurements.json',dict(component_passed=True,actual_physx_steps=192,target_steps=0,cases=cases,actual_native_world_pose_velocity_gate_qualified=False,live_target_contact_qualified=False,full_23B_qualified=False,scope='Known external robot-only input through the actual-q geometry/COM-origin interface; independent work/force readback required. No live target, executed approach or cut.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,joint_state_interface_component_passed=passed,controlled_steps=0 if robot is None else robot.steps,newton_steps=0,deformable_steps=0,cases_completed=len(cases)))
  if robot is not None:robot.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
