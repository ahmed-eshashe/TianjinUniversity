"""Known signed six-axis/off-centre mounted-robot load TRACES, no target.

This records independent inertial/joint-wrench channels for later calibration.
Trace/queue/replay passes are not momentum, work or cutting qualification.
"""
import argparse,signal,traceback,json
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=robot=None;passed=False;cases=[]
 def stop(*args):raise InterruptedError('Known wrench calibration stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  plan_path=ROOT/'runs/offline/fixed_mount_com_frame_20261102_01/fixed_mount_plan.json';plan=json.loads(plan_path.read_text());waypoints=ROOT/'runs/offline/prepared_contact_candidate_20261102_03/ik_waypoints.json';q=json.loads(waypoints.read_text())[-1]['q_right_rad'];blade_path=ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';parent=ROOT/'runs/native/mounted_target_v06_r4_20261102_01/supervisor_result.json';baseline_pose_path=ROOT/'runs/native/mounted_target_v06_r4_20261102_01/no_feedback_interval0.npz';baseline_mechanics_path=ROOT/'runs/native/robot_energy_operator_v03_20261102_01/candidate_contact_robot_mechanics.npz';old_snapshot_path=ROOT/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json'
  if not json.loads(parent.read_text())['passed']:raise ValueError('Prior whole-target component required')
  pins=capture_sources(out,[Path(__file__)],inputs=[plan_path,waypoints,blade_path,Path(plan['scene']),parent,baseline_pose_path,baseline_mechanics_path,old_snapshot_path]+[Path(x)for x in plan['source_sha256']]);dt=1/38400;n=8
  write(out,'input_manifest.json',dict(cases=17,intervals_per_case=n,actual_physx_steps=136,target_steps=0,dt_s=dt,force_axis_amplitude_n=.01,moment_axis_amplitude_nm=.001,maximum_wrench_force_n=.010001,maximum_wrench_moment_nm=.003,controller='Same known gravity effort clipped to original limits, zero implicit gains; passive followers remain zero effort.',scope='Known synthetic forces and moments on actual fixed MountedKnife. Twelve signed axis cases, real-CAD-point off-centre positive/negative/replay, clear before/after. NO tomato or simultaneous target clock. Trace/reset checks only; independently validate physics/work later.'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch
  from scipy.spatial.transform import Rotation
  from tomato_contact_robot_v04 import ContactRobotV04
  from tomato_robot_kinematic_snapshot import snapshot as kinematic_snapshot
  torch.set_num_threads(1);robot=ContactRobotV04(out,plan,dt,q);robot.reset_contact();before=robot.read();r=robot.robot;com=r.data.body_com_pose_b.torch[0,robot.tool,:3].cpu().numpy().astype(float);vertices=np.array(json.loads(blade_path.read_text())['vertices']);point=vertices[np.argmax(np.linalg.norm(vertices-com,axis=1))];R=Rotation.from_quat(before['tool_pose'][3:]).as_matrix();lever=R@(point-com);axis=int(np.argmin(abs(lever)));off_force=np.eye(3)[axis]*.01;off=np.r_[off_force,np.cross(lever,off_force)];definitions=[('clear_before',np.zeros(6))]
  baseline=np.load(baseline_pose_path);mechanics=np.load(baseline_mechanics_path);old_pose=baseline['robot_body_link_pose_before'];new_pose=before['body_link_pose'];position_error=float(np.linalg.norm(old_pose[:,:3]-new_pose[:,:3],axis=1).max());angle_error=float(Rotation.from_quat(new_pose[:,3:]).inv().__mul__(Rotation.from_quat(old_pose[:,3:])).magnitude().max());matrix=r.data.mass_matrix.torch[0].cpu().numpy();g=r.data.gravity_compensation_forces.torch[0].cpu().numpy();matrix_error=float(abs(matrix-mechanics['native_mass_matrix']).max());gravity_error=float(abs(g-mechanics['native_gravity']).max());inertia=r.data.body_inertia.torch[0].cpu().numpy().reshape(-1,3,3);armature=r.data.joint_armature.torch[0].cpu().numpy();anchor=np.array(robot.sim.stage.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount').GetAttribute('physics:localPos1').Get());new_snapshot=kinematic_snapshot(robot)
  if r.num_joints!=36 or not np.array_equal(before['mass'],mechanics['mass'])or not np.array_equal(inertia,mechanics['inertia_com_link_axes'])or not np.array_equal(armature,mechanics['armature'])or not np.array_equal(anchor,com)or position_error>1e-6 or angle_error>1e-5 or matrix_error>1e-6 or gravity_error>1e-5 or not new_snapshot['all_body_fk_matches']:raise ValueError('Equivalent reporting-frame native parity failed')
  write(out,'robot_kinematic_snapshot_com_frame.json',new_snapshot);write(out,'native_coordinate_equivalence.json',dict(passed=True,maximum_all_body_position_difference_m=position_error,maximum_all_body_orientation_difference_rad=angle_error,maximum_native_mass_matrix_difference_kg_m2=matrix_error,maximum_native_gravity_torque_difference_nm=gravity_error,all_body_masses_exact=True,all_body_inertias_exact=True,all_joint_armatures_exact=True,DOF=36,knife_joint_anchor_equals_actual_local_COM=True,all_exported_FK_matches_actual=True,scope='Equivalent fixed joint reporting-frame change only. Native physical placement, M/g and exact unchanged masses/inertias/armature checked BEFORE any mechanical steps. Original source scene untouched.'))
  for i in range(6):
   vector=np.eye(6)[i]*(.01 if i<3 else .001)
   for sign,label in [(1,'positive'),(-1,'negative')]:definitions.append((f'axis{i}_{label}',sign*vector))
  definitions +=[('offcentre_positive',off),('offcentre_negative',-off),('offcentre_replay',off),('clear_after',np.zeros(6))];reference=None
  write(out,'known_wrench_definition.json',dict(local_COM_m=com.tolist(),actual_CAD_vertex_local_m=point.tolist(),offcentre_world_lever_m=lever.tolist(),offcentre_positive_wrench_COM=off.tolist(),definitions=[dict(case=name,wrench_COM=vector.tolist())for name,vector in definitions],body_names=r.body_names,joint_names=r.joint_names,backend_body_names=list(r.root_view.shared_metatype.link_names),native_reported_dt_s=robot.sim.get_physics_dt()))
  for label,wrench in definitions:
   robot.reset_contact();rows=[]
   for i in range(n):
    if(out/'stop.request').exists():raise InterruptedError('Known wrench checkpoint stop')
    before=robot.read();view=r.root_view
    def read(value):return value.numpy().copy()
    M=r.data.mass_matrix.torch[0].cpu().numpy().copy();J=r.data.body_com_jacobian_w.torch[0].cpu().numpy().copy();native_cfg=dict(stiffness=read(view.get_dof_stiffnesses()),damping=read(view.get_dof_dampings()),friction=read(view.get_dof_friction_coefficients()),friction_properties=read(view.get_dof_friction_properties()),backend_armature=read(view.get_dof_armatures()))
    if any(np.any(native_cfg[key])for key in ['stiffness','damping']):raise ValueError('Actual backend has uncounted native gains')
    after,audit=robot.advance_contact(wrench,True,before);incoming=read(view.get_link_incoming_joint_force());np.savez(out/f'{label}_interval{i}.npz',mass_matrix=M,tool_com_jacobian_world=J[robot.tool-1],body_com_jacobian_world=J,mass=before['mass'],body_inertia_com_link_axes=r.data.body_inertia.torch[0].cpu().numpy().reshape(-1,3,3),armature=r.data.joint_armature.torch[0].cpu().numpy(),before_body_link_pose=before['body_link_pose'],after_body_link_pose=after['body_link_pose'],before_body_com_pose=before['body_com_pose'],after_body_com_pose=after['body_com_pose'],before_body_com_velocity=before['body_com_velocity'],after_body_com_velocity=after['body_com_velocity'],incoming_joint_wrench_backend=incoming,**native_cfg)
    row=dict(interval=i,actual_physx_time_s=(i+1)*dt,q_before=before['q'].tolist(),q_after=after['q'].tolist(),qd_before=before['qd'].tolist(),qd_after=after['qd'].tolist(),tool_pose_before=before['tool_pose'].tolist(),tool_pose_after=after['tool_pose'].tolist(),tool_velocity_before=before['tool_velocity'].tolist(),tool_velocity_after=after['tool_velocity'].tolist(),actual_requested_wrench_COM=wrench.tolist(),robot_audit=audit);rows.append(row);write(out,'known_wrench_partial.json',dict(case=label,physx_steps=robot.steps,rows=rows))
    if np.linalg.norm(wrench[:3])>.010001 or np.linalg.norm(wrench[3:])>.003:raise ValueError('Declared isolated wrench amplitude exceeded')
   if label=='offcentre_positive':reference=np.array([np.r_[row['q_after'],row['qd_after'],row['tool_pose_after']]for row in rows])
   if label=='offcentre_replay':
    error=float(abs(np.array([np.r_[row['q_after'],row['qd_after'],row['tool_pose_after']]for row in rows])-reference).max())
    if error>1e-9:raise ValueError(('Known wrench replay failed',error))
   cases.append(dict(case=label,rows=rows));write(out,'known_wrench_cases.json',dict(cases=cases))
  if robot.steps!=136 or not sources_unchanged(pins):raise ValueError('Known wrench clock/source gate failed')
  write(out,'known_wrench_measurements.json',dict(trace_component_passed=True,actual_physx_steps=136,target_steps=0,cases=cases,scope='Known signed6D/off-centre/clear/replay trace and queue checks only. No independent dynamic force reconstruction, integrated impulse/work or target/cutting qualification inferred.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,robot_wrench_com_trace_passed=passed,controlled_steps=0 if robot is None else robot.steps,newton_steps=0,deformable_steps=0,cases_completed=len(cases)))
  if robot is not None:robot.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
