"""Independent held-load force/potential/ledger controls; no physical steps."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('External load controls stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  parent=ROOT/'runs/native/static_preparation_cached_20261102_01';prepared=parent/'prepared_equilibrium.npz';pins=capture_sources(out,[Path(__file__)],inputs=[prepared,parent/'supervisor_result.json'])
  import json
  if json.loads((parent/'supervisor_result.json').read_text())['passed'] is not True:raise ValueError('Prepared parent not qualified')
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from warp import sparse
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_board_support import nodal_plane_stiffness
  from tomato_external_load import ExternalLoadCandidate,ExternalLoadLedger,balanced_cap_field
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world);model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(holder,world,source_rest);holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);holder.surface_contact.physical_colors=model.particle_colors;s0=ExternalLoadCandidate(holder,data,fixed);s1=ExternalLoadCandidate(holder,data,fixed);pose=np.load(prepared)['x_sim'];free=s0.assembly.free.numpy().astype(bool);dt=1/2400;target=pose.copy();target[free,2]-=9.81*dt*dt;s0.target.assign(target);s1.target.assign(target);x=wp.array(pose,dtype=wp.vec3d);cap=np.array([n['side']=='slice'for n in data['design']['nodes']]);rng=np.random.default_rng(29);direction=rng.normal(size=pose.shape);direction[~free]=0;direction/=np.linalg.norm(direction);delta=np.zeros_like(pose);delta[cap]=[1e-7,-2e-7,3e-7];initial=s0.state();initial.particle_q.assign(pose);moved=s0.state();moved.particle_q.assign(pose+delta);moved.particle_qd.assign(delta/dt);ledger0=ExternalLoadLedger(s0,data,fixed,k,origin);ledger1=ExternalLoadLedger(s1,data,fixed,k,origin)
  write(out,'input_manifest.json',dict(cases=4,newton_steps=0,deformable_steps=0,controlled_steps=0,physical_time_advanced_s=0.,force_difference_budget_n=1e-10,energy_difference_budget_j=1e-12,matrix_action_difference_budget_n=1e-8,load_channel_impulse_budget_ns=1e-12,load_channel_moment_budget_nms=1e-12,load_work_budget_j=1e-14,finite_external_work_derivative_budget_n=1e-8,scope='Synthetic held-load operator and ledger controls on qualified intact prestress. Manufactured motion is NOT integrated/accepted physics. No load stability or robot/cut qualification.'))
  for label,F,M in [('clear',[0,0,0],[0,0,0]),('down',[0,0,-.01],[0,0,0]),('lateral_twist',[-.01,0,0],[0,1e-4,0]),('reversed',[.01,0,0],[0,-1e-4,0])]:
   field,center=balanced_cap_field(pose,data['mass'],cap,F,M);s0.set_load(np.zeros_like(field));s1.set_load(field);s0.force(x,dt);f0=s0.rhs.numpy();E0=s0.energy(x,dt);s1.force(x,dt);f1=s1.rhs.numpy();E1=s1.energy(x,dt);fe=float(abs(f1-f0-field).max());ee=float(abs(E1-E0+np.sum(field*(pose-data['x']))));s0.assembly.assemble(x,dt);v=wp.array(direction*1e-7,dtype=wp.vec3d);a0=wp.zeros(s0.n,dtype=wp.vec3d);sparse.bsr_mv(s0.assembly.matrix,v,a0);s1.force(x,dt);s1.assembly.assemble(x,dt);a1=wp.zeros(s0.n,dtype=wp.vec3d);sparse.bsr_mv(s1.assembly.matrix,v,a1);ae=float(abs(a1.numpy()-a0.numpy()).max());eps=1e-7;effects=[]
   for sign in [1,-1]:
    trial=wp.array(pose+sign*eps*direction,dtype=wp.vec3d);effects.append(s1.energy(trial,dt,trial=True)-s0.energy(trial,dt,trial=True))
   derivative=float(abs(-(effects[0]-effects[1])/(2*eps)-np.sum(field*direction)));ledger0.reset(initial);ledger1.reset(initial);ledger0.step(moved,dt);ledger1.step(moved,dt);record=ledger1.measurements(moved);impulse=float(np.linalg.norm(ledger1.impulse.numpy()[3]-dt*field.sum(0)));moment=float(np.linalg.norm(ledger1.angular.numpy()[3]-dt*np.cross(pose+delta+origin,field).sum(0)));work=float(abs(record['prescribed_load_work_j']-np.sum(field*delta)));balance=float(abs(record['energy_less_prescribed_work_j']-(record['energy']['total_j']-np.sum(field*delta))))
   state=s1.state();state.particle_q.assign(pose);s1.reset(state);ledger1.reset(state);reset=bool(not np.any(s1.external_force.numpy())and not np.any(ledger1.impulse.numpy())and not np.any(ledger1.angular.numpy())and ledger1.load_work.numpy()[0]==0 and not np.any(holder.objective_history.numpy())and not np.any(holder.eligible.numpy()))
   row=dict(case=label,force_difference_error_n=fe,energy_difference_error_j=ee,matrix_action_difference_n=ae,finite_external_work_derivative_error_n=derivative,external_impulse_error_ns=impulse,external_moment_error_nms=moment,held_load_work_error_j=work,physical_energy_minus_work_error_j=balance,reset_clear=reset,net_force_n=field.sum(0).tolist(),net_moment_about_prepared_cap_centroid_nm=np.cross(pose-center,field).sum(0).tolist())
   if not np.isfinite([fe,ee,ae,derivative,impulse,moment,work,balance]).all()or fe>1e-10 or ee>1e-12 or ae>1e-8 or derivative>1e-8 or impulse>1e-12 or moment>1e-12 or work>1e-14 or balance>1e-14 or not reset:raise ValueError(row)
   cases.append(row)
  if not sources_unchanged(pins):raise ValueError('Held-load source changed')
  write(out,'external_load_measurements.json',dict(cases=cases,scope='Four full-registry held force/moment, force/potential, matrix independence, manufactured-motion impulse/angular/work ledgers and reset controls. ZERO physical steps. No actual dynamic load challenge, support, mounted work or cut pass.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,external_load_operator_passed=passed,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
