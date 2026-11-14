"""Independent native positive-block audit; no mechanical steps."""
import argparse,hashlib,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--compact',action='store_true');args=p.parse_args();out=args.output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('GN reference audit stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_objective_full_model import configure_objective
  from tomato_objective_gn_blocks import objective_gn
  if args.compact:
   from tomato_objective_gn_compact import objective_gn
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();model=build_model(data);s=configure_objective(configure_solver(model,data,iterations=1),data);reference_path=ROOT/'work/integration_20261102/objective_gn_reference.npz';ref=np.load(reference_path);s.eligible.fill_(1)
  for label in ['rest','tensile','mixed_open','mixed_compressed','rotated_mixed','pure_compression']:
   if (out/'stop.request').exists():raise InterruptedError('Stop before GN audit case')
   s.objective_x.assign(ref[label+'_positions']);s.objective_hessian.zero_()
   wp.launch(objective_gn,dim=(s.pairs.shape[0],16) if args.compact else s.pairs.shape[0],inputs=[s.objective_x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible],outputs=[s.objective_hessian]);wp.synchronize();h=s.objective_hessian.numpy();error=float(abs(h-ref[label+'_blocks']).max());minimum=float(np.linalg.eigvalsh(h).min());symmetry=float(abs(h-h.transpose(0,2,1)).max());row=dict(id=label,block_reference_error_n_m=error,minimum_eigenvalue_n_m=minimum,symmetry_error_n_m=symmetry)
   if error>1e-6 or minimum< -1e-7 or symmetry>1e-7:raise ValueError('Positive moving-frame block audit failed '+str(row))
   cases.append(row)
  files=[Path(__file__),ROOT/'rl/tomato_objective_gn_blocks.py',ROOT/'rl/tomato_objective_gn_model.py',ROOT/'rl/tomato_objective_gn_compact.py',ROOT/'rl/tomato_objective_gn_compact_model.py',reference_path];pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};snapshot=out/'source_snapshot';snapshot.mkdir(exist_ok=True,parents=True)
  for p in files:(snapshot/p.name).write_bytes(p.read_bytes())
  write(out,'objective_gn_measurements.json',dict(cases=cases,source_sha256=pins,scope='Independent float64 local-gap Jacobian reference for positive Gauss-Newton blocks. Force law unchanged; not exact deformed force Jacobian or dynamic convergence qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,objective_gn_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
