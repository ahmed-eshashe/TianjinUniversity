"""Measure numerical settings honestly, including configurations that miss budgets."""
import argparse,hashlib,json,signal,time,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
ROOT=Path(__file__).resolve().parents[1]
SETTINGS=[(1,32),(1,64),(2,16),(2,32),(4,8),(4,16)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;complete=False;steps=0;experiments=[]
 def stop(*a):raise InterruptedError('Integration sensitivity stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  pins=capture_sources(out,[Path(__file__)],inputs=[ROOT/'work/integration_20261102/support_ledger_contract.json'])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp,newton
  from tomato_native_full_model import registry,configure_solver
  from tomato_board_support import nodal_plane_stiffness
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_relative_support_ledger import RelativeSupportLedger
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=np.array([0.,0.,.002]);fixed=np.asarray(data['design']['fixture']['node_ids']);model=build_relative_model(data,fixed_nodes=fixed);model.set_gravity((0.,0.,-9.81));k=nodal_plane_stiffness(data);s=configure_relative(configure_solver(model,data,iterations=32,solver_class=RelativeObjectiveVBD),data,board_stiffness=k);engine=s.surface_contact=RelativeSurfaceContact(data,s.spatial_reference,margin=.0001,capacity=256);engine.physical_colors=model.particle_colors;ledger=RelativeSupportLedger(s,data,fixed,k);states=[model.state(),model.state()];rest=model.particle_q.numpy().copy();contract_path=ROOT/'work/integration_20261102/support_ledger_contract.json';g=json.loads(contract_path.read_text())
  write(out,'input_manifest.json',dict(settings=SETTINGS,duration_s=.01,episodes_per_setting=2,total_expected_steps=684,position_comparison_screen_m=1e-5,velocity_comparison_screen_m_s=.001,ledger_contract=g,source_sha256=pins,scope='Numerical setting screen only; completing this study does not pass each configuration or sustained support.'))
  def reset():
   for state in states:s.reset(state,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD);state.particle_q.assign(rest);state.particle_qd.zero_();state.clear_forces()
   s.particle_q_prev.assign(rest);s.reset_material();engine.invalid.zero_();engine.contact_energy.zero_();ledger.reset()
  for factor,iterations in SETTINGS:
   dt=1/(2400*factor);n=24*factor;s.iterations=iterations;reset();s.step(states[0],states[1],None,None,dt);ledger.step(states[1],dt);s.step(states[1],states[0],None,None,dt);ledger.step(states[0],dt);wp.synchronize();steps+=2;reset()
   with wp.ScopedCapture() as capture:
    s.step(states[0],states[1],None,None,dt);ledger.step(states[1],dt);s.step(states[1],states[0],None,None,dt);ledger.step(states[0],dt)
   episodes=[];finals=[]
   for episode in range(2):
    reset();initial=ledger.measurements(states[0])['energy']['total_j'];trace=[];start=time.monotonic()
    for batch in range(n//2):
     if (out/'stop.request').exists():raise InterruptedError('Stop during sensitivity pair')
     wp.capture_launch(capture.graph);wp.synchronize();steps+=2;s.commit_cohesion(states[0]);x=data['x']+states[0].particle_q.numpy().astype(float);v=states[0].particle_qd.numpy().astype(float);ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);audit=ledger.measurements(states[0]);audit.update(time_s=(batch+1)*2*dt,energy_increase_j=audit['energy']['total_j']-initial,minimum_volume_ratio=float(ratios.min()))
     if not np.isfinite(x).all() or ratios.min()<=.1 or engine.invalid.numpy()[0] or s.volume_invalid.numpy()[0] or np.max(abs(states[0].particle_q.numpy()[fixed]))!=0 or s.history.numpy().max()!=0:raise ValueError('Invalid physical state during sensitivity screen')
     trace.append(audit);write(out,'sensitivity_partial.json',dict(experiments=experiments,current_setting=[factor,iterations],episode=episode,trace=trace,newton_steps=steps))
    episodes.append(dict(trace=trace,wall_s=time.monotonic()-start));finals.append((x.copy(),v.copy()));np.savez(out/f'final_f{factor}_i{iterations}_e{episode}.npz',x=x,v=v)
   pe=float(abs(finals[0][0]-finals[1][0]).max());ve=float(abs(finals[0][1]-finals[1][1]).max())
   if pe>1e-7 or ve>2e-5:raise ValueError('Sensitivity setting reset/replay failure')
   linear=max(row['linear_impulse_residual_ns'] for e in episodes for row in e['trace']);angular=max(row['angular_impulse_residual_nms'] for e in episodes for row in e['trace']);energy=max(row['energy_increase_j'] for e in episodes for row in e['trace']);within=linear<=g['linear_impulse_error_ns'] and angular<=g['angular_impulse_error_nms'] and energy<=g['maximum_energy_increase_above_initial_j'];experiments.append(dict(dt_factor=factor,dt_s=dt,iterations=iterations,episodes=episodes,replay_position_error_m=pe,replay_velocity_error_m_s=ve,maximum_impulse_residual_ns=linear,maximum_angular_residual_nms=angular,maximum_energy_increase_j=energy,within_ledger_budget=bool(within),warm_setup_excluded=True))
  reference=np.load(out/'final_f4_i16_e0.npz')
  for row in experiments:
   final=np.load(out/f"final_f{row['dt_factor']}_i{row['iterations']}_e0.npz");pe=float(abs(final['x']-reference['x']).max());ve=float(abs(final['v']-reference['v']).max());row['position_difference_from_finest_m']=pe;row['velocity_difference_from_finest_m_s']=ve;row['within_short_screen']=bool(row['within_ledger_budget'] and pe<=1e-5 and ve<=.001)
  if steps!=684:raise ValueError('Unexpected sensitivity step count')
  write(out,'sensitivity_measurements.json',dict(experiments=experiments,newton_steps=steps,source_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items()),scope='Rest-relative coordinates and float64 physical geometry, with contact queries refreshed each solver iteration. Original spring/barrier material laws; zero-stiffness mechanical triangles omitted, complete collision surface retained. 0.01 second numerical setting screen only; finest-reference self-agreement is not convergence proof.'));complete=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=complete,sensitivity_complete=complete,storage='rest-relative',newton_steps=steps,controlled_steps=0,settings_completed=len(experiments)))
  if app is not None:app.close(exit_code=0 if complete else 1)
 return 0 if complete else 1
if __name__=='__main__':raise SystemExit(main())
