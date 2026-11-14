"""Sixteen explicit global-candidate steps, with analytic and reset controls."""
import argparse,json,signal,time,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;cases=[]
 def stop(*a):raise InterruptedError('Global integrator stopped')
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
  from tomato_fraction_boundary import FractionBoundaryCandidate as GlobalImplicitCandidate
  from tomato_global_ledger import GlobalSupportLedger
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];k=nodal_plane_stiffness(data);dt=1/2400;global_contract=json.loads(contracts[0].read_text());local_contract=json.loads(contracts[1].read_text());write(out,'input_manifest.json',dict(cases=3,episodes_per_case=2,deformable_steps=16,newton_native_vbd_steps=0,controlled_steps=0,backend='Explicit float64 coupled Fraction-to-volume-boundary positive tensile-curvature block-Jacobi GN-preconditioned L-BFGS/PCG candidate, Newton registry and collision backend, original material/source precision',dt_s=dt,maximum_outer_iterations=40,maximum_cg_iterations=1000,cg_relative_tolerance=1e-9,cg_absolute_tolerance=1e-16,velocity_defect_budget_per_declared_duration_m_s=.0001,declared_solver_duration_s=.1,freefall_position_budget_m=1e-8,freefall_velocity_budget_m_s=1e-5,replay_position_budget_m=1e-10,replay_velocity_budget_m_s=1e-8,global_contract=global_contract,local_contract=local_contract,scope='Integrator component and analytic freefall controls only. No sustained support, coupled robot, fracture or cutting qualification.'))
  for label,fixed,gravity,count in [('freefall',np.array([],dtype=int),(0.,0.,-9.81),4),('rest_fixture',np.array(data['design']['fixture']['node_ids']),(0.,0.,0.),2),('gravity_fixture',np.array(data['design']['fixture']['node_ids']),(0.,0.,-9.81),2)]:
   model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k);e=holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;s=GlobalImplicitCandidate(holder,data,fixed,gravity=gravity);states=[s.state(),s.state()];ledger=GlobalSupportLedger(s,data,fixed,k);episodes=[];finals=[]
   for episode in range(2):
    for state in states:s.reset(state)
    ledger.reset();trace=[];start=time.monotonic();initial=ledger.measurements(states[0])['energy']['total_j']
    for i in range(count):
     if (out/'stop.request').exists():raise InterruptedError('Global integrator stop')
     try:s.step(states[i%2],states[1-i%2],None,None,dt)
     except BaseException:write(out,'nonlinear_failure_trace.json',dict(case=label,episode=episode,step=i,iterations=s.last_trace));raise
     state=states[1-i%2];steps+=1;x=state.particle_q.numpy();v=state.particle_qd.numpy();ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);row=dict(step=i,minimum_volume_ratio=float(ratios.min()),nonlinear_trace=s.last_trace)
     if not np.isfinite(x).all() or not np.isfinite(v).all() or ratios.min()<=.1 or holder.history.numpy().max() or holder.eligible.numpy().max() or not np.array_equal(x[fixed],data['x'][fixed]):raise ValueError('Invalid accepted global candidate state')
     if label=='freefall':
      expected_x=data['x'].copy();expected_x[:,2]+=-9.81*dt*dt*(i+1)*(i+2)/2;expected_v=np.tile([0,0,-9.81*dt*(i+1)],(len(x),1));pe=float(abs(x-expected_x).max());ve=float(abs(v-expected_v).max());row.update(analytic_position_error_m=pe,analytic_velocity_error_m_s=ve)
      if pe>1e-8 or ve>1e-5:raise ValueError('Global freefall differs from analytic implicit Euler')
     if label=='rest_fixture' and (np.max(abs(x-data['x']))>1e-15 or np.max(abs(v))>1e-12):raise ValueError('Zero-load rest changed')
     if label!='rest_fixture':
      ledger.step(state,dt);audit=ledger.measurements(state);audit['energy_increase_j']=audit['energy']['total_j']-initial;row['ledger']=audit
      if audit['linear_impulse_residual_ns']>global_contract['linear_impulse_error_ns'] or audit['angular_impulse_residual_nms']>global_contract['angular_impulse_error_nms'] or audit['energy_increase_j']>global_contract['maximum_energy_increase_above_initial_j'] or audit['cumulative_absolute_nodal_impulse_residual_ns']>local_contract['cumulative_absolute_nodal_impulse_residual_ns']:raise ValueError('Global integrator independent force/energy budget failed')
     trace.append(row);write(out,'fraction_integrator_partial.json',dict(cases=cases,current_case=label,episode=episode,trace=trace,deformable_steps=steps))
    finals.append((x.copy(),v.copy()));episodes.append(dict(trace=trace,wall_s=time.monotonic()-start));np.savez(out/f'{label}_episode{episode}.npz',x=x,v=v)
   pe=float(abs(finals[0][0]-finals[1][0]).max());ve=float(abs(finals[0][1]-finals[1][1]).max())
   if pe>1e-10 or ve>1e-8:raise ValueError('Global candidate reset/replay failed')
   cases.append(dict(case=label,episodes=episodes,replay_position_error_m=pe,replay_velocity_error_m_s=ve))
  if steps!=16 or not sources_unchanged(pins):raise ValueError('Global step count/source closure changed')
  write(out,'fraction_integrator_measurements.json',dict(cases=cases,deformable_steps=steps,native_vbd_steps=0,scope='Explicitly versioned Fraction-to-volume-boundary positive tensile-curvature block-Jacobi GN-preconditioned L-BFGS/PCG float64 integrator: analytic full-target freefall, exact zero-load rest, two-step remainder fixture and reset/replay controls. Sixteen candidate deformable steps; no sustained support, actual robot contact, fracture or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,fraction_integrator_passed=passed,newton_steps=0,deformable_steps=steps,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
