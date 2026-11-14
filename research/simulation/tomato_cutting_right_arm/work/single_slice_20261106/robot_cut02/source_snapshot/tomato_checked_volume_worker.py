"""Reproduce saved volume-bound rounding failure and verify checked candidates."""
import argparse,hashlib,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;records=[]
 def stop(*args):raise InterruptedError('Checked volume audit stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp
  from tomato_native_volume_steps import colored_step,predictor_fraction,apply_predictor
  from tomato_checked_volume_steps import checked_colored_step,check_predictor,finish_predictor,reject_unverified_predictor
  from tomato_native_full_gather import adjacency
  wp.init();wp.set_device('cuda:0');path=ROOT/'runs/native/sustained_support_20261102_05/first_bad_update.npz';z=np.load(path);before=z['before'];base=z['baseline'];dis=z['displacement'];colors=z['colors'];cells=z['cells'];vol=z['volumes'];color=int(z['bad_info'][1]);offsets,rows=adjacency(cells,len(before));c=wp.array(colors,dtype=int);tet=wp.array(cells,dtype=wp.vec4i);v=wp.array(vol,dtype=float);v64=wp.array(vol,dtype=wp.float64);baseline=wp.array(base,dtype=wp.vec3)
  def ratio(x):return np.linalg.det(x.astype(float)[cells[:,1:]]-x.astype(float)[cells[:,:1]])/(6*vol)
  results={}
  for label,kernel in [('old',colored_step),('checked',checked_colored_step)]:
   x=wp.array(before,dtype=wp.vec3);d=wp.array(dis,dtype=wp.vec3);invalid=wp.zeros(1,dtype=int);clips=wp.zeros(1,dtype=int);args=[color,c,x,baseline,d,offsets,rows,tet,v]
   if label=='checked':args.append(v64)
   wp.launch(kernel,dim=len(before),inputs=args,outputs=[invalid,clips]);wp.synchronize();pos=x.numpy();results[label]=float(ratio(pos).min())
   records.append(dict(id=label+'_colored_update',minimum_reference_ratio=results[label],invalid=int(invalid.numpy()[0])))
  if not results['old']<=.1 or not results['checked']>.1:raise ValueError('Saved regression not reproduced/resolved')
  # A globally predicted move formed from the failing colored proposal.
  proposed=np.zeros_like(dis);mask=colors==color;proposed[mask]=base[mask]+dis[mask]-before[mask]
  for label,move in [('checked_predictor',proposed),('clear_predictor',np.zeros_like(proposed))]:
   x=wp.array(before,dtype=wp.vec3);b=wp.array(before,dtype=wp.vec3);d=wp.array(move,dtype=wp.vec3);fraction=wp.ones(1,dtype=float);invalid=wp.zeros(1,dtype=int);active=wp.ones(1,dtype=int);bad=wp.zeros(1,dtype=int)
   wp.launch(predictor_fraction,dim=len(cells),inputs=[b,d,tet,v],outputs=[fraction,invalid])
   for _ in range(40):
    bad.zero_();wp.launch(check_predictor,dim=len(cells),inputs=[b,d,tet,v,v64,fraction,active],outputs=[bad]);wp.launch(finish_predictor,dim=1,inputs=[fraction,active,bad])
   wp.launch(reject_unverified_predictor,dim=1,inputs=[fraction,active,invalid]);wp.launch(apply_predictor,dim=len(before),inputs=[x,b,d,fraction]);wp.synchronize();minimum=float(ratio(x.numpy()).min())
   if minimum<=.1 or int(invalid.numpy()[0]):raise ValueError('Checked predictor left inadmissible geometry')
   if label=='clear_predictor' and not np.array_equal(x.numpy(),before):raise ValueError('Clear predictor changed geometry')
   records.append(dict(id=label,minimum_reference_ratio=minimum,fraction=float(fraction.numpy()[0])))
  write(out,'checked_volume_measurements.json',dict(cases=records,source_fixture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),floor_unchanged=.1,scope='Saved rounding regression for colored/predictor proposals, not sustained stability or complete-cut qualification'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,checked_volume_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(records)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
