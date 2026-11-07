"""Exploratory fixed-attachment visible hand pose: bounded stationary check."""
import argparse,json,traceback,signal,time
from pathlib import Path
from tomato_isaac_startup_worker import write
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=parked=None;count=setup=0;passed=False
 def stop(*_):raise InterruptedError('Demo grip check stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  import numpy as np,torch
  plan=json.loads((R/'work/pickup_demo_20261104/posture_plan_v02.json').read_text());write(out,'scope.json',dict(exploratory=True,fixed_attachment=True,friction_grasp_validated=False,contact_or_cutting=False))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=False,device='cpu',visualizer=['kit']).app
  from tomato_parked_robot import ParkedRobot
  from pxr import UsdLux
  from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
  parked=ParkedRobot(out,plan,1/240);r=parked.robot;sim=parked.sim;write(out,'contact_control.json',parked.positive_control());setup=parked.setup_steps
  light=UsdLux.DomeLight.Define(sim.stage,'/DemoLight');light.CreateIntensityAttr(900.)
  target=np.load(R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz')['x'];arms=[i for i,n in enumerate(r.joint_names)if '_AR5_'in n];rows=[]
  for i in range(120):
   effort=torch.zeros_like(parked.home);effort[:,arms]=r.data.gravity_compensation_forces.torch[:,arms];r.set_joint_effort_target_index(target=effort);rows.append(parked.step(target));count+=1
  poses=r.data.body_link_pose_w.torch[0].cpu().numpy();center=poses[parked.hand,:3];write(out,'actual_pose.json',dict(joint_names=r.joint_names,q=r.data.joint_pos.torch[0].tolist(),body_names=r.body_names,poses=poses.tolist()))
  kr=np.array(plan['knife_rotation']);hc=np.array([-.0860033812,.0076461609,.0015865240]);grip_center=np.array(plan['knife_origin_route_m'][0])+kr@hc
  for name,eye,look in [('overview',np.array([1.5,1.2,1.0]),np.array([.45,-.15,-.05])),('hand_closeup',grip_center-.30*kr[:,0]+.20*kr[:,2]+np.array([0,0,.12]),grip_center),('grip_reverse',grip_center-.30*kr[:,0]-.20*kr[:,2]+np.array([0,0,.12]),grip_center),('grip_side',grip_center-.36*kr[:,0]+np.array([0,0,.08]),grip_center)]:
   sim.set_camera_view(eye=eye.tolist(),target=look.tolist())
   for _ in range(20):sim.render()
   path=out/(name+'.png');capture=capture_viewport_to_file(get_active_viewport(),str(path));deadline=time.monotonic()+20
   while time.monotonic()<deadline and(not path.exists()or path.stat().st_size<1000):sim.render();time.sleep(.01)
   if not path.exists():raise ValueError('Missing screenshot')
  write(out,'measurements.json',dict(rows=rows,fixed_attachment=True,actual_hand_error_rad=float((r.data.joint_pos.torch-parked.home).abs().max()),scope='Stationary pose, original physical stop bounds; no moving trajectory qualification'));passed=True
 except BaseException:
  write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
  if parked is not None:
   norm=np.linalg.norm(parked.contacts(),axis=-1);pairs=[dict(body=parked.bodies[i],other=parked.filters[j],force=float(norm[i,j])) for i,j in np.argwhere(norm>.1)];write(out,'collision_pairs.json',pairs)
   count=parked.steps
   center=r.data.body_link_pose_w.torch[0,parked.hand,:3].cpu().numpy();sim.set_camera_view(eye=(center+np.array([.25,-.3,.2])).tolist(),target=center.tolist())
   for _ in range(15):sim.render()
   capture=capture_viewport_to_file(get_active_viewport(),str(out/'failure_pose.png'))
   for _ in range(15):sim.render()
 finally:
  write(out,'worker_result.json',dict(demo_grip_passed=passed,controlled_steps=count+setup,shutdown_requested=app is not None,training=False))
  if parked is not None:parked.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
