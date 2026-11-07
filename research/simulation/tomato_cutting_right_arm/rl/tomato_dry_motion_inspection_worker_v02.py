"""Open the saved measured dry-motion scene, timeline paused. No physics steps."""
import argparse,json,signal,time,traceback,hashlib
from pathlib import Path
from tomato_isaac_startup_worker import write
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False
 def stop(*_):raise InterruptedError('Owned inspection stop')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  source=R/'runs/native/visible_dry_motion_20261102_01';result=json.loads((source/'supervisor_result.json').read_text())
  if not result['passed']or result['remaining_live_group_members']:raise ValueError('Dry-run parent or cleanup failed')
  scene=source/'inspection_scene.usda';write(out,'input_manifest.json',dict(scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),controlled_steps=0,inspection_seconds=180,scope='Paused saved-scene inspection only, no simulation or video.'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=False,device='cpu',visualizer=['kit']).app
  import numpy as np
  from scipy.spatial.transform import Rotation
  from pxr import UsdGeom,Gf
  import omni.usd,omni.timeline
  from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
  timeline=omni.timeline.get_timeline_interface();timeline.stop();context=omni.usd.get_context()
  if not context.open_stage(str(scene)):raise ValueError('Could not open saved inspection scene')
  for _ in range(30):app.update()
  stage=context.get_stage();camera=UsdGeom.Camera.Define(stage,'/DryMotionInspectionCamera');camera.CreateFocalLengthAttr(22.);camera.CreateClippingRangeAttr(Gf.Vec2f(.01,100.));viewport=get_active_viewport();viewport.camera_path=camera.GetPath()
  def view(eye,target,label):
   eye=np.array(eye,float);target=np.array(target,float);z=(eye-target)/np.linalg.norm(eye-target);x=np.cross([0,0,1],z);x/=np.linalg.norm(x);y=np.cross(z,x);T=np.eye(4);T[:3,:3]=np.stack([x,y,z],axis=1);T[:3,3]=eye;UsdGeom.Xformable(camera).MakeMatrixXform().Set(Gf.Matrix4d(T.T.tolist()))
   for _ in range(20):app.update()
   path=out/(label+'.png');handle=capture_viewport_to_file(viewport,str(path));deadline=time.monotonic()+10
   while time.monotonic()<deadline and(not path.exists()or path.stat().st_size<1000):app.update()
   if not path.exists()or path.stat().st_size<1000:raise ValueError('Inspection image failed')
   if timeline.is_playing():raise ValueError('Inspection timeline unexpectedly playing')
   return str(path)
  images=[view((-.8,.85,.8),(.28,0.,.18),'active_arm_overview'),view((-.4,.65,.5),(.13,.12,.22),'fixed_mount_inspection')]
  stage.GetRootLayer().Export(str(out/'paused_inspection_scene.usda'))
  write(out,'inspection_ready.json',dict(paused=True,controlled_steps=0,images=images,scene=str(out/'paused_inspection_scene.usda'),expires_after_ready_seconds=180,scope='Current display is the saved dry-motion endpoint. Ideal fixed joint, no physical bracket. No video, contact or simulation.'))
  print('PAUSED_INSPECTION_READY',flush=True);passed=True;until=time.monotonic()+180
  while app.is_running()and time.monotonic()<until and not(out/'stop.request').exists():
   if timeline.is_playing():timeline.pause()
   app.update();time.sleep(.02)
 except BaseException as exc:write(out,'worker_error.json',dict(error=repr(exc),traceback=traceback.format_exc()))
 finally:
  write(out,'worker_result.json',dict(diagnostic_passed=passed,dry_scene_inspection_passed=passed,controlled_steps=0,newton_steps=0,shutdown_requested=app is not None,training=False))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
