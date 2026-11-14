"""Native two-loop recursion versus independent dense inverse-BFGS updates."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('BFGS operator stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  pins=capture_sources(out,[Path(__file__)])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_global_lbfgs import PositiveLBFGSMemory
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');n=7;size=3*n;rng=np.random.default_rng(77);Q=rng.normal(size=(size,size));A=Q.T@Q+np.eye(size);base=np.diag(np.linspace(.1,2.,size));write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,relative_direction_budget=1e-12,absolute_direction_budget=1e-10,scope='Two-loop arithmetic and curvature/memory controls only. No physical step or target support claim.'))
  for label,limit,negative in [('positive',8,False),('memory_eviction',2,False),('negative_curvature',8,True)]:
   memory=PositiveLBFGSMemory(n,maximum_pairs=limit);x=np.zeros((n,3));force=rng.normal(size=(n,3));memory.observe(wp.array(x,dtype=wp.vec3d),wp.array(force,dtype=wp.vec3d));kept=[]
   for _ in range(4):
    s=rng.normal(size=(n,3))*.01;y=(-s if negative else (A@s.ravel()).reshape(n,3));x+=s;force-=y;update=memory.observe(wp.array(x,dtype=wp.vec3d),wp.array(force,dtype=wp.vec3d))
    if not negative:kept.append((s.copy().ravel(),y.copy().ravel()));kept=kept[-limit:]
    if update['accepted']==negative:raise ValueError('Curvature safeguard failed')
   H=base.copy()
   for s,y in kept:
    rho=1/(s@y);V=np.eye(size)-rho*np.outer(s,y);H=V@H@V.T+rho*np.outer(s,s)
   q=memory.transform(wp.array(force,dtype=wp.vec3d)).numpy();direction=wp.array((base@q.ravel()).reshape(n,3),dtype=wp.vec3d);memory.finish(direction);actual=direction.numpy().ravel();expected=H@force.ravel();absolute=float(abs(actual-expected).max());relative=float(np.linalg.norm(actual-expected)/np.linalg.norm(expected));power=float(actual@force.ravel())
   if not(absolute<=1e-10 or relative<=1e-12)or power<=0 or len(memory.pairs)!=len(kept):raise ValueError((label,absolute,relative,power))
   memory.clear()
   if memory.pairs:raise ValueError('Memory clear failed')
   cases.append(dict(case=label,absolute_direction_error=absolute,relative_direction_error=relative,direction_dot_force=power,accepted_pairs=len(kept)))
  if not sources_unchanged(pins):raise ValueError('BFGS operator source changed')
  write(out,'lbfgs_operator_measurements.json',dict(cases=cases,scope='Three native recursion/positive-curvature/eviction controls versus dense CPU inverse-BFGS matrices. No integration, support or cut qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,lbfgs_operator_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
