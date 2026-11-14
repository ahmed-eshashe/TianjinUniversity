"""Intact gravity-preload preparation, with zero physical time advancement."""
import argparse,gzip,json,signal,time,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;stages=[];evaluations=0
 def stop(*a):raise InterruptedError('Gravity preload preparation stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  contract=ROOT/'runs/offline/integration_contract_20261102_10/contract.json';pins=capture_sources(out,[Path(__file__)],inputs=[contract])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_board_support import nodal_plane_stiffness
  from tomato_static_gravity import StaticGravityCandidate
  from tomato_failed_safe_ledger import FailedSafeLocalLedger
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');world_data=registry();world_data['x']+=[0,0,.002];origin=np.array([world_data['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world_data,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world_data);model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(holder,world_data,source_rest);e=holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;s=StaticGravityCandidate(holder,data,fixed,regularizer_s=1/2400);state=s.state();loads=[0.,.1,.25,.5,.75,1.];write(out,'input_manifest.json',dict(load_fractions=loads,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,maximum_static_iterations_per_load=2000,maximum_force_acceleration_m_s2=1e-5,force_l1_budget_n=1e-6,board_penetration_budget_m=.0001,maximum_source_displacement_m=.02,search_matrix_mass_regularizer_s=1/2400,search_regularizer_is_physical_inertia_or_damping=False,physical_damping=0.,friction=0.,world_from_sim_translation_m=origin.tolist(),scope='Explicit intact gravity equilibrium as a proposed new settled initial configuration. Original spring rest lengths, cell volumes, masses, constitutive/contact values, fixture nodes and free cap remain unchanged. Preparation iterations advance no physical time and do not pass a gravity transient, ten-second hold, time convergence, robot work or cutting gate.'))
  with gzip.open(out/'static_audit.jsonl.gz','wt',compresslevel=1)as stream:
   for load in loads:
    start=time.monotonic()
    def callback(row):
     nonlocal evaluations
     evaluations+=1;stream.write(json.dumps(row,separators=(',',':'))+'\n')
     if (out/'stop.request').exists():raise InterruptedError('Static checkpoint stop')
     if evaluations%24==0:
      stream.flush();write(out,'static_partial.json',dict(completed_loads=stages,current_load=load,last=row,residual_evaluations=evaluations))
     x=s.x.numpy();ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
     if ratios.min()<=.1 or not np.array_equal(x[fixed],data['x'][fixed]) or np.linalg.norm(x-data['x'],axis=1).max()>.02 or -(x[:,2]+origin[2]).min()>.0001 or holder.objective_history.numpy().max() or holder.eligible.numpy().max():raise ValueError('Static preload left unchanged geometry/history operating bounds')
    row=s.solve_load(state,load,maximum_outer=2000,force_l1_budget_n=1e-6,acceleration_budget_m_s2=1e-5,callback=callback);x=state.particle_q.numpy();stages.append(dict(load=load,final=row,wall_s=time.monotonic()-start,source_displacement_m=float(np.linalg.norm(x-data['x'],axis=1).max())));np.savez(out/f'load_{str(load).replace(".","_")}.npz',x_sim=x,x=x+origin,v=state.particle_qd.numpy(),world_from_sim_translation_m=origin);write(out,'static_partial.json',dict(completed_loads=stages,residual_evaluations=evaluations))
  s.force(state.particle_q,s.regularizer_s);x=state.particle_q.numpy();world=x+origin;mass=data['mass'];gravity=np.zeros_like(world);gravity[:,2]=-9.81*mass;board=np.zeros_like(world);board[:,2]=holder.board_stiffness.numpy()*np.maximum(-world[:,2],0);internal=s.bulk_force.numpy()+holder.objective_force.numpy()+e.physical_force.numpy();reaction=np.zeros_like(world);reaction[fixed]=-(gravity+board+internal)[fixed];forces=np.array([gravity.sum(0),board.sum(0),reaction.sum(0)]);moments=np.array([np.cross(world,gravity).sum(0),np.cross(world,board).sum(0),np.cross(world,reaction).sum(0)]);net_force=float(np.linalg.norm(forces.sum(0)));net_moment=float(np.linalg.norm(moments.sum(0)));residual=s.rhs.numpy();force_crosscheck=float(np.linalg.norm(forces.sum(0)-residual.sum(0)));moment_crosscheck=float(np.linalg.norm(moments.sum(0)-np.cross(world,residual).sum(0)))
  if net_force>1e-6 or net_moment>1e-7 or force_crosscheck>1e-8 or moment_crosscheck>1e-8 or not sources_unchanged(pins):raise ValueError('Independent static external force/moment/source check failed')
  ledger=FailedSafeLocalLedger(s,data,fixed,k,origin);energy=ledger.measurements(state)['energy'];np.savez(out/'prepared_equilibrium.npz',x_sim=x,x=world,v=np.zeros_like(world),world_from_sim_translation_m=origin,history=holder.objective_history.numpy(),mirror=holder.history.numpy(),eligible=holder.eligible.numpy(),fixture=fixed,reference_world=world_data['x']);write(out,'static_preparation_measurements.json',dict(stages=stages,residual_evaluations=evaluations,physical_time_advanced_s=0.,force_by_type_n=forces.tolist(),moment_by_type_nm=moments.tolist(),net_external_force_n=net_force,net_external_moment_nm=net_moment,force_crosscheck_n=force_crosscheck,moment_crosscheck_nm=moment_crosscheck,prestressed_physical_energy=energy,scope='Prepared intact equilibrium only; no physical transient/settling, stability/perturbation, ten-second support, time convergence, actual mounted work or cut qualification. The prepared configuration preserves original constitutive rest data and prestress; future episodes must identify/hash this initial condition explicitly.'));passed=True
 except BaseException:
  if 's'in locals() and 'np'in locals():
   try:np.savez(out/'static_failure_state.npz',x_sim=s.x.numpy(),force=s.rhs.numpy(),matrix_values=s.assembly.matrix.values.numpy(),matrix_columns=s.assembly.matrix.columns.numpy(),matrix_offsets=s.assembly.matrix.offsets.numpy(),world_from_sim_translation_m=origin);write(out,'static_failure_trace.json',dict(completed_loads=stages,iterations=s.last_trace))
   except BaseException:pass
  write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,regularized_static_preparation_passed=passed,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,load_stages_completed=len(stages),residual_evaluations=evaluations))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
