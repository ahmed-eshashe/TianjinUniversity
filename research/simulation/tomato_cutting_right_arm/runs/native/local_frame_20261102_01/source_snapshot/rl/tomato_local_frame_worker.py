"""Coordinate-translation force/energy/ledger controls, zero mechanical steps."""
import argparse,json,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Local coordinate check stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  captured=ROOT/'runs/native/rebased_local_preflight_20261102_01/first_bad_update.npz';pins=capture_sources(out,[Path(__file__)],inputs=[captured])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_board_support import nodal_plane_stiffness
  from tomato_global_implicit import GlobalImplicitCandidate
  from tomato_global_ledger import GlobalSupportLedger
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_local_frame_ledger import LocalFrameSupportLedger
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];origin=np.array([data['design']['cut_x_m'],0,.0295]);local,source_rest=translated_registry(data,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(data);dt=1/2400
  def build(d,height):
   model=build_relative_model(d,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,d,iterations=1,solver_class=RelativeObjectiveVBD),d,board_stiffness=k,board_height=height);retain_canonical_material(holder,data,source_rest);e=holder.surface_contact=RelativeSurfaceContact(d,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;return GlobalImplicitCandidate(holder,d,fixed)
  world_solver=build(data,0.);local_solver=build(local,-origin[2]);wl=GlobalSupportLedger(world_solver,data,fixed,k);ll=LocalFrameSupportLedger(local_solver,local,fixed,k,origin);write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,world_from_sim_translation_m=origin.tolist(),force_absolute_budget_n=1e-8,force_relative_budget=1e-8,energy_absolute_budget_j=1e-10,energy_relative_budget=1e-9,ledger_impulse_budget_ns=1e-10,ledger_energy_budget_j=1e-10,scope='Pure simulation-frame translation. Canonical spring rest lengths, masses, stiffnesses, cell volumes, source design, fixture IDs and physical board retained. No integration or support pass.'))
  for label,x in [('rest',data['x'].copy()),('affine',data['x']@np.array([[.74,.015,0],[0,.76,.01],[0,0,.85]]).T),('captured_contact',np.load(captured)['x'])]:
   target=x.copy();target[:,2]-=9.81*dt*dt;target[fixed]=x[fixed];world_solver.target.assign(target);local_solver.target.assign(target-origin);xw=wp.array(x,dtype=wp.vec3d);xl=wp.array(x-origin,dtype=wp.vec3d);world_solver.force(xw,dt);Ew=world_solver.energy(xw,dt);Fw=world_solver.rhs.numpy();local_solver.force(xl,dt);El=local_solver.energy(xl,dt);Fl=local_solver.rhs.numpy();absolute=float(abs(Fw-Fl).max());relative=float(np.linalg.norm(Fw-Fl)/max(np.linalg.norm(Fw),1e-20));ee=float(abs(Ew-El));er=ee/max(abs(Ew),abs(El),1e-12)
   if not (absolute<=1e-8 or relative<=1e-8)or not(ee<=1e-10 or er<=1e-9):raise ValueError(('Translated force/potential differs',label,absolute,relative,ee,er))
   ws=world_solver.state();ls=local_solver.state();ws.particle_q.assign(x);ls.particle_q.assign(x-origin);velocity=np.random.default_rng(58).normal(size=x.shape)*.001;velocity[fixed]=0;ws.particle_qd.assign(velocity);ls.particle_qd.assign(velocity);wl.reset();ll.reset();wl.step(ws,dt);ll.step(ls,dt);wa=wl.measurements(ws);la=ll.measurements(ls);ie=max(float(abs(np.asarray(wa[key])-np.asarray(la[key])).max())for key in ['gravity_board_fixture_impulse_ns','gravity_board_fixture_angular_impulse_nms']);le=float(abs(wa['energy']['total_j']-la['energy']['total_j']))
   if ie>1e-10 or le>1e-10:raise ValueError('Translated world ledger differs')
   cases.append(dict(case=label,force_absolute_error_n=absolute,force_relative_error=relative,energy_absolute_error_j=ee,energy_relative_error=er,world_ledger_impulse_error_ns=ie,world_ledger_energy_error_j=le))
  if not sources_unchanged(pins):raise ValueError('Coordinate-check sources changed')
  write(out,'local_frame_measurements.json',dict(cases=cases,world_from_sim_translation_m=origin.tolist(),scope='Three prescribed full-model world/local force, incremental potential and world-ledger comparisons. Physical source parameters and board unchanged. Zero mechanical steps, no support/replay or cut claim.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,local_frame_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
