"""Isolate world-position cancellation from material/mesh/solver convergence."""
import argparse,hashlib,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;cases=[]
 def stop(*a):raise InterruptedError('Position precision fixture stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp,newton
  from newton.solvers import SolverVBD
  wp.init();wp.set_device('cuda:0');origin=np.array([[0.,0.,h] for h in [.005,.02,.035,.06]]);mass=.001;duration=.01
  for factor in [1,4,8]:
   dt=1/(2400*factor);n=24*factor
   for mode in ['world','relative']:
    b=newton.ModelBuilder(gravity=(0.,0.,-9.81))
    for x in (origin if mode=='world' else np.zeros_like(origin)):b.add_particle(wp.vec3(*x),wp.vec3(0.),mass,radius=0.)
    b.color();model=b.finalize(device='cuda:0');solver=SolverVBD(model,iterations=1);states=[model.state(),model.state()]
    for i in range(n):
     if (out/'stop.request').exists():raise InterruptedError('Stop before freefall step')
     solver.step(states[i%2],states[1-i%2],None,None,dt);steps+=1
    wp.synchronize();state=states[n%2];x=state.particle_q.numpy().astype(float)+(origin if mode=='relative' else 0);v=state.particle_qd.numpy().astype(float);target_v=np.array([0.,0.,-9.81*dt*n]);target_x=origin+np.array([0.,0.,-.5*9.81*dt**2*n*(n+1)]);ve=float(abs(v-target_v).max());pe=float(abs(x-target_x).max());ie=float(np.linalg.norm(mass*np.sum(v-target_v,axis=0)));row=dict(storage=mode,dt_factor=factor,dt_s=dt,steps=n,velocity_error_m_s=ve,position_error_m=pe,impulse_error_ns=ie,final_v=v.tolist());cases.append(row);write(out,'precision_partial.json',dict(cases=cases,newton_steps=steps))
    if mode=='relative' and (ve>1e-5 or pe>1e-7 or ie>1e-7):raise ValueError('Relative-position freefall missed preregistered analytic budget '+str(row))
  for factor in [4,8]:
   world=next(q for q in cases if q['storage']=='world' and q['dt_factor']==factor);relative=next(q for q in cases if q['storage']=='relative' and q['dt_factor']==factor)
   if world['velocity_error_m_s']<10*relative['velocity_error_m_s'] or world['velocity_error_m_s']<.0001:raise ValueError('World-coordinate cancellation not independently reproduced')
  if steps!=624:raise ValueError('Unexpected freefall step count')
  write(out,'position_precision_measurements.json',dict(cases=cases,newton_steps=steps,source_sha256={str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},scope='Native four-particle freefall, no material/contact/volume forces. World-coordinate error is a diagnostic positive control; only relative-coordinate cases must meet the analytic budget. Does not qualify a relative-coordinate tomato solver.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,position_precision_passed=passed,newton_steps=steps,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
