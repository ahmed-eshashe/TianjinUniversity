"""Independent full loaded-state energy-gradient audit; no dynamics advanced."""
import argparse,json,signal,subprocess,sys,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Loaded force audit stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  reference=ROOT/'rl/tomato_loaded_force_cpu_reference.py';stalled=ROOT/'runs/native/static_preparation_safeguarded_20261102_01/static_failure_state.npz';quarter=ROOT/'runs/native/global_hold_preview_20261102_01/episode0_final.npz';pins=capture_sources(out,[Path(__file__),reference],inputs=[stalled,quarter])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_board_support import nodal_plane_stiffness
  from tomato_static_gravity import StaticGravityCandidate
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');world_data=registry();world_data['x']+=[0,0,.002];origin=np.array([world_data['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world_data,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world_data);model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(holder,world_data,source_rest);e=holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;s=StaticGravityCandidate(holder,data,fixed,regularizer_s=1/2400);write(out,'input_manifest.json',dict(cases=2,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,force_absolute_budget_n=1e-8,force_relative_budget=1e-6,energy_absolute_budget_j=1e-10,energy_relative_budget=1e-9,scope='Independent CPU-autograd gradient of original full loaded potential; raw embedding scatter, no dynamics or equilibrium qualification.'))
  for label,path,load in [('stalled_static',stalled,.1),('quarter_gravity_state',quarter,1.)]:
   payload=np.load(path);x=payload['x_sim']
   if not np.array_equal(payload['world_from_sim_translation_m'],origin)or x.shape!=data['x'].shape or not np.isfinite(x).all():raise ValueError('Loaded diagnostic coordinate/input mismatch')
   s.set_load(load);xw=wp.array(x,dtype=wp.vec3d);s.force(xw,s.regularizer_s);G=s.energy(xw,s.regularizer_s);count=int(e.stencil_count.numpy()[0]);inputpath=out/f'{label}_inputs.npz';np.savez(inputpath,x=x,source_sim=data['x'],free=s.assembly.free.numpy(),mass=data['mass'],gravity=np.array([0.,0.,-9.81*load]),spring_pairs=data['springs'],spring_k=data['k'],spring_rest=holder.relative_spring_rest.numpy(),cells=data['cells'],volumes=data['volumes'],cohesive_pairs=holder.pairs.numpy(),cohesive_counts=holder.counts.numpy(),anchors=holder.objective_anchors.numpy(),sign=holder.objective_sign.numpy(),weights=holder.objective_weights.numpy(),local_k=holder.objective_stiffness.numpy(),history=holder.objective_history.numpy(),eligible=holder.eligible.numpy(),embedding_ids=e.indices.numpy(),embedding_weights=e.weights.numpy(),endpoint=e.endpoint.numpy()[:count],kind=e.kind.numpy()[:count],threshold=e.mollifier_threshold.numpy()[:count],radius=np.array([e.margin]),contact_k=np.array([e.model.soft_contact_ke]),board_k=holder.board_stiffness.numpy(),board_height=np.array([holder.board_height]),native_energy=np.array([G]),native_bulk_force=s.bulk_force.numpy(),native_cohesive_force=holder.objective_force.numpy(),native_contact_force=e.physical_force.numpy(),native_rhs=s.rhs.numpy());refout=out/f'{label}_reference.json'
   with(out/f'{label}_reference.log').open('w')as log:result=subprocess.run([sys.executable,str(reference),'--input',str(inputpath),'--output',str(refout)],stdout=log,stderr=subprocess.STDOUT,timeout=180,check=False)
   if result.returncode or not json.loads(refout.read_text())['passed']:raise ValueError('Independent loaded force/energy gradient failed '+label)
   cases.append(dict(case=label,reference=json.loads(refout.read_text())))
  if not sources_unchanged(pins):raise ValueError('Loaded force reference source changed')
  write(out,'loaded_force_measurements.json',dict(cases=cases,scope='Two posed full-registry independent potential gradients, including actual stalled static and 250 ms gravity configurations. No equilibrium, physical time, support or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,loaded_force_passed=passed,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
