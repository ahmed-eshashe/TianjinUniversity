"""Bounded undamaged full-target duration diagnostic for the global candidate."""
import argparse,json,signal,time,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--long',action='store_true');args=p.parse_args();out=args.output;long=args.long;app=None;passed=False;steps=0;episodes=[]
 def stop(*a):raise InterruptedError('Global duration diagnostic stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  contracts=[ROOT/'work/integration_20261102/support_ledger_contract.json',ROOT/'work/integration_20261102/local_residual_contract.json'];pins=capture_sources(out,[Path(__file__)],inputs=contracts)
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_board_support import nodal_plane_stiffness
  from tomato_global_implicit import GlobalImplicitCandidate
  from tomato_global_ledger import GlobalSupportLedger
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(data);dt=1/2400;n=240 if long else 24;duration=n*dt;g=json.loads(contracts[0].read_text());local=json.loads(contracts[1].read_text());model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k);e=holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;s=GlobalImplicitCandidate(holder,data,fixed);states=[s.state(),s.state()];ledger=GlobalSupportLedger(s,data,fixed,k);write(out,'input_manifest.json',dict(duration_s=duration,dt_s=dt,episodes=2,deformable_steps=2*n,native_vbd_steps=0,controlled_steps=0,backend='Explicit float64 coupled global GN/PCG candidate using unchanged source forces, Newton registry and complete collision backend',maximum_outer_iterations=40,maximum_cg_iterations=1000,cg_relative_tolerance=1e-9,cg_absolute_tolerance=1e-13,solver_declared_duration_s=.1,solver_total_velocity_defect_budget_m_s=.0001,board_penetration_budget_m=.0001,maximum_displacement_m=.02,replay_position_budget_m=1e-10,replay_velocity_budget_m_s=1e-8,global_contract=g,local_contract=local,scope='Undamaged standalone duration/admissibility component test, no sustained settling or actual robot/work/fracture/cut claim. Original fixed remainder fixture, free cap and complete collision surface.'))
  finals=[]
  for episode in range(2):
   for state in states:s.reset(state)
   ledger.reset();initial=ledger.measurements(states[0])['energy']['total_j'];trace=[];start=time.monotonic()
   for i in range(n):
    if (out/'stop.request').exists():raise InterruptedError('Global diagnostic checkpoint stop')
    try:s.step(states[i%2],states[1-i%2],None,None,dt)
    except BaseException:write(out,'nonlinear_failure_trace.json',dict(episode=episode,step=i,iterations=s.last_trace));raise
    state=states[1-i%2];steps+=1;ledger.step(state,dt);x=state.particle_q.numpy();v=state.particle_qd.numpy();ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);audit=ledger.measurements(state);audit.update(time_s=(i+1)*dt,minimum_volume_ratio=float(ratios.min()),energy_increase_j=audit['energy']['total_j']-initial,board_penetration_m=float(max(0.,-x[:,2].min())),maximum_displacement_m=float(np.linalg.norm(x-data['x'],axis=1).max()),maximum_speed_m_s=float(np.linalg.norm(v,axis=1).max()),nonlinear_trace=s.last_trace)
    invalid=(not np.isfinite(x).all() or not np.isfinite(v).all() or ratios.min()<=.1 or holder.history.numpy().max() or holder.eligible.numpy().max() or not np.array_equal(x[fixed],data['x'][fixed]) or e.invalid.numpy()[0] or holder.volume_invalid.numpy()[0]);budget=(audit['linear_impulse_residual_ns']>g['linear_impulse_error_ns'] or audit['angular_impulse_residual_nms']>g['angular_impulse_error_nms'] or audit['energy_increase_j']>g['maximum_energy_increase_above_initial_j'] or audit['cumulative_absolute_nodal_impulse_residual_ns']>local['cumulative_absolute_nodal_impulse_residual_ns'] or audit['board_penetration_m']>.0001 or audit['maximum_displacement_m']>.02)
    if invalid or budget:np.savez(out/'first_bad_state.npz',x=x,v=v,previous_velocity=states[i%2].particle_qd.numpy(),bulk_force=ledger.force.numpy(),cohesive_force=ledger.objective_force.numpy(),closure_force=e.physical_force.numpy(),reference=data['x'],mass=data['mass'],fixture=fixed,cells=data['cells'],dt=np.array([dt]));write(out,'preflight_failure.json',dict(audit=audit,invalid=bool(invalid),budget_exceeded=bool(budget)));raise ValueError('Global candidate exceeded an unchanged numerical/geometry gate')
    trace.append(audit);write(out,'global_preflight_partial.json',dict(episodes=episodes,episode=episode,trace=trace,deformable_steps=steps))
   finals.append((x.copy(),v.copy()));episodes.append(dict(trace=trace,wall_s=time.monotonic()-start));np.savez(out/f'episode{episode}_final.npz',x=x,v=v)
  pe=float(abs(finals[0][0]-finals[1][0]).max());ve=float(abs(finals[0][1]-finals[1][1]).max())
  if pe>1e-10 or ve>1e-8 or steps!=2*n or not sources_unchanged(pins):raise ValueError('Global candidate replay/count/source gate failed')
  write(out,'global_preflight_measurements.json',dict(episodes=episodes,duration_s=duration,deformable_steps=steps,replay_position_error_m=pe,replay_velocity_error_m_s=ve,scope='Explicitly versioned global GN/PCG float64 standalone undamaged duration component. No long settling, load challenge, time/contact convergence, coupled robot work, fracture or performed cut qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,global_preflight_passed=passed,duration_s=.1 if long else .01,newton_steps=0,deformable_steps=steps,controlled_steps=0,episodes_completed=len(episodes)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
