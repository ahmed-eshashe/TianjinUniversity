"""Isolated plugin loading/provenance check. No scene, robot, or physics steps."""
import argparse, hashlib, json, signal, traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
R=Path(__file__).resolve().parents[1]
W=R/'work/native_instrumentation_20261102'
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output
 app=None;passed=False
 def stop(*_):raise InterruptedError('Native observer load check stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  manifest=json.loads((W/'override_manifest.json').read_text())
  for path,digest in manifest['files'].items():
   if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise ValueError('Override changed: '+path)
  write(out,'input_manifest.json',dict(override=manifest,worker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),physics_steps=0))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none'],fast_shutdown=False,kit_args='--/app/exts/devFolders=['+str(W/'override_v01')+']').app
  import omni.physx
  interface=omni.physx.get_physx_interface()
  if interface is None:raise RuntimeError('PhysX interface unavailable')
  paths=sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines() if 'libomni.physx.plugin.so' in line})
  expected=str(Path(manifest['core_plugin']).resolve())
  resolved=[str(Path(x).resolve()) for x in paths]
  write(out,'loaded_plugin.json',dict(paths=paths,resolved=resolved,expected=expected,hashes={x:hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in paths}))
  if resolved!=[expected]:raise RuntimeError('Wrong or duplicate loaded core plugin')
  passed=True
 except BaseException:
  write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(native_observer_load_passed=passed,controlled_steps=0,robot_steps=0,shutdown_requested=app is not None,training=False,motor_work_qualified=False))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
