"""Actual fixed-mount robot and elastic triangle; no fracture or tomato claim."""
import argparse,hashlib,json,signal,sys,time,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output
 app=sim=None;passed=False;ns=ps=0;cases=[]
 def stop(*args):raise InterruptedError('Mounted contact diagnostic stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  cp=ROOT/'runs/offline/integration_contract_20261102_01/contract.json';contract=json.loads(cp.read_text());cfg=contract['mounted_coupon'];g=cfg['gates'];dt=cfg['dt_s']
  plan_path=ROOT/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json';plan=json.loads(plan_path.read_text())
  source_files=[cp,plan_path,Path(plan['scene']),Path(__file__),ROOT/'rl/tomato_mesh_weighted_contact.py',ROOT/'rl/tomato_half_step_reaction.py',ROOT/'rl/tomato_blade_quadrature.py',ROOT/'rl/tomato_exact_blade_coverage.py',ROOT/'rl/tomato_exact_blade_queries.py',ROOT/'work/exact_blade_cells.json']
  pins={**plan['source_sha256'],**{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}}
  write(out,'input_manifest.json',dict(source_sha256=pins,contract=contract,scope='Actual mounted robot; synthetic elastic coupon; no damage'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp,newton
  from scipy.spatial.transform import Rotation
  import isaaclab.sim as sim_utils
  from isaaclab_physx.physics import PhysxCfg
  from isaaclab.assets import Articulation,ArticulationCfg
  from isaaclab.actuators import ImplicitActuatorCfg
  from isaaclab.app.settings_manager import get_settings_manager
  from tomato_mesh_weighted_contact import MeshContactVBD,publish
  from tomato_blade_quadrature import converged
  from tomato_half_step_reaction import collect_reaction
  wp.init();wp.set_device('cuda:0')
  sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=dt,gravity=(0.,0.,0.),use_fabric=False,use_newton_actuators=False,physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),log_dir=str(out)))
  sim.stage.GetRootLayer().subLayerPaths.append(plan['scene']);get_settings_manager().set_bool('/physics/disableContactProcessing',False)
  m=np.asarray(plan['robot_root_world_matrix'])
  robot=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,init_state=ArticulationCfg.InitialStateCfg(pos=tuple(m[:3,3]),rot=tuple(Rotation.from_matrix(m[:3,:3]).as_quat()),joint_pos=plan['home_rad']),actuators={
   'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),
   'hand':ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),
   'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
  sim.reset();get_settings_manager().set_bool('/physics/disableContactProcessing',False)
  tool=robot.body_names.index('MountedKnife');ids=[robot.joint_names.index(n) for n in plan['right_joint_names']];home=torch.tensor([[plan['home_rad'][n] for n in robot.joint_names]],dtype=torch.float32)
  robot.reset();robot.write_joint_state_to_sim_index(position=home,velocity=torch.zeros_like(home));robot.set_joint_position_target_index(target=home);robot.write_data_to_sim();robot.update(dt)
  initial_pose=robot.data.body_link_pose_w.torch[0,tool].cpu().numpy().copy();local_com=robot.data.body_com_pose_b.torch[0,tool,:3].cpu().numpy().copy()
  blade=json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());verts=np.asarray(blade['vertices']);faces=np.asarray(blade['triangles']);tet=np.asarray(json.loads((ROOT/'work/exact_blade_cells.json').read_text())['cells'])
  area=np.linalg.norm(np.cross(verts[faces[:,1]]-verts[faces[:,0]],verts[faces[:,2]]-verts[faces[:,0]]),axis=1)
  tri=verts[faces[int(np.argmax(area))]];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal);center=tri.mean(0)
  local_coupon=center+.035*(tri-center)-cfg['initial_penetration_m']*normal
  rotation=Rotation.from_quat(initial_pose[3:]).as_matrix();rest=local_coupon@rotation.T+initial_pose[:3]
  builder=newton.ModelBuilder(gravity=(0.,0.,0.))
  for point in rest:builder.add_particle(wp.vec3(*point),wp.vec3(0.),cfg['particle_mass_kg'],radius=0.)
  for a,b in [(0,1),(1,2),(2,0)]:builder.add_spring(a,b,cfg['spring_stiffness_n_m'],0.,0.)
  builder.add_triangle(0,1,2,tri_ke=0.,tri_ka=0.,tri_kd=0.)
  body=builder.add_body(xform=wp.transform(wp.vec3(*initial_pose[:3]),wp.quat(*initial_pose[3:])),com=wp.vec3(*local_com),is_kinematic=True)
  builder.add_shape_box(body,hx=.001,hy=.001,hz=.001,cfg=newton.ModelBuilder.ShapeConfig(density=0.,ke=2500.,kd=0.,mu=0.));builder.color();model=builder.finalize(device='cuda:0');model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
  solver=MeshContactVBD(model,iterations=32,integrate_with_external_rigid_solver=True,rigid_compliant_alm=True,rigid_avbd_beta=0.)
  states=[model.state(),model.state()];contacts=newton.Contacts(rigid_contact_max=8,soft_contact_max=4096,requires_grad=False,clear_buffers=False,device='cuda:0');contacts._enable_rigid_soft_full_surface_contact=True
  baseline_masses=model.particle_mass.numpy().astype(float);triangles=np.array([[0,1,2]])
  def packet():return dict(pose=robot.data.body_link_pose_w.torch[0,tool].cpu().numpy().tolist(),velocity=robot.data.body_com_vel_w.torch[0,tool].cpu().numpy().tolist())
  def echo():
   z=packet()
   for s in states:s.body_q.assign(np.asarray([z['pose']],dtype=np.float32));s.body_qd.assign(np.asarray([z['velocity']],dtype=np.float32))
   wp.synchronize();return z
  base_count=int(sim._physics_step_count)
  for label in cfg['cases']:
   driven=label.startswith('driven');feedback=label in ['passive_feedback','passive_replay','driven_feedback'];clear=label=='clear'
   for composer in [robot.instantaneous_wrench_composer,robot.permanent_wrench_composer]:composer.set_forces_and_torques_index(forces=torch.ones((1,1,3)),torques=torch.ones((1,1,3)),positions=None,body_ids=[tool],is_global=True)
   robot.reset();robot.write_joint_state_to_sim_index(position=home,velocity=torch.zeros_like(home));robot.set_joint_position_target_index(target=home)
   robot.write_joint_stiffness_to_sim_index(stiffness=torch.full((1,len(ids)),2500. if driven else 0.),joint_ids=ids)
   robot.write_joint_damping_to_sim_index(damping=torch.full((1,len(ids)),150. if driven else 0.),joint_ids=ids)
   robot.write_data_to_sim();robot.update(dt)
   if robot.instantaneous_wrench_composer.active or robot.permanent_wrench_composer.active:raise ValueError('Robot dirty wrench queue survived reset')
   if float((robot.data.joint_pos.torch-home).abs().max())>g['reset_joint_rad']:raise ValueError('Robot joint reset failed')
   points=rest+([0,0,.1] if clear else [0,0,0])
   for s in states:solver.reset(s,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD);s.particle_q.assign(points.astype(np.float32));s.particle_qd.zero_();s.clear_forces()
   solver.particle_q_prev.assign(points.astype(np.float32));contacts.clear();before=echo();records=[];impulse=np.zeros(3);start=time.monotonic()
   for i in range(cfg['intervals_per_case']):
    if (out/'stop.request').exists():raise InterruptedError('Stop during mounted contact')
    sin,sout=states[i%2],states[1-i%2];before=echo();rot=Rotation.from_quat(before['pose'][3:]).as_matrix();trans=np.asarray(before['pose'][:3]);x=sin.particle_q.numpy().astype(float);v0=sin.particle_qd.numpy().astype(float)
    clipped,query,quadrature=converged(verts@rot.T+trans,tet,x,triangles,points,verts,faces,rot,trans)
    weights,payload=publish(contacts,clipped['samples'],query);solver.contact_weights=wp.array(weights,dtype=float);count=len(weights)
    if not clear and i==0 and count==0:
     write(out,'missing_contact_geometry.json',dict(initial_pose=initial_pose.tolist(),before=before,rest=rest.tolist(),current=x.tolist(),local_coupon=local_coupon.tolist(),normal=normal.tolist(),samples=clipped['samples'],query={k:np.asarray(v).tolist() for k,v in query.items()}))
     raise ValueError('Missing initial generated authored-blade contact')
    sin.clear_forces();solver.step(sin,sout,None,contacts,dt);wp.synchronize();ns+=1
    if not np.array_equal(sout.body_q.numpy()[0],np.asarray(before['pose'],dtype=np.float32)):raise ValueError('Newton moved robot-owned blade')
    reaction=collect_reaction(model,sout,sin,contacts,solver) if count else dict(force=[],wrench=[],rigid_point=[])
    force=np.asarray(reaction['force']).reshape(-1,3).sum(0);wrench=np.asarray(reaction['wrench']).reshape(-1,6).sum(0);points_contact=np.asarray(reaction['rigid_point']).reshape(-1,3)
    com=trans+rot@local_com;moment=np.cross(points_contact-com,-np.asarray(reaction['force']).reshape(-1,3)).sum(0)
    impulse+=dt*force;vel=sout.particle_qd.numpy().astype(float);momentum=(baseline_masses[:,None]*vel).sum(0);impulse_error=float(np.linalg.norm(momentum-impulse))
    jac=robot.data.body_com_jacobian_w.torch[0,tool-1].cpu().numpy().astype(float);tau=jac.T@wrench
    qd_before=robot.data.joint_vel.torch[0].cpu().numpy().astype(float)
    if feedback:robot.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor([[wrench[:3].tolist()]],dtype=torch.float32),torques=torch.tensor([[wrench[3:].tolist()]],dtype=torch.float32),positions=None,body_ids=[tool],is_global=True)
    robot.set_joint_position_target_index(target=home);robot.write_data_to_sim();sim.step(render=False);ps+=1;robot.update(dt);after=echo();qd_after=robot.data.joint_vel.torch[0].cpu().numpy().astype(float)
    row=dict(interval=i,contacts=count,quadrature=quadrature,force_n=force.tolist(),wrench_at_tool_com=wrench.tolist(),independent_moment_nm=moment.tolist(),particle_impulse_error_ns=impulse_error,robot_before=before,robot_after=after,qd_before=qd_before.tolist(),qd_after=qd_after.tolist(),generalized_contact_torque_nm=tau.tolist(),particle_x=sout.particle_q.numpy().tolist(),particle_v=vel.tolist(),contact_exchange_power_w=float(wrench@np.asarray(before['velocity'])),particle_contact_work_j=float(np.sum(np.asarray(reaction['force']).reshape(-1,3)*(np.asarray([sum(np.asarray(payload['arrays']['soft_contact_barycentric'][j])[k]*(sout.particle_q.numpy()[payload['arrays']['soft_contact_indices'][j][k]]-x[payload['arrays']['soft_contact_indices'][j][k]]) for k in range(3)) for j in range(count)]).reshape(-1,3)))) if count else 0.,actual_max_initial_penetration_m=float(max(-np.asarray(query['phi']),default=0.)))
    records.append(row);write(out,'mounted_contact_partial.json',dict(cases=cases,current=label,records=records,newton_steps=ns,physx_steps=ps))
    if impulse_error>g['particle_impulse_error_ns'] or np.linalg.norm(force+wrench[:3])>g['wrench_balance_n'] or np.linalg.norm(moment-wrench[3:])>g['moment_balance_nm'] or np.linalg.norm(force)>g['force_ceiling_n']:raise ValueError('Mounted contact exceeded predeclared impulse/wrench gate')
    if not np.isfinite(sout.particle_q.numpy()).all() or not np.isfinite(qd_after).all():raise ValueError('Nonfinite mounted state')
    if robot.instantaneous_wrench_composer.active or robot.permanent_wrench_composer.active:raise ValueError('Wrench queue not consumed')
   cases.append(dict(label=label,records=records,elapsed_wall_s=time.monotonic()-start))
  by={c['label']:c['records'] for c in cases};comparisons={}
  for mode in ['passive','driven']:
   a,b=by[mode+'_feedback'],by[mode+'_no_feedback'];delta=np.asarray(a[0]['qd_after'])-np.asarray(b[0]['qd_after']);tau=np.asarray(a[0]['generalized_contact_torque_nm']);response=float(np.linalg.norm(delta));virtual=float(tau@delta)
   comparisons[mode]=dict(velocity_response_rad_s=response,virtual_response=virtual)
   if response<g['robot_response_min_rad_s'] or virtual<=g['virtual_response_min']:raise ValueError('Robot does not respond consistently to generated contact wrench')
  first,replay=by['passive_feedback'],by['passive_replay'];replay_error=max(float(np.max(np.abs(np.asarray(a[key])-b[key]))) for a,b in zip(first,replay) for key in ['particle_x','particle_v','qd_after'])
  if replay_error>1e-7:raise ValueError('Mounted contact replay mismatch')
  if any(r['contacts'] or np.linalg.norm(r['force_n']) for r in by['clear']):raise ValueError('Clear control has stale contact')
  if ns!=24 or ps!=24 or int(sim._physics_step_count)!=base_count+24:raise ValueError('Unexpected mounted-contact step count')
  write(out,'mounted_contact_measurements.json',dict(cases=cases,comparisons=comparisons,replay_error=replay_error,tool_body_index=tool,local_tool_com=local_com.tolist(),newton_steps=ns,physx_steps=ps,scope='Actual fixed-mount robot contact with elastic triangle, both passive and driven. No fracture, full-tomato contact, whole-system energy closure or sustained support claim.',source_pins_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items())))
  if not all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items()):raise ValueError('Mounted input source changed')
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,mounted_contact_passed=passed,newton_steps=ns,controlled_steps=ps,cases_completed=len(cases)))
  if sim is not None:sim.stop();sim_utils.SimulationContext.clear_instance()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
