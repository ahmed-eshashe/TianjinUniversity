"""Single bounded corrected-controller clear-motion effort capture; no contact qualification."""
import argparse,json,signal,traceback,os,hashlib
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--trace',choices=['off','on'],required=True);args=p.parse_args();out=args.output;app=parked=None;passed=False;count=0;setup=0
 def stop(*_):raise InterruptedError('Bounded motor effort capture stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  w=R/'work/native_instrumentation_20261102';manifest=json.loads((w/'override_manifest_v02.json').read_text())
  for path,digest in manifest['files'].items():
   if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise ValueError('Override changed')
  os.environ.pop('TOMATO_NATIVE_DRIVE_TRACE',None)
  if args.trace=='on':os.environ['TOMATO_NATIVE_DRIVE_TRACE']=str(out/'native_trace.csv')
  write(out,'observer_manifest.json',dict(override=manifest,trace=args.trace,scope='Observer equivalence only; no motor-work qualification'))
  import numpy as np
  contract=R/'work/motor_work_review_20261102/capture_contract.json';planpath=R/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json';nearpath=R/'runs/offline/near_approach_plan_20261102_02/near_approach_plan.json';prep=R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz';snapshot=R/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json';plan=json.loads(planpath.read_text());near=json.loads(nearpath.read_text());route=np.array(near['right_joint_route_rad'])[240:256];plan['home_rad']=dict(plan['home_rad']);plan['home_rad'].update(dict(zip(plan['right_joint_names'],route[0])));pins=capture_sources(out,[Path(__file__)],inputs=[contract,planpath,Path(plan['scene']),nearpath,prep,snapshot]);write(out,'input_manifest.json',dict(source_sha256=pins,contract=json.loads(contract.read_text()),scope='Robot-only clear retreat, no target solve or contact work qualification'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none'],fast_shutdown=False,kit_args='--/app/exts/devFolders=['+str(w/'override_v02')+']').app
  paths=sorted({str(Path(line.split()[-1]).resolve()) for line in Path('/proc/self/maps').read_text().splitlines() if 'libomni.physx.plugin.so' in line})
  write(out,'loaded_plugin.json',dict(paths=paths))
  if paths!=[str(Path(manifest['core_plugin']).resolve())]:raise ValueError('Wrong loaded core plugin')
  import ctypes
  native=ctypes.CDLL(manifest["core_plugin"]);trace_snapshot=native.tomato_trace_pass_snapshot_v2;trace_snapshot.restype=ctypes.c_ulonglong;trace_snapshot.argtypes=[]
  markers=[]
  def mark(label):
   markers.append(dict(label=label,pass_count=int(trace_snapshot())));write(out,"trace_boundaries.json",markers)
  mark("before_robot_initialization")
  import torch
  from tomato_parked_robot import ParkedRobot
  parked=ParkedRobot(out,plan,1/240);mark("after_robot_initialization");r=parked.robot;write(out,'collision_positive_control.json',parked.positive_control());setup=parked.setup_steps;mark("after_monitor_control")
  if setup!=3:raise ValueError('Unexpected monitor setup count')
  base=parked.home.clone();armids=[i for i,n in enumerate(r.joint_names)if '_AR5_'in n];jn=list(r.joint_names);bn=list(r.body_names);bjn=list(r.backend_joint_names);bbn=list(r.backend_body_names);jmap=[bjn.index(n)for n in jn];bmap=[bbn.index(n)for n in bn];joints={j['name']:j for j in json.loads(snapshot.read_text())['joints']if j.get('name')};axes=[];children=[]
  for n in jn:
   j=joints[n];axes.append(j['axis']);children.append(bbn.index(j['child'].rsplit('/',1)[-1]))
  write(out,'ordering.json',dict(joint_names=jn,body_names=bn,backend_joint_names=bjn,backend_body_names=bbn,user_to_backend_joint=jmap,user_to_backend_body=bmap,joint_child_backend=children,child_joint_axes=axes,initial_q=base.cpu().numpy()[0].tolist()))
  def arr(v):
   if hasattr(v,'torch'):v=v.torch
   if hasattr(v,'detach'):return v.detach().cpu().numpy().copy()
   return v.numpy().copy()if hasattr(v,'numpy')else np.array(v,copy=True)
  def state():return dict(q=arr(r.data.joint_pos)[0],qd=arr(r.data.joint_vel)[0],body_pose=arr(r.data.body_link_pose_w)[0],body_com_pose=arr(r.data.body_com_pose_w)[0],body_com_velocity=arr(r.data.body_com_vel_w)[0])
  records=[];rows=[];start=int(parked.sim._physics_step_count)
  for step in range(120):
   seg=step//8;alpha=(step%8+1)/8;goal=base.clone();goal[:,parked.ids]=torch.tensor([(1-alpha)*route[seg]+alpha*route[seg+1]],dtype=torch.float32);velocity=torch.zeros_like(base);velocity[:,parked.ids]=torch.tensor([(route[seg+1]-route[seg])/(8*parked.dt)],dtype=torch.float32);parked.home=goal
   before=state();gravity=r.data.gravity_compensation_forces.torch.clone();effort=torch.zeros_like(base);effort[:,armids]=gravity[:,armids];limits=r.data.joint_effort_limits.torch;effort=torch.clamp(effort,min=-limits,max=limits);r.set_joint_velocity_target_index(target=velocity);r.set_joint_effort_target_index(target=effort)
   mark('before_step_'+str(step));row=parked.step(np.load(prep)['x']);mark('after_step_'+str(step));count+=1;after=state()
   measured=arr(r.root_view.get_dof_projected_joint_forces())[0];incoming=arr(r.root_view.get_link_incoming_joint_force())[0];commanded=arr(r.root_view.get_dof_actuation_forces())[0];again=arr(r.root_view.get_dof_projected_joint_forces())[0]
   if not np.array_equal(measured,again):raise ValueError('Measured effort changed without a physical step')
   projected=np.einsum('ij,ij->i',incoming[np.array(children),3:].astype(float),np.array(axes,dtype=float));muser=measured[jmap];err=np.abs(muser-projected);tol=1e-6+1e-6*np.abs(projected)
   record={**{'before_'+k:v for k,v in before.items()},**{'after_'+k:v for k,v in after.items()},'position_command':arr(goal)[0],'velocity_command':arr(velocity)[0],'gravity_feedforward':arr(effort)[0],'measured_effort_backend':measured,'measured_effort_repeat_backend':again,'incoming_joint_wrench_backend':incoming,'commanded_effort_backend':commanded,'approximate_applied_effort':arr(r.actuators.applied_effort)[0],'approximate_computed_effort':arr(r.actuators.computed_effort)[0],'projected_from_incoming_user':projected}
   if not all(np.isfinite(v).all()for v in record.values()):raise ValueError('Nonfinite effort/motion capture')
   np.savez_compressed(out/f'interval_{step:03d}.npz',**record);records.append(record);row.update(time_start_s=step*parked.dt,time_end_s=(step+1)*parked.dt,projection_error_max_nm=float(err.max()),projection_consistent=bool(np.all(err<=tol)));rows.append(row);write(out,'progress.json',dict(executed_steps=count,total_physx_steps=int(parked.sim._physics_step_count),stage='clear_effort_capture'))
   if not np.all(err<=tol):raise ValueError('Projected effort versus incoming joint projection mismatch; stop protocol')
  for name in ['get_dof_stiffnesses','get_dof_dampings','get_dof_armatures','get_dof_max_forces']:
   np.save(out/(name+'.npy'),arr(getattr(r.root_view,name)()))
  write(out,'robot_trace.json',rows)
  checks=dict(exact_steps=count==120 and int(parked.sim._physics_step_count)-start==120,source_closure_preserved=sources_unchanged(pins),projection_consistency=all(x['projection_consistent']for x in rows),measured_effort_varies=bool(np.ptp(np.array([x['measured_effort_backend']for x in records]),axis=0).max()>0),actual_motion=bool(np.max(np.abs(records[-1]['after_q']-records[0]['before_q']))>1e-5))
  write(out,'measurements.json',dict(checks=checks,maximum_projection_error_nm=max(x['projection_error_max_nm']for x in rows),maximum_measured_effort_nm=float(np.max(np.abs([x['measured_effort_backend']for x in records]))),physical_steps=count+setup,executed_steps=count,setup_physx_steps=setup,deformable_steps=0,motor_work_qualified=False,touch_qualified=False,scope='Measured-effort interface and clear motion only; not independently isolated drive work or energy precision qualification'))
  if not all(checks.values()):raise ValueError(('Effort capture checks failed',checks))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(diagnostic_passed=passed,motor_effort_capture_passed=passed,controlled_steps=count+setup,executed_steps=count,setup_physx_steps=setup,deformable_steps=0,newton_steps=0,shutdown_requested=app is not None,training=False,motor_work_qualified=False))
  if parked is not None:parked.close()
  if app is not None:
   # Release Kit hook holders while their native extension manager is alive.
   import isaaclab_physx
   isaaclab_physx._SIMULATION_MANAGER_ENABLE_HOOK = None
   from isaaclab_physx.physics.physx_manager import PhysxManager
   PhysxManager._timeline = None
   import sys,gc
   original=sys.modules.get("isaacsim.core.simulation_manager.impl.simulation_manager")
   if original is not None:original.SimulationManager._timeline = None
   gc.collect()
   write(out,'shutdown_lifecycle.json',dict(simulation_manager_hook_released_before_app_shutdown=True))
   app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
