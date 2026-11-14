"""Bounded force-readout torque-source split diagnostic. No production controller edit."""
import argparse,json,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=parked=None;passed=False;steps=setup=cases=0
 def stop(*_):raise InterruptedError('Effort split diagnostic stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  import numpy as np
  contract=R/'work/astra_effort_resolution_20261102/effort_split_contract.json';pp=R/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json';npth=R/'runs/offline/near_approach_plan_20261102_02/near_approach_plan.json';prep=R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz';snap=R/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json';plan=json.loads(pp.read_text());plan['home_rad']=dict(plan['home_rad']);qnear=json.loads(npth.read_text())['right_joint_route_rad'][240];plan['home_rad'].update(dict(zip(plan['right_joint_names'],qnear)));pins=capture_sources(out,[Path(__file__)],inputs=[contract,pp,npth,prep,snap,Path(plan['scene'])]);write(out,'input_manifest.json',dict(contract=json.loads(contract.read_text()),source_sha256=pins,scope='Diagnostic equivalent equilibrium torque splits; no loaded contact, work qualification or production modification'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import torch
  from tomato_parked_robot import ParkedRobot
  parked=ParkedRobot(out,plan,1/240);r=parked.robot;write(out,'monitor.json',parked.positive_control());setup=parked.setup_steps;base=parked.home.clone();arm=[i for i,n in enumerate(r.joint_names)if '_AR5_'in n];target=np.load(prep)['x'];jn=list(r.joint_names);bn=list(r.body_names);jmap=[list(r.backend_joint_names).index(n)for n in jn]
  def arr(v):
   if hasattr(v,'torch'):v=v.torch
   return v.detach().cpu().numpy().copy()if hasattr(v,'detach')else v.numpy().copy()if hasattr(v,'numpy')else np.array(v,copy=True)
  def state():return dict(q=arr(r.data.joint_pos)[0],qd=arr(r.data.joint_vel)[0],pose=arr(r.data.body_link_pose_w)[0],com=arr(r.data.body_com_pose_w)[0],velocity=arr(r.data.body_com_vel_w)[0])
  write(out,'ordering.json',dict(joint_names=jn,body_names=bn,backend_joint_names=list(r.backend_joint_names),backend_body_names=list(r.backend_body_names),user_to_backend_joint=jmap,arm_ids=arm))
  np.savez_compressed(out/'parameters.npz',mass=arr(r.data.body_mass)[0],inertia=arr(r.data.body_inertia)[0],armature=arr(r.root_view.get_dof_armatures())[0],stiffness=arr(r.root_view.get_dof_stiffnesses())[0],damping=arr(r.root_view.get_dof_dampings())[0],friction=arr(r.root_view.get_dof_friction_properties())[0],limits=arr(r.root_view.get_dof_limits())[0])
  results=[];rows=[]
  for ci,fraction in enumerate([0.,1.,.5]):
   parked.home=base.clone();parked.reset();r.set_joint_velocity_target_index(target=torch.zeros_like(base));r.set_joint_effort_target_index(target=torch.zeros_like(base));r.write_data_to_sim();drift=speed=0.
   for k in range(24):
    before=state();gravity=r.data.gravity_compensation_forces.torch.clone();goal=base.clone();goal[:,arm]+=(1-fraction)*gravity[:,arm]/2500.;effort=torch.zeros_like(base);effort[:,arm]=fraction*gravity[:,arm];limits=r.data.joint_effort_limits.torch
    if torch.any(abs(effort)>limits):raise ValueError('Diagnostic effort exceeds original limit')
    parked.home=goal;r.set_joint_velocity_target_index(target=torch.zeros_like(base));r.set_joint_effort_target_index(target=effort);row=parked.step(target);steps+=1;after=state();raw=arr(r.root_view.get_link_incoming_joint_force())[0];measured=arr(r.root_view.get_dof_projected_joint_forces())[0];data={**{'before_'+n:v for n,v in before.items()},**{'after_'+n:v for n,v in after.items()},'gravity':arr(gravity)[0],'goal':arr(goal)[0],'explicit_effort':arr(effort)[0],'incoming':raw,'measured':measured,'approximate':arr(r.actuators.applied_effort)[0]}
    if not all(np.isfinite(x).all()for x in data.values()):raise ValueError('Nonfinite diagnostic')
    np.savez_compressed(out/f'case{ci}_step{k:02d}.npz',**data);drift=max(drift,float(np.max(abs(after['q'][arm]-arr(base)[0,arm]))));speed=max(speed,float(np.max(abs(after['qd'][arm]))));row.update(case=ci,fraction=fraction,step=k);rows.append(row)
   valid=drift<1e-4 and speed<.001;results.append(dict(case=ci,fraction=fraction,arm_pose_drift_rad=drift,maximum_arm_speed_rad_s=speed,static_valid=valid));cases+=1
   if not valid:raise ValueError(('Equilibrium control invalid',results[-1]))
  write(out,'trace.json',rows);write(out,'measurements.json',dict(cases=results,source_unchanged=sources_unchanged(pins),physics_steps=steps+setup,motor_work_qualified=False,scope='Readout diagnostic only'))
  if not sources_unchanged(pins):raise ValueError('Source closure changed')
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(diagnostic_passed=passed,effort_split_passed=passed,controlled_steps=steps+setup,executed_steps=steps,setup_physx_steps=setup,cases_completed=cases,deformable_steps=0,newton_steps=0,training=False,motor_work_qualified=False,shutdown_requested=app is not None))
  if parked is not None:parked.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
