"""Initial dynamic qualification of the objective full-model candidate."""
import argparse,hashlib,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;episodes=[]
 def stop(*args):raise InterruptedError('Objective full model stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp,newton,time
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_objective_full_model import ObjectiveTomatoVBD,configure_objective
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();model=build_model(data);solver=configure_objective(configure_solver(model,data,iterations=16,solver_class=ObjectiveTomatoVBD),data);states=[model.state(),model.state()];rest=model.particle_q.numpy().copy()
  files=[Path(__file__),ROOT/'rl/tomato_objective_full_model.py',ROOT/'rl/tomato_objective_bulk_gather.py',ROOT/'rl/tomato_native_objective_reference.py',ROOT/'rl/tomato_objective_cohesion_reference.py',ROOT/'rl/tomato_checked_volume_steps.py',ROOT/'rl/tomato_board_support.py',ROOT/'rl/tomato_native_full_model.py'];pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};write(out,'input_manifest.json',dict(source_sha256=pins,dt_s=1/2400,iterations=16,mechanical_law='original bulk spring/barrier plus versioned objective interface',self_contact=False))
  for episode in range(2):
   for state in states:solver.reset(state,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD);state.particle_q.assign(rest);state.particle_qd.zero_();state.clear_forces()
   solver.particle_q_prev.assign(rest);solver.reset_material();trace=[]
   for i in range(2):
    if (out/'stop.request').exists():raise InterruptedError('Stop before objective full-model step')
    start=time.monotonic();sin,sout=states[i%2],states[1-i%2];solver.step(sin,sout,None,None,1/2400);wp.synchronize();steps+=1;solver.commit_cohesion(sout);x=sout.particle_q.numpy();v=sout.particle_qd.numpy();drift=float(np.max(np.abs(x-rest)));speed=float(np.max(np.abs(v)));ratios=np.linalg.det(x.astype(float)[data['cells'][:,1:]]-x.astype(float)[data['cells'][:,:1]])/(6*data['volumes']);trace.append(dict(x=x.tolist(),v=v.tolist(),maximum_drift_m=drift,maximum_speed_m_s=speed,minimum_volume_ratio=float(ratios.min()),wall_s=time.monotonic()-start));write(out,'objective_model_partial.json',dict(episodes=episodes,current=trace,newton_steps=steps))
    if drift>1e-7 or speed>2e-5 or ratios.min()<=.1 or not np.isfinite(x).all():raise ValueError('Candidate full-model rest gate failed')
   episodes.append(trace)
  pe=float(np.max(np.abs(np.asarray([r['x'] for r in episodes[0]])-np.asarray([r['x'] for r in episodes[1]]))));ve=float(np.max(np.abs(np.asarray([r['v'] for r in episodes[0]])-np.asarray([r['v'] for r in episodes[1]]))))
  if pe>1e-7 or ve>2e-5:raise ValueError('Candidate rest reset/replay gate failed')
  write(out,'objective_model_measurements.json',dict(episodes=episodes,position_replay_error_m=pe,velocity_replay_error_m_s=ve,newton_steps=steps,scope='Actual full saved bulk model with objective interface candidate, four no-contact rest steps and material reset. No gravity support, blade, fracture or self-contact qualification.',source_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items())));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,objective_model_passed=passed,newton_steps=steps,controlled_steps=0,episodes_completed=len(episodes)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
