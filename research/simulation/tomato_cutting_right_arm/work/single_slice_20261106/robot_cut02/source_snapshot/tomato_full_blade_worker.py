"""Actual tomato and authored blade cell-coverage contact with PhysX feedback."""
import argparse,signal,traceback,json,hashlib
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=sim=None;passed=False;ns=ps=echoes=0;records=[]
 def stop(*args):raise InterruptedError('Full authored blade check stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp,newton
  from scipy.spatial.transform import Rotation
  import isaaclab.sim as sim_utils
  from isaaclab.assets import RigidObject,RigidObjectCfg
  from isaaclab_physx.physics import PhysxCfg
  from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg
  from tomato_native_full_model import registry,build_model,configure_solver,FullTomatoVBD
  from tomato_mesh_weighted_contact import set_penalty,publish
  from tomato_exact_blade_coverage import coverage,verify_cells
  from tomato_blade_quadrature import converged
  from tomato_exact_blade_queries import sample
  from tomato_native_worker import validate_inputs
  from tomato_half_step_reaction import collect_reaction
  from tomato_deterministic_contact_solver import FullBladeVBD
  wp.init();wp.set_device('cuda:0');data=registry();config=json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text());blade=validate_inputs(ROOT,config)['blade'];cells=json.loads((ROOT/'work/exact_blade_cells.json').read_text())
  if cells['source_blade_sha256']!=config['blade']['sha256'] or not cells['boundary_matches_original_facets']:raise ValueError('Changed exact blade input')
  certificate=verify_cells(blade,cells)
  author_rotation=np.array([[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]]);center=(np.min(blade['vertices'],axis=0)+np.max(blade['vertices'],axis=0))/2;local_vertices=(np.asarray(blade['vertices'])-center)@author_rotation.T;faces=np.asarray(blade['triangles']);tet=np.asarray(cells['cells'])
  triangles=np.asarray([tri for piece in data['design']['pieces'] for tri in piece['triangles']]);longest=float(np.max(np.linalg.norm(data['x'][triangles[:,1]]-data['x'][triangles[:,0]],axis=1)))
  if longest>.02:raise ValueError('Current full-mesh dynamic qualification requires small soft facets; oversized fixture remains a precision failure')
  top=float(data['x'][data['pairs'][:,0],2].max());entry_hits=[]
  for face in faces:
   points=local_vertices[face];matrix=(points[1:,:2]-points[0,:2]).T
   if abs(np.linalg.det(matrix))<1e-20:continue
   uv=np.linalg.solve(matrix,-points[0,:2]);bary=np.r_[1-uv.sum(),uv]
   if min(bary)>=-1e-12:entry_hits.append(float(bary@points[:,2]))
  if not entry_hits:raise ValueError('Actual blade has no central entry intersection')
  local_entry=min(entry_hits);initial_pos=[data['design']['cut_x_m'],0.,top-local_entry-.00025]
  sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=DT,gravity=(0.,0.,0.),physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),use_fabric=False,use_newton_actuators=False,log_dir=str(out)))
  spawn=sim_utils.CuboidCfg(size=(.001,.001,.001),rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),PhysxRigidBodyCfg(linear_damping=0.,angular_damping=0.,disable_gravity=True,sleep_threshold=0.,stabilization_threshold=0.,solver_position_iteration_count=16,solver_velocity_iteration_count=0)],collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=False),mass_props=sim_utils.MassCfg(mass=.02,density=0.))
  body=RigidObject(RigidObjectCfg(prim_path='/World/AuthoredBlade',spawn=spawn,init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(initial_pos),rot=(0.,0.,0.,1.))))
  from pxr import UsdGeom,Gf
  mesh=UsdGeom.Mesh.Define(sim.stage,'/World/AuthoredBlade/ActualBladeVisual');mesh.CreatePointsAttr([Gf.Vec3f(*p) for p in local_vertices]);mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr(faces.ravel().tolist())
  sim.stage.GetRootLayer().Export(str(out/'actual_tomato_blade_scene.usda'))
  sim.reset();base_count=int(sim._physics_step_count);body.set_coms_index(coms=torch.tensor([[[0.,0.,0.,0.,0.,0.,1.]]],dtype=torch.float32));body.set_inertias_index(inertias=torch.tensor([[[.001,0.,0.,0.,.001,0.,0.,0.,.001]]],dtype=torch.float32));body.write_root_com_velocity_to_sim_index(root_velocity=torch.zeros((1,6),dtype=torch.float32));body.update(DT)
  model=build_model(data,body=True);solver=configure_solver(model,data,iterations=96,solver_class=FullBladeVBD,integrate_with_external_rigid_solver=True,rigid_compliant_alm=True,rigid_avbd_beta=0.);sin=model.state();sout=model.state();contacts=newton.Contacts(rigid_contact_max=8,soft_contact_max=131072,requires_grad=False,clear_buffers=False,device='cuda:0');contacts._enable_rigid_soft_full_surface_contact=True;mass=model.particle_mass.numpy().astype(float);impulse=np.zeros(3)
  def packet():return dict(pose=body.data.root_link_pose_w.torch.cpu().tolist()[0],velocity=body.data.root_com_vel_w.torch.cpu().tolist()[0])
  def echo():
   nonlocal echoes
   p=packet()
   for state in (sin,sout):
    wp.copy(state.body_q,body.data.root_link_pose_w.warp);wp.copy(state.body_qd,body.data.root_com_vel_w.warp);wp.synchronize()
    if state.body_q.numpy().tolist()[0]!=p['pose'] or state.body_qd.numpy().tolist()[0]!=p['velocity']:raise ValueError('Authored blade state feedback differs')
   echoes+=1;return p
  original_packet=echo();episodes=[];reset_checks=[]
  def restore(pose):
   nonlocal sin,sout
   for composer in (body.instantaneous_wrench_composer,body.permanent_wrench_composer):composer.set_forces_and_torques_index(forces=torch.tensor([[[99.,-55.,33.]]],dtype=torch.float32),torques=torch.tensor([[[1.,2.,3.]]],dtype=torch.float32),positions=None,is_global=True)
   body.reset()
   if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:raise ValueError('Dirty blade wrench survived reset')
   body.write_root_pose_to_sim_index(root_pose=torch.tensor([pose],dtype=torch.float32));body.write_root_com_velocity_to_sim_index(root_velocity=torch.zeros((1,6),dtype=torch.float32));body.write_data_to_sim();body.update(DT)
   for state in (sin,sout):solver.reset(state,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD);state.clear_forces()
   solver.history.zero_();solver.eligible.zero_();solver.invalid.zero_();solver.volume_invalid.zero_();contacts.clear();solver.contact_weights=wp.zeros(0,dtype=float);echo();reset_checks.append(dict(dirty_queues_cleared=True,contact_count=int(contacts.soft_contact_count.numpy()[0]),material_history_zero=True))
  for episode in range(2):
   records=[];impulse=np.zeros(3)
   if episode:restore(original_packet['pose'])
   for i in range(8):
    if (out/'stop.request').exists():raise InterruptedError('Stopped between blade exchanges')
    before=packet();rotation=Rotation.from_quat(before['pose'][3:]).as_matrix();translation=np.array(before['pose'][:3]);world=local_vertices@rotation.T+translation;pos=sin.particle_q.numpy();c,query,quadrature=converged(world,tet,pos,triangles,data['x'],local_vertices,faces,rotation,translation);samples=c['samples']
    weights,payload=publish(contacts,samples,query);solver.contact_weights=wp.array(weights,dtype=float);solver.prepare_contacts(payload);count=len(weights);sin.clear_forces();solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1;solver.commit_cohesion(sout)
    if sout.body_q.numpy().tolist()[0]!=before['pose'] or sout.body_qd.numpy().tolist()[0]!=before['velocity']:raise ValueError('Newton changed PhysX-owned blade')
    reaction=collect_reaction(model,sout,sin,contacts,solver) if count else dict(force=[],wrench=[]);force=np.asarray(reaction['force']).reshape(-1,3).sum(axis=0);wrench=np.asarray(reaction['wrench']).reshape(-1,6).sum(axis=0)
    body.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor([[wrench[:3].tolist()]],dtype=torch.float32),torques=torch.tensor([[wrench[3:].tolist()]],dtype=torch.float32),positions=None,is_global=True);body.write_data_to_sim();sim.step(render=False);ps+=1;body.update(DT);after=echo();x=sout.particle_q.numpy().astype(float);v=sout.particle_qd.numpy().astype(float);particle_momentum=(mass[:,None]*v).sum(axis=0);body_momentum=.02*np.array(after['velocity'][:3]);impulse+=DT*force;me=float(np.linalg.norm(particle_momentum+body_momentum));pie=float(np.linalg.norm(particle_momentum-impulse));bie=float(np.linalg.norm(body_momentum+impulse));angular=(np.cross(x,mass[:,None]*v)).sum(axis=0)+np.cross(np.asarray(after['pose'][:3]),body_momentum)+.001*np.asarray(after['velocity'][3:]);ae=float(np.linalg.norm(angular));ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
    record=dict(interval=i,generated_contacts=count,clipped_candidates=len(samples),quadrature=quadrature,covered_area_m2=sum(s['area_m2'] for s in samples),force_n=force.tolist(),wrench=wrench.tolist(),momentum_error_ns=me,particle_impulse_error_ns=pie,body_impulse_error_ns=bie,angular_momentum_error_nms=ae,min_volume_ratio=float(min(ratios)),blade_before=before,blade_after=after);record['positions']=x.tolist();record['velocities']=v.tolist();records.append(record);write(out,'full_blade_partial.json',dict(episodes=episodes,current_records=records,max_soft_edge_m=longest))
    if max(me,pie,bie)>2e-7 or ae>2e-8:raise ValueError(f'Authored blade coupling balance {me=}, {pie=}, {bie=}, {ae=}')
    if min(ratios)<=.1 or not np.isfinite(x).all():raise ValueError('Actual blade mesh step lost admissibility')
    sin,sout=sout,sin
   episodes.append(records)
  baseline,replay=episodes;comparisons=[]
  for first,second in zip(baseline,replay):
   pe=float(np.max(abs(np.asarray(first['positions'])-second['positions'])));ve=float(np.max(abs(np.asarray(first['velocities'])-second['velocities'])));fe=float(np.linalg.norm(np.asarray(first['force_n'])-second['force_n']));scale=max(np.linalg.norm(first['force_n']),np.linalg.norm(second['force_n']),1e-12);bpe=float(np.max(abs(np.asarray(first['blade_after']['pose'])-second['blade_after']['pose'])));bve=float(np.max(abs(np.asarray(first['blade_after']['velocity'])-second['blade_after']['velocity'])))
   comparisons.append(dict(interval=first['interval'],particle_position_error_m=pe,particle_velocity_error_m_s=ve,force_error_n=fe,body_pose_error=bpe,body_velocity_error=bve))
   write(out,'full_blade_replay_comparisons.json',dict(comparisons=comparisons))
   if pe>1e-7 or ve>2e-5 or bpe>1e-7 or bve>2e-5 or fe>.01*scale+1e-5:raise ValueError('Full authored-blade replay exceeds mechanical gates: '+str(comparisons[-1]))
  clear_pose=list(original_packet['pose']);clear_pose[2]+=.01;restore(clear_pose);before=packet();rotation=Rotation.from_quat(before['pose'][3:]).as_matrix();translation=np.asarray(before['pose'][:3]);world=local_vertices@rotation.T+translation;c,query,quadrature=converged(world,tet,sin.particle_q.numpy(),triangles,data['x'],local_vertices,faces,rotation,translation)
  if c['samples']:raise ValueError('Clear-space blade has solid intersections')
  weights,payload=publish(contacts,[],query);solver.contact_weights=wp.array(weights,dtype=float);solver.prepare_contacts(payload);solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1;body.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.zeros((1,1,3)),torques=torch.zeros((1,1,3)),positions=None,is_global=True);body.write_data_to_sim();sim.step(render=False);ps+=1;body.update(DT);clear_packet=echo();clear_speed=float(np.max(abs(sout.particle_qd.numpy())))
  if clear_speed>2e-5 or max(abs(v) for v in clear_packet['velocity'])>1e-7:raise ValueError('Stale force after blade clear/reset')
  clear_control=dict(contacts=0,particle_max_speed_m_s=clear_speed,blade_velocity=clear_packet['velocity'])
  if records[0]['generated_contacts']<=0 or np.linalg.norm(impulse)<=1e-8:raise ValueError('Missing generated actual blade force')
  if ns!=17 or ps!=17 or echoes!=20 or int(sim._physics_step_count)!=base_count+17:raise ValueError('Unexpected actual blade step counts')
  write(out,'full_blade_measurements.json',dict(episodes=episodes,replay_comparisons=comparisons,reset_checks=reset_checks,clear_control=clear_control,newton_steps=ns,physx_steps=ps,exact_feedback_echoes=echoes,max_soft_edge_m=longest,nodes=model.particle_count,triangles=len(triangles),rigid_tetrahedra=len(tet),material_frame='fixed world X; no damage eligibility in this contact qualification',reference_area_m2=1e-6,pressure_stiffness_n_m3=1.75e9,solid_cell_certificate=certificate,quadrature_measure='reference material area, three-point degree-2 Gaussian rule with bounded refinement',central_entry_z_local_m=local_entry,initial_entry_overlap_m=.00025,bulk_model_unchanged=True,cohesive_history_frozen=True,scope='Actual authored blade and complete saved tomato geometry in free dynamics. Synthetic contact/material/mass/inertia. Short contact exchange; not a full cut, robot or independent experiment.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,full_blade_passed=passed,newton_steps=ns,controlled_steps=ps,cuda_state_echoes=echoes,full_blade_intervals=sum(len(e) for e in episodes) if "episodes" in locals() else 0))
  if sim is not None:sim.stop();sim_utils.SimulationContext.clear_instance()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
