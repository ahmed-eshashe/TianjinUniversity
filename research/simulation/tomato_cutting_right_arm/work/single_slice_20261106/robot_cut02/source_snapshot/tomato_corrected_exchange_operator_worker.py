"""Frozen real-CAD force handoff/queue test. Zero PhysX or deformable steps."""
import argparse,json,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=parked=None;passed=False;cases=[];queued=0
 def stop(*_):raise InterruptedError('Owned corrected exchange operator stop')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  parent=R/'work/corrected_contact_exchange_20261102/operator01/measurements.json';assert json.loads(parent.read_text())['passed'];planpath=R/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json';contactpath=R/'runs/offline/prepared_contact_candidate_20261102_03/ik_waypoints.json';nearpath=R/'runs/offline/near_approach_plan_20261102_02/near_approach_plan.json';prep=R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz';packetpath=R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz';snapshot=R/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json';bladepath=R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';pins=capture_sources(out,[Path(__file__)],inputs=[parent,planpath,contactpath,nearpath,prep,packetpath,snapshot,bladepath]);plan=json.loads(planpath.read_text());contact=json.loads(contactpath.read_text())[-1]['q_right_rad'];near=json.loads(nearpath.read_text())['right_joint_route_rad'][240];plan['home_rad']=dict(plan['home_rad']);plan['home_rad'].update(dict(zip(plan['right_joint_names'],contact)))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from tomato_parked_robot import ParkedRobot
  from tomato_exported_robot import ExportedRobot
  from tomato_cad_pressure import CADPressurePacket
  from tomato_corrected_contact_exchange import AcceptedContactExchange,CorrectedRobotContactQueue
  from tomato_host_fixed_pressure import evaluate_fixed
  parked=ParkedRobot(out,plan,1/240);r=parked.robot;start_count=int(parked.sim._physics_step_count);fk=ExportedRobot(snapshot);z=np.load(prep);x=z['x'];blade=json.loads(bladepath.read_text());ref=np.load(packetpath);geometry=np.array(blade['vertices']);faces=np.array(blade['triangles']);binding=CorrectedRobotContactQueue(r,parked.tool);arm_ids=[i for i,n in enumerate(r.joint_names)if '_AR5_'in n]
  write(out,'input_manifest.json',dict(source_sha256=pins,physical_steps=0,deformable_steps=0,cases=['positive','replay','clear'],positive_queue_requests=2,controller='Unchanged implicit gains plus native bounded arm gravity/zero velocity targets; commands written before queued contact, no simulation step.',clock_scope='Two synthetic1/76800s subinterval weights over one frozen force field exercise accumulation into1/38400s request; NO physical accepted intervals or elapsed contact time.',scope='Assigned frozen robot states and actual CAD material pressure operator. Queue only, then reset before writes/steps. No actual touch, physical force feedback, work, approach or cutting qualification.'))
  for label in ['positive','replay','clear']:
   parked.home[:,parked.ids]=torch.tensor([near if label=='clear'else contact],dtype=torch.float32);parked.reset();q0=r.data.joint_pos.torch[0].cpu().numpy().copy();qd0=r.data.joint_vel.torch[0].cpu().numpy().copy();K=fk.knife_pose(dict(zip(r.joint_names,map(float,q0))));native=r.data.body_link_pose_w.torch[0,parked.tool].cpu().numpy().astype(float);cn=r.data.body_com_pose_w.torch[0,parked.tool,:3].cpu().numpy().astype(float);com=r.data.body_com_pose_b.torch[0,parked.tool,:3].cpu().numpy().astype(float);cp=K[:3,3]+K[:3,:3]@com;gap=float(np.linalg.norm(K[:3,3]-native[:3]));angle=float(Rotation.from_matrix(K[:3,:3]@Rotation.from_quat(native[3:]).as_matrix().T).magnitude())
   if gap>1e-6 or angle>1e-5:raise ValueError('Actual q/Native contact geometry discrepancy')
   gravity=r.data.gravity_compensation_forces.torch.clone();effort=torch.zeros_like(parked.home);effort[:,arm_ids]=gravity[:,arm_ids];effort=torch.clamp(effort,min=-r.data.joint_effort_limits.torch,max=r.data.joint_effort_limits.torch);r.set_joint_velocity_target_index(target=torch.zeros_like(parked.home));r.set_joint_effort_target_index(target=effort);r.write_data_to_sim()
   data={k:ref[k][:0]if label=='clear'else ref[k]for k in ['indices','barycentric','areas']};vertices=geometry@K[:3,:3].T+K[:3,3];clear_gap=float(np.maximum(x.min(0)-vertices.max(0),vertices.min(0)-x.max(0)).max());domain_motion=None
   if label=='clear':
    if clear_gap<=.015:raise ValueError('Clear operator packet lacks a positive geometric certificate')
   else:
    domain_motion=float(np.linalg.norm(vertices-(geometry@ref['rotation'].T+ref['translation']),axis=1).max())
    if domain_motion>5e-6:raise ValueError('Frozen material packet coverage-domain bound')
   wp.init();wp.set_device('cuda:0');pressure=CADPressurePacket(len(x));pressure.set_cad(vertices=geometry,triangles=faces,**data,rotation=K[:3,:3],translation=K[:3,3],com_local=com,source_scope='Frozen operator at measured actual-q geometry; no physical interval');energy=pressure.evaluate(wp.array(x,dtype=wp.vec3d));force=pressure.force.numpy();wrench=pressure.reaction();penetration=float(max(0.,-pressure.phi.numpy().min(initial=0.)))if pressure.count else 0.;reference=evaluate_fixed(blade,x,data,K[:3,:3],K[:3,3],com);ferr=float(abs(force-reference['force_n']).max());werr=float(abs(wrench-reference['body_wrench']).max());eerr=abs(energy-reference['energy_j'])
   if ferr>1e-9 or werr>1e-10 or eerr>1e-12:raise ValueError('Independent host CAD force/wrench/energy mismatch')
   exchange=AcceptedContactExchange(block_id=label,time_start_s=0.,robot_dt_s=1/38400,target_dt_s=1/76800,body_id=parked.tool,geometry_com_world=cp,native_com_world=cn)
   for i in range(2):exchange.accept(time_start_s=i/76800,time_end_s=(i+1)/76800,points_world=x,target_nodal_force=force,pressure_reaction_at_geometry_com=wrench,maximum_penetration_m=penetration)
   request=exchange.finish();native_w=np.array(request.requested_native_com_wrench);direct=np.r_[-force.sum(0),-np.cross(x-cn,force).sum(0)]
   if np.max(abs(native_w-direct))>1e-10:raise ValueError('Native COM reaction sign/moment mismatch')
   if label!='clear':
    if np.linalg.norm(wrench[:3])<1e-4:raise ValueError('Positive real-CAD signal missing')
    exchange.queue_once(binding);queued+=1
    try:exchange.queue_once(binding);raise AssertionError('Repeated application allowed')
    except ValueError:pass
    if not r.instantaneous_wrench_composer.active:raise ValueError('Native queue missing')
   elif np.any(force)or np.any(wrench)or energy or np.any(request.actual_float32_queue_wrench)or r.instantaneous_wrench_composer.active:raise ValueError('Clear operator is not empty')
   np.savez_compressed(out/(label+'_operator.npz'),x_world=x,force=force,reaction_geometry_COM=wrench,geometry_tool_matrix=K,geometry_com=cp,native_com=cn,native_tool_pose=native,local_com=com,requested_native_wrench=native_w,float32_queue_wrench=np.array(request.actual_float32_queue_wrench),indices=data['indices'],barycentric=data['barycentric'],areas=data['areas'],energy=np.array([energy]),gravity_effort=effort.cpu().numpy()[0])
   if not np.array_equal(r.data.joint_pos.torch[0].cpu().numpy(),q0)or not np.array_equal(r.data.joint_vel.torch[0].cpu().numpy(),qd0)or int(parked.sim._physics_step_count)!=start_count:raise ValueError('Frozen operator changed state or physical clock')
   parked.reset()
   if r.instantaneous_wrench_composer.active or r.permanent_wrench_composer.active:raise ValueError('Queued operator load not cleared before any physical step')
   cases.append(dict(case=label,pressure_samples=pressure.count,reaction_force_n=float(np.linalg.norm(wrench[:3])),maximum_penetration_m=penetration,actual_q_native_position_gap_m=gap,actual_q_native_angle_gap_rad=angle,packet_domain_motion_m=domain_motion,clear_CAD_bound_gap_m=clear_gap,host_native_force_error_n=ferr,host_native_wrench_error_n_nm=werr,host_native_energy_error_j=eerr,request=request.__dict__,queued_not_stepped=label!='clear',cleared_before_physics=True))
  checks=dict(cases_complete=len(cases)==3,positive_requests_queued_once=queued==2,no_physical_steps=int(parked.sim._physics_step_count)==start_count,source_closure_preserved=sources_unchanged(pins),zero_clear_reaction=cases[-1]['reaction_force_n']==0,positive_replay=cases[0]['request']['requested_native_com_wrench']==cases[1]['request']['requested_native_com_wrench'])
  write(out,'measurements.json',dict(checks=checks,cases=cases,physical_steps=0,deformable_steps=0,queued_positive_requests=queued,scope='Actual CAD pressure + once-only correct Native COM queue binding with corrected controller commands; frozen explicit initial states, no loaded dynamics, touch, physical impulse transfer, motor work or23B qualification.'))
  if not all(checks.values()):raise ValueError(('Exchange operator result failed',checks))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(diagnostic_passed=passed,corrected_exchange_operator_passed=passed,controlled_steps=0,deformable_steps=0,newton_steps=0,cases_completed=len(cases),queued_requests=queued,shutdown_requested=app is not None,training=False))
  if parked is not None:parked.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
