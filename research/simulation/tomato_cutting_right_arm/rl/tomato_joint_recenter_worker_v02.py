"""Equivalent right-arm joint-angle origins; native calibration and coast.

Parent joint frames absorb a constant reference angle. Positions/limits and
drive/state position values shift by the opposite offset. No robot geometry,
mass, inertia, armature, effort/velocity limit or TGS iteration setting changes.
The original scene stays read-only. Import SDKs only after AppLauncher.
"""
import argparse, copy, hashlib, json, signal, traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources, sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=robot=None;passed=False;cases=[]
 def stop(*args):raise InterruptedError('Joint-coordinate diagnostic stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  plan_path=ROOT/'runs/offline/fixed_mount_com_frame_20261102_01/fixed_mount_plan.json';oldplan=json.loads(plan_path.read_text());base=ROOT/'runs/native/robot_wrench_com_trace_20261102_01';snapshot_path=base/'robot_kinematic_snapshot_com_frame.json';old_snapshot=json.loads(snapshot_path.read_text());calibration=ROOT/'runs/offline/com_frame_calibration_readback_20261102_01/measurements.json';velocity_path=ROOT/'runs/offline/moving_contact_protocol_20261102_01/initial_velocity.json';velocity=json.loads(velocity_path.read_text());blade_path=ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';contact_raw=base/'clear_before_interval0.npz';old_cases_path=base/'known_wrench_cases.json';home_path=ROOT/'runs/native/robot_energy_operator_v03_20261102_01/home_robot_mechanics.npz';stop_evidence=ROOT/'runs/native/moving_contact_c1_down_20261102_01/motion_consistency_stop_evidence.json';contract_path=ROOT/'runs/offline/integration_contract_20261102_42/contract.json'
  contract=json.loads(contract_path.read_text())
  if not sources_unchanged(contract['source_sha256'])or not json.loads(calibration.read_text())['passed']or not json.loads(stop_evidence.read_text())['numerical_motion_consistency_stop']:raise ValueError('Frozen coordinate/known-load diagnostic parents required')
  inputs=[plan_path,Path(oldplan['scene']),snapshot_path,calibration,velocity_path,blade_path,contact_raw,old_cases_path,home_path,stop_evidence,contract_path]+[Path(x)for x in oldplan['source_sha256']]
  pins=capture_sources(out,[Path(__file__)],inputs=inputs);dt=1/38400
  write(out,'input_manifest.json',dict(cases=21,actual_physx_steps=264,target_steps=0,dt_s=dt,calibration_cases=17,calibration_intervals_per_case=8,coast_cases=4,coast_intervals_per_case=32,position_equivalence_budget_m=1e-6,rotation_equivalence_budget_rad=1e-5,mass_matrix_equivalence_budget_kg_m2=1e-6,gravity_equivalence_budget_nm=1e-5,physical_limit_mapping_budget_rad=1e-6,coast_right_joint_position_velocity_budget_rad=1e-9,coast_geometry_velocity_budget_m=1e-7,scope='Equivalent angle-coordinate diagnostic only; original TGS32, motor and physical properties. No target, cut, training or automatic force/work qualification.'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np, torch
  from scipy.spatial.transform import Rotation
  from pxr import Usd, UsdPhysics, Gf
  from tomato_moving_contact_robot import MovingContactRobot
  from tomato_robot_kinematic_snapshot import snapshot as kinematic_snapshot
  torch.set_num_threads(1)
  names=oldplan['right_joint_names'];offset=np.array([old_snapshot['joint_values_rad'][n]for n in names]);offset_map=dict(zip(names,offset.tolist()));scene=out/'joint_recenter_scene.usda';stage=Usd.Stage.CreateNew(str(scene.resolve()));stage.GetRootLayer().subLayerPaths=[oldplan['scene']];all_prims=list(stage.Traverse());joints={prim.GetName():prim for prim in all_prims if prim.IsA(UsdPhysics.RevoluteJoint)and prim.GetName()in names}
  if set(joints)!=set(names):raise ValueError('All seven original arm joints must be found uniquely')
  paths={str(p.GetPath())for p in joints.values()};changes=[]
  for prim in all_prims:
   if any('Mimic'in api for api in prim.GetAppliedSchemas()):
    if str(prim.GetPath())in paths or any(str(target)in paths for rel in prim.GetRelationships()for target in rel.GetTargets()):raise ValueError('Coordinate offset would need a separately qualified mimic transformation')
  for name,angle in offset_map.items():
   prim=joints[name];joint=UsdPhysics.RevoluteJoint(prim);axis_name=joint.GetAxisAttr().Get();axis=np.eye(3)['XYZ'.index(axis_name)];q0=joint.GetLocalRot0Attr().Get();r0=Rotation.from_quat([*q0.GetImaginary(),q0.GetReal()]);newq=(r0*Rotation.from_rotvec(axis*angle)).as_quat().astype(np.float32);joint.GetLocalRot0Attr().Set(Gf.Quatf(float(newq[3]),Gf.Vec3f(*map(float,newq[:3]))));limits=[]
   for attr in [joint.GetLowerLimitAttr(),joint.GetUpperLimitAttr()]:
    old=float(attr.Get());new=float(np.float32(old-np.rad2deg(angle)));attr.Set(new);limits.append(dict(attribute=attr.GetName(),old_degrees=old,new_degrees=new,mapped_error_rad=float(np.deg2rad(new)+angle-np.deg2rad(old))))
   mapped_attrs=[]
   for attr_name in ['drive:angular:physics:targetPosition','state:angular:physics:position']:
    attr=prim.GetAttribute(attr_name)
    if attr and attr.Get()is not None:
     old=float(attr.Get());new=float(np.float32(old-np.rad2deg(angle)));attr.Set(new);mapped_attrs.append(dict(attribute=attr_name,old_degrees=old,new_degrees=new))
   oldj=next(j for j in old_snapshot['joints']if j['name']==name);A=np.array(oldj['parent_joint_matrix']);An=A.copy();An[:3,:3]=Rotation.from_quat(newq.astype(float)).as_matrix();B=np.array(oldj['inverse_child_joint_matrix']);errors=[]
   for delta in [-.1,0.,.1]:
    oldrot=np.eye(4);oldrot[:3,:3]=Rotation.from_rotvec(axis*(angle+delta)).as_matrix();newrot=np.eye(4);newrot[:3,:3]=Rotation.from_rotvec(axis*delta).as_matrix();oldT=A@oldrot@B;newT=An@newrot@B;errors.append(dict(delta_rad=delta,translation_error_m=float(np.linalg.norm(oldT[:3,3]-newT[:3,3])),rotation_error_rad=float(Rotation.from_matrix(oldT[:3,:3]@newT[:3,:3].T).magnitude())))
   if max(abs(v['mapped_error_rad'])for v in limits)>1e-6 or max(v['translation_error_m']for v in errors)>1e-6 or max(v['rotation_error_rad']for v in errors)>1e-5:raise ValueError('Typed coordinate change exceeds declared equivalence budget')
   changes.append(dict(joint=name,path=str(prim.GetPath()),old_angle_equals_new_plus_offset_rad=angle,shifted_limits=limits,shifted_drive_or_state_positions=mapped_attrs,algebraic_checks=errors))
  stage.GetRootLayer().Save();stage=None
  plan=copy.deepcopy(oldplan);plan['scene']=str(scene.resolve());plan['home_rad'].update({name:oldplan['home_rad'][name]-offset_map[name]for name in names});plan['right_joint_route_rad']=(np.array(oldplan['right_joint_route_rad'])-offset).tolist();plan['joint_coordinate_offset_rad']=offset_map;plan['joint_coordinates']='Native q_new; physical original q_old=q_new+recorded offset, qd and effort unchanged. Right contact initial native q is zero. Original IK Cartesian errors/routes remain original physical geometry references.';plan['source_sha256'][str(plan_path)]=hashlib.sha256(plan_path.read_bytes()).hexdigest();plan['source_sha256'][str(scene.resolve())]=hashlib.sha256(scene.read_bytes()).hexdigest();write(out,'fixed_mount_recenter_plan.json',plan);write(out,'coordinate_algebra_and_limits.json',dict(changes=changes,physical_parameters_modified=False,original_sources_modified=False,solver='Original TGS and32 position iterations retained'))
  robot=MovingContactRobot(out,plan,dt,np.zeros(7));r=robot.robot
  def check_equivalence(label,reference_pose,reference_M,reference_g,actual):
   position=float(np.linalg.norm(actual['body_link_pose'][:,:3]-reference_pose[:,:3],axis=1).max());angle=float((Rotation.from_quat(actual['body_link_pose'][:,3:]).inv()*Rotation.from_quat(reference_pose[:,3:])).magnitude().max());matrix=float(abs(actual['mass_matrix']-reference_M).max());gravity=float(abs(actual['gravity']-reference_g).max())
   if position>1e-6 or angle>1e-5 or matrix>1e-6 or gravity>1e-5:raise ValueError(('Native coordinate equivalence failed',label,position,angle,matrix,gravity))
   return dict(case=label,maximum_all_body_position_difference_m=position,maximum_all_body_orientation_difference_rad=angle,maximum_native_mass_matrix_difference_kg_m2=matrix,maximum_native_gravity_torque_difference_nm=gravity)
  robot.reset();home=robot.read();home_ref=np.load(home_path);checks=[check_equivalence('original_physical_home',home_ref['body_link_pose_world'],home_ref['native_mass_matrix'],home_ref['native_gravity'],home)]
  robot.reset_contact();before=robot.read();old=np.load(contact_raw);oldcases=json.loads(old_cases_path.read_text())['cases'];oldg=np.array(oldcases[0]['rows'][0]['robot_audit']['requested_gravity_effort_nm']);checks.append(check_equivalence('original_physical_contact',old['before_body_link_pose'],old['mass_matrix'],oldg,before))
  for key,actual in [('mass',before['mass']),('body_inertia_com_link_axes',r.data.body_inertia.torch[0].cpu().numpy().reshape(-1,3,3)),('armature',r.data.joint_armature.torch[0].cpu().numpy())]:
   if not np.array_equal(actual,old[key]):raise ValueError(('Physical mass/inertia/armature changed',key))
  native_limits=r.data.joint_pos_limits.torch[0].cpu().numpy()[robot.ids].astype(float)+offset[:,None];old_limits=np.deg2rad(np.array([[change['shifted_limits'][0]['old_degrees'],change['shifted_limits'][1]['old_degrees']]for change in changes]));write(out,'native_joint_limit_mapping.json',dict(native_shifted_limits_mapped_to_original_rad=native_limits.tolist(),original_authored_hard_limits_rad=old_limits.tolist(),planning_inset_rad=.002,scope='Original snapshot planner bounds contain +/-0.002rad insets. Physical hard limits compare against the original authored values, not the inset planning envelope. Original1e-6rad gate unchanged.'));limit_error=float(abs(native_limits-old_limits).max())
  if limit_error>1e-6:raise ValueError('Mapped physical native joint limits changed excessively')
  snap=kinematic_snapshot(robot)
  if not snap['all_body_fk_matches']:raise ValueError('New coordinate FK does not match initialized native geometry')
  write(out,'robot_kinematic_snapshot_recenter.json',snap);write(out,'native_coordinate_equivalence.json',dict(passed=True,cases=checks,physical_joint_limit_mapping_error_rad=limit_error,all_masses_inertias_armatures_exact=True,DOF=36,source_physical_fixed_mount_unchanged=True,scope='New zero for right joint angles only; physical equivalence at original home and contact, with typed roundoff recorded. Original material/geometry/motor/solver settings retained.'))
  com=r.data.body_com_pose_b.torch[0,robot.tool,:3].cpu().numpy().astype(float);vertices=np.array(json.loads(blade_path.read_text())['vertices']);point=vertices[np.argmax(np.linalg.norm(vertices-com,axis=1))];R=Rotation.from_quat(before['tool_pose'][3:]).as_matrix();lever=R@(point-com);off_force=np.eye(3)[int(np.argmin(abs(lever)))]*.01;off=np.r_[off_force,np.cross(lever,off_force)];definitions=[('clear_before',np.zeros(6))]
  for i in range(6):
   for sign,label in [(1,'positive'),(-1,'negative')]:definitions.append((f'axis{i}_{label}',sign*np.eye(6)[i]*(.01 if i<3 else .001)))
  definitions +=[('offcentre_positive',off),('offcentre_negative',-off),('offcentre_replay',off),('clear_after',np.zeros(6))]
  write(out,'known_wrench_definition.json',dict(local_COM_m=com.tolist(),actual_CAD_vertex_local_m=point.tolist(),definitions=[dict(case=name,wrench_COM=w.tolist())for name,w in definitions],body_names=r.body_names,joint_names=r.joint_names,backend_body_names=list(r.root_view.shared_metatype.link_names),native_reported_dt_s=robot.sim.get_physics_dt()))
  def save_raw(label,i,before,after,wrench):
   view=r.root_view;J=r.data.body_com_jacobian_w.torch[0].cpu().numpy().copy();incoming=view.get_link_incoming_joint_force().numpy().copy();np.savez(out/f'{label}_interval{i}.npz',mass=before['mass'],body_inertia_com_link_axes=r.data.body_inertia.torch[0].cpu().numpy().reshape(-1,3,3),armature=r.data.joint_armature.torch[0].cpu().numpy(),before_body_link_pose=before['body_link_pose'],after_body_link_pose=after['body_link_pose'],before_body_com_pose=before['body_com_pose'],after_body_com_pose=after['body_com_pose'],before_body_com_velocity=before['body_com_velocity'],after_body_com_velocity=after['body_com_velocity'],incoming_joint_wrench_backend=incoming,local_tool_com=com,applied_wrench_COM=wrench.astype(np.float32),body_com_jacobian_world=J)
  reference=None
  for label,wrench in definitions:
   robot.reset_contact();rows=[]
   for i in range(8):
    if(out/'stop.request').exists():raise InterruptedError('Owned coordinate calibration stop')
    before=robot.read();after,audit=robot.advance_contact(wrench,True,before);save_raw(label,i,before,after,wrench);rows.append(dict(interval=i,q_before=before['q'].tolist(),q_after=after['q'].tolist(),qd_before=before['qd'].tolist(),qd_after=after['qd'].tolist(),actual_requested_wrench_COM=wrench.tolist(),robot_audit=audit))
   current=np.array([np.r_[x['q_after'],x['qd_after']]for x in rows])
   if label=='offcentre_positive':reference=current
   if label=='offcentre_replay'and np.max(abs(current-reference))>1e-9:raise ValueError('Recentered known-load replay failed')
   cases.append(dict(case=label,rows=rows));write(out,'known_wrench_cases.json',dict(cases=cases))
  coasts=[];coast_reference={}
  for direction in ['down','up']:
   qd=np.array(velocity['joint_velocity_rad_s'])*(1 if direction=='down'else -1);twist=np.array(velocity['expected_tool_twist_world'])*(1 if direction=='down'else -1);robot.configure_initial_velocity(qd,twist)
   for repeat in range(2):
    label=f'coast_{direction}_{repeat}';before=robot.reset_moving_contact();q0=before['q'].copy();R0=Rotation.from_quat(before['tool_pose'][3:]).as_matrix();c0=before['tool_pose'][:3]+R0@com;dq=np.zeros(36);dc=np.zeros(3);trace=[]
    for i in range(32):
     if(out/'stop.request').exists():raise InterruptedError('Owned coordinate coast stop')
     before=robot.read();after,audit=robot.advance_contact(np.zeros(6),False,before);dq+=.5*dt*(before['qd']+after['qd']);dc+=.5*dt*(before['tool_velocity'][:3]+after['tool_velocity'][:3]);save_raw(label,i,before,after,np.zeros(6));trace.append(dict(interval=i,q_before=before['q'].tolist(),q_after=after['q'].tolist(),qd_before=before['qd'].tolist(),qd_after=after['qd'].tolist(),robot_audit=audit,actual_tool_pose_before=before['tool_pose'].tolist(),actual_tool_pose_after=after['tool_pose'].tolist(),actual_tool_velocity_before=before['tool_velocity'].tolist(),actual_tool_velocity_after=after['tool_velocity'].tolist()))
    R1=Rotation.from_quat(after['tool_pose'][3:]).as_matrix();c1=after['tool_pose'][:3]+R1@com;qerror=float(abs((after['q']-q0-dq)[robot.ids]).max());perror=float(abs(c1-c0-dc).max());displacement=float(np.linalg.norm(c1-c0))
    if qerror>1e-9 or perror>1e-7 or displacement<.5e-6:raise ValueError(('Recentered coast geometry/velocity mismatch',label,qerror,perror,displacement))
    if repeat==0:coast_reference[direction]=(after['q'].copy(),after['qd'].copy(),after['tool_pose'].copy())
    else:
     if max(float(abs(x-y).max())for x,y in zip(coast_reference[direction],(after['q'],after['qd'],after['tool_pose'])))>1e-9:raise ValueError('Recentered coasting replay failed')
    write(out,label+'_coast_trace.json',trace);coasts.append(dict(case=label,right_joint_position_velocity_error_rad=qerror,maximum_COM_pose_velocity_error_m=perror,actual_COM_displacement_m=displacement,integrated_native_COM_velocity_displacement_m=dc.tolist(),actual_COM_geometry_displacement_m=(c1-c0).tolist()));cases.append(dict(case=label,steps=32));write(out,'coast_measurements.json',dict(cases=coasts))
  if robot.steps!=264 or len(cases)!=21 or not sources_unchanged(pins):raise ValueError('Coordinate diagnostic clock/source mismatch')
  write(out,'joint_recenter_measurements.json',dict(component_passed=True,actual_physx_steps=264,target_steps=0,coordinate_equivalence=checks,coast_cases=coasts,known_signed_calibration_requires_independent_readback=True,full_23B_qualified=False,scope='Static physical coordinate equivalence and actual native zero-offset coasting motion/replay pass. Known signed load traces saved for independent Newton-Euler readback. No target/cutting work qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,joint_recenter_v02_component_passed=passed,controlled_steps=0 if robot is None else robot.steps,newton_steps=0,deformable_steps=0,cases_completed=len(cases)))
  if robot is not None:robot.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
