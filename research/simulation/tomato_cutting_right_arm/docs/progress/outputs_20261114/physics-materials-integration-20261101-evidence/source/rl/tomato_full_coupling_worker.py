"""Actual tomato assembly exchanging contact loads with an isolated PhysX body."""
import argparse,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=sim=None;passed=False;ns=ps=echoes=0;episodes=[]
 def stop(*args):raise InterruptedError('Full-model coupling stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp,newton
  import isaaclab.sim as sim_utils
  from isaaclab.assets import RigidObject,RigidObjectCfg
  from isaaclab_physx.physics import PhysxCfg
  from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_half_step_reaction import collect_reaction
  from tomato_nonlinear_checks import spring_state
  wp.init();wp.set_device('cuda:0');data=registry()
  sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=DT,gravity=(0.,0.,0.),physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),use_fabric=False,use_newton_actuators=False,log_dir=str(out)))
  spawn=sim_utils.CuboidCfg(size=(.01,.01,.01),rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),PhysxRigidBodyCfg(linear_damping=0.,angular_damping=0.,disable_gravity=True,sleep_threshold=0.,stabilization_threshold=0.,solver_position_iteration_count=16,solver_velocity_iteration_count=0)],collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=False),mass_props=sim_utils.MassCfg(mass=.02,density=0.))
  body=RigidObject(RigidObjectCfg(prim_path='/World/FullMeshProbe',spawn=spawn,init_state=RigidObjectCfg.InitialStateCfg(pos=(-.0374,0.,.0275),rot=(0.,0.,0.,1.))))
  sim.reset();base_count=int(sim._physics_step_count)
  body.set_coms_index(coms=torch.tensor([[[0.,0.,0.,0.,0.,0.,1.]]],dtype=torch.float32));body.set_inertias_index(inertias=torch.tensor([[[.001,0.,0.,0.,.001,0.,0.,0.,.001]]],dtype=torch.float32));body.write_root_com_velocity_to_sim_index(root_velocity=torch.zeros((1,6),dtype=torch.float32));body.update(DT)
  model=build_model(data,body=True);solver=configure_solver(model,data,iterations=64,integrate_with_external_rigid_solver=True,rigid_compliant_alm=True,rigid_avbd_beta=0.)
  sin=model.state();sout=model.state();pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,soft_contact_max=16384,rigid_contact_max=8,enable_rigid_soft_full_surface_contact=True);contacts=pipeline.contacts();mass=model.particle_mass.numpy().astype(float)
  def packet():return dict(pose=body.data.root_link_pose_w.torch.cpu().tolist()[0],velocity=body.data.root_com_vel_w.torch.cpu().tolist()[0])
  def echo():
   nonlocal echoes
   p=packet()
   for state in (sin,sout):
    wp.copy(state.body_q,body.data.root_link_pose_w.warp);wp.copy(state.body_qd,body.data.root_com_vel_w.warp)
    wp.synchronize()
    if state.body_q.numpy().tolist()[0]!=p['pose'] or state.body_qd.numpy().tolist()[0]!=p['velocity']:raise ValueError('Actual full-mesh proxy feedback differs')
   echoes+=1;return p
  initial=echo();records=[];total_force=np.zeros(3);previous_momentum=np.zeros(3)
  for i in range(8):
   if (out/'stop.request').exists():raise InterruptedError('Stopped between full-mesh exchanges')
   before=packet();oldx=sin.particle_q.numpy().astype(float);oldv=sin.particle_qd.numpy().astype(float);sin.clear_forces();pipeline.collide(sin,contacts);wp.synchronize();count=int(contacts.soft_contact_count.numpy()[0])
   if not 0<=count<contacts.soft_contact_max:raise ValueError('Contact overflow')
   solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1;solver.commit_cohesion(sout)
   if sout.body_q.numpy().tolist()[0]!=before['pose'] or sout.body_qd.numpy().tolist()[0]!=before['velocity']:raise ValueError('Newton changed externally owned body')
   reaction=collect_reaction(model,sout,sin,contacts,solver) if count else dict(force=[],wrench=[])
   force=np.array(reaction['force'],dtype=float).reshape(-1,3).sum(axis=0);wrench=np.array(reaction['wrench'],dtype=float).reshape(-1,6).sum(axis=0)
   if np.linalg.norm(force+wrench[:3])>1e-7:raise ValueError('Contact action/reaction mismatch')
   body.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor([[wrench[:3].tolist()]],dtype=torch.float32),torques=torch.tensor([[wrench[3:].tolist()]],dtype=torch.float32),positions=None,is_global=True);body.write_data_to_sim();sim.step(render=False);ps+=1;body.update(DT);after=echo()
   x=sout.particle_q.numpy().astype(float);v=sout.particle_qd.numpy().astype(float);particle_momentum=(mass[:,None]*v).sum(axis=0);body_momentum=.02*np.array(after['velocity'][:3]);total_force+=DT*force
   residual=float(np.linalg.norm(particle_momentum+body_momentum));particle_impulse=float(np.linalg.norm(particle_momentum-total_force));body_impulse=float(np.linalg.norm(body_momentum+total_force))
   ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
   angular=(np.cross(x,mass[:,None]*v)).sum(axis=0)+np.cross(np.asarray(after['pose'][:3]),body_momentum)+.001*np.asarray(after['velocity'][3:]);angular_error=float(np.linalg.norm(angular))
   if angular_error>2e-8:raise ValueError(f'Full-model angular momentum gate {angular_error=}')
   record=dict(interval=i,contact_count=count,force_n=force.tolist(),wrench=wrench.tolist(),particle_momentum_ns=particle_momentum.tolist(),body_momentum_ns=body_momentum.tolist(),momentum_error_ns=residual,particle_impulse_error_ns=particle_impulse,body_impulse_error_ns=body_impulse,min_volume_ratio=float(min(ratios)),angular_momentum_error_nms=angular_error,body_before=before,body_after=after)
   records.append(record);write(out,'full_coupling_partial.json',dict(records=records))
   if max(residual,particle_impulse,body_impulse)>2e-7:raise ValueError(f'Full-model momentum/impulse gate {residual=}, {particle_impulse=}, {body_impulse=}')
   if min(ratios)<=.1 or not np.isfinite(x).all():raise ValueError('Actual mesh lost admissibility')
   sin,sout=sout,sin
  if records[0]['contact_count']<=0 or np.linalg.norm(total_force)<=1e-8:raise ValueError('Missing actual mesh contact transfer')
  if ns!=8 or ps!=8 or echoes!=9 or int(sim._physics_step_count)!=base_count+8:raise ValueError('Unexpected full coupling counts')
  write(out,'full_coupling_measurements.json',dict(records=records,newton_steps=ns,physx_steps=ps,exact_feedback_echoes=echoes,dt_s=DT,nodes=model.particle_count,springs=model.spring_count,patches=len(data['cohesion'].patches),scope='Actual full tomato assembly plus synthetic dynamic probe. Real blade and robot are separate qualification.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,full_coupling_passed=passed,newton_steps=ns,controlled_steps=ps,cuda_state_echoes=echoes))
  if sim is not None:sim.stop();sim_utils.SimulationContext.clear_instance()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
