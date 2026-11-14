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
  from tomato_failed_safe_global import FailedSafeFractionCandidate as GlobalImplicitCandidate
  from tomato_failed_safe_ledger import FailedSafeLocalLedger
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];k=nodal_plane_stiffness(data);dt=1/38400;global_contract=json.loads(contracts[0].read_text());local_contract=json.loads(contracts[1].read_text());write(out,'input_manifest.json',dict(cases=3,episodes_per_case=2,deformable_steps=16,newton_native_vbd_steps=0,controlled_steps=0,backend='Prepared-history failed-frame-safe, fraction-to-volume-boundary positive-tensile-curvature global candidate; unchanged physical source law/registry/collision',dt_s=dt,maximum_outer_iterations=40,maximum_cg_iterations=1000,cg_relative_tolerance=1e-9,cg_absolute_tolerance=1e-16,velocity_defect_budget_per_declared_duration_m_s=1e-6,declared_solver_duration_s=.1,freefall_position_budget_m=1e-10,freefall_velocity_budget_m_s=1e-8,replay_position_budget_m=1e-10,replay_velocity_budget_m_s=1e-8,global_contract=global_contract,local_contract=local_contract,scope='Integrator component and analytic freefall controls only. No sustained support, coupled robot, fracture or cutting qualification.'))
  for label,fixed,gravity,count in [('intact_fixture',np.array(data['design']['fixture']['node_ids']),(0.,0.,-9.81),2),('prepared_partial',np.array(data['design']['fixture']['node_ids']),(0.,0.,-9.81),4),('prepared_failed_free_cap',np.array(data['design']['fixture']['node_ids']),(0.,0.,-9.81),2)]:
   model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k);e=holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;s=GlobalImplicitCandidate(holder,data,fixed,gravity=gravity,velocity_defect_budget_m_s=1e-6);states=[s.state(),s.state()];ledger=FailedSafeLocalLedger(s,data,fixed,k,np.zeros(3));episodes=[];finals=[];cap=np.unique(data['cells'][data['x'][data['cells']].mean(1)[:,0]<data['design']['cut_x_m']]);initial_x=data['x'].copy();history=np.zeros((holder.pairs.shape[0],2));law=holder.objective_law.numpy()
   if label=='prepared_partial':initial_x[cap,0]-=.0005;history[:,0]=.0015;history[:,1]=law[:,2]*(.0015-law[:,1])/(.0015*(law[:,2]-law[:,1]))
   if label=='prepared_failed_free_cap':center=np.array([data['design']['cut_x_m'],0,.0295]);initial_x[cap]=(initial_x[cap]-center)@np.diag([1.,-1.,-1.])+center;initial_x[cap,0]-=.0045;history[:,0]=.0045;history[:,1]=1.
   for episode in range(2):
    for state in states:s.reset(state)
    for state in states:state.particle_q.assign(initial_x)
    holder.objective_history.assign(history);holder.history.assign(history.astype(np.float32));holder.eligible.zero_()
    ledger.reset();trace=[];start=time.monotonic();initial=ledger.measurements(states[0])['energy']['total_j']
    for i in range(count):
     if (out/'stop.request').exists():raise InterruptedError('Global integrator stop')
     try:s.step(states[i%2],states[1-i%2],None,None,dt)
     except BaseException:write(out,'nonlinear_failure_trace.json',dict(case=label,episode=episode,step=i,iterations=s.last_trace));raise
     state=states[1-i%2];steps+=1;x=state.particle_q.numpy();v=state.particle_qd.numpy();ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);row=dict(step=i,minimum_volume_ratio=float(ratios.min()),nonlinear_trace=s.last_trace)
     if not np.isfinite(x).all() or not np.isfinite(v).all() or ratios.min()<=.1 or not np.array_equal(holder.objective_history.numpy(),history) or not np.array_equal(holder.history.numpy(),history.astype(np.float32)) or holder.eligible.numpy().max() or not np.array_equal(x[fixed],data['x'][fixed]):raise ValueError('Invalid accepted global candidate state')
     if label=='prepared_failed_free_cap':
      expected_x=initial_x[cap].copy();expected_x[:,2]+=-9.81*dt*dt*(i+1)*(i+2)/2;expected_v=np.tile([0,0,-9.81*dt*(i+1)],(len(cap),1));pe=float(abs(x[cap]-expected_x).max());ve=float(abs(v[cap]-expected_v).max());row.update(analytic_cap_position_error_m=pe,analytic_cap_velocity_error_m_s=ve)
      if pe>1e-10 or ve>1e-8:raise ValueError('Prepared failed cap differs from independent rigid freefall')
     ledger.step(state,dt);audit=ledger.measurements(state);audit['energy_increase_j']=audit['energy']['total_j']-initial;row['ledger']=audit
     if audit['linear_impulse_residual_ns']>global_contract['linear_impulse_error_ns'] or audit['angular_impulse_residual_nms']>global_contract['angular_impulse_error_nms'] or audit['energy_increase_j']>global_contract['maximum_energy_increase_above_initial_j'] or audit['cumulative_absolute_nodal_impulse_residual_ns']>local_contract['cumulative_absolute_nodal_impulse_residual_ns']:raise ValueError('Global integrator independent force/energy budget failed')
     trace.append(row);write(out,'failed_safe_integrator_partial.json',dict(cases=cases,current_case=label,episode=episode,trace=trace,deformable_steps=steps))
    finals.append((x.copy(),v.copy()));episodes.append(dict(trace=trace,wall_s=time.monotonic()-start));np.savez(out/f'{label}_episode{episode}.npz',x=x,v=v)
   pe=float(abs(finals[0][0]-finals[1][0]).max());ve=float(abs(finals[0][1]-finals[1][1]).max())
   if pe>1e-10 or ve>1e-8:raise ValueError('Global candidate reset/replay failed')
   cases.append(dict(case=label,episodes=episodes,replay_position_error_m=pe,replay_velocity_error_m_s=ve))
  for state in states:s.reset(state)
  reset_energy=ledger.measurements(states[0])['energy']
  if holder.objective_history.numpy().max() or holder.history.numpy().max() or holder.eligible.numpy().max() or reset_energy['cohesion_stored_j'] or reset_energy['fracture_dissipated_j']:raise ValueError('Prepared failure reset retained history/energy')
  holder.eligible.fill_(1);before=states[0].particle_q.numpy().copy();rejected=False
  try:s.step(states[0],states[1],None,None,dt)
  except ValueError as exc:rejected='refuses live damage eligibility' in str(exc)
  holder.eligible.zero_()
  if not rejected or not np.array_equal(before,states[0].particle_q.numpy()) or holder.objective_history.numpy().max():raise ValueError('Unqualified live eligibility was not refused without advancing state/history')
  if steps!=16 or not sources_unchanged(pins):raise ValueError('Global step count/source closure changed')
  write(out,'failed_safe_integrator_measurements.json',dict(cases=cases,deformable_steps=steps,native_vbd_steps=0,scope='Sixteen prepared-history candidate steps: intact fixed fixture, existing partial damage under gravity, independently rotated fully failed cap with analytic freefall, strict replay/reset. Live eligibility is refused. No performed fracture, blade work, one-second release or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,failed_safe_integrator_passed=passed,newton_steps=0,deformable_steps=steps,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
