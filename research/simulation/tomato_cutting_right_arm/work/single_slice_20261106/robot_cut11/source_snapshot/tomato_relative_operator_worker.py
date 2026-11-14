"""Static force/energy, geometry reconstruction and admissibility reference audits."""
import argparse,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Relative operator audit stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  pins=capture_sources(out,[Path(__file__)])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_relative_kernels import reconstruct,relative_bulk,relative_predictor_check,relative_colored_step
  from tomato_native_volume_steps import apply_predictor
  from tomato_checked_volume_steps import finish_predictor,reject_unverified_predictor
  from tomato_bulk_reference import bulk_reference
  from tomato_collision_embedding import mapped_positions
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=np.array([0.,0.,.002]);model=build_relative_model(data);s=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data);engine=s.surface_contact=RelativeSurfaceContact(data,s.spatial_reference,margin=.0001);engine.physical_colors=model.particle_colors;u=wp.zeros(len(data['x']),dtype=wp.vec3);f=wp.zeros(len(data['x']),dtype=wp.vec3);h=wp.zeros(len(data['x']),dtype=wp.mat33);Q=Rotation.from_rotvec([.3,.4,-.2]).as_matrix();rng=np.random.default_rng(42);direction=rng.normal(size=data['x'].shape);direction/=np.linalg.norm(direction);color_ids=model.particle_colors.numpy()
  for label in ['rest','rotation','compression','nonaffine']:
   if (out/'stop.request').exists():raise InterruptedError('Stop before relative operator case')
   reference=data['x'];positions=reference.copy()
   if label=='rotation':positions=positions@Q.T+[.02,.03,.01]
   if label=='compression':positions=positions*np.array([.5,.7,.8])
   if label=='nonaffine':positions=positions@np.array([[1.,.004,.001],[.002,1.,-.001],[.001,.002,.99]]).T+rng.normal(size=positions.shape)*1e-8
   displacement=(positions-reference).astype(np.float32);u.assign(displacement);physical=reference+displacement.astype(float);wp.launch(reconstruct,dim=len(reference),inputs=[s.spatial_reference,u],outputs=[s.objective_x],block_dim=64);s.volume_invalid.zero_();wp.launch(relative_bulk,dim=len(reference),inputs=[-1,model.particle_colors,s.objective_x,s.spring_offsets,s.spring_ids,model.spring_indices,s.relative_spring_rest,s.relative_spring_k,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[s.volume_invalid,f,h],block_dim=64);wp.synchronize();expected=bulk_reference(physical,data);native=f.numpy().astype(float);native_h=h.numpy().astype(float);force_error=float(abs(native-expected['force']).max());block_error=float(abs(native_h-expected['blocks']).max());scale=float(abs(expected['force']).max());hscale=float(abs(expected['blocks']).max());reconstruction=float(abs(s.objective_x.numpy()-physical).max());step=1e-8;energy_plus=bulk_reference(physical+step*direction,data)['energy_j'];energy_minus=bulk_reference(physical-step*direction,data)['energy_j'];fd=-(energy_plus-energy_minus)/(2*step);work=float(np.sum(expected['force']*direction));work_error=abs(fd-work)
   if force_error>1e-6+1e-6*scale or block_error>1e-3+1e-6*hscale or reconstruction>1e-14 or work_error>1e-4+1e-5*max(abs(fd),abs(work)) or s.volume_invalid.numpy()[0]:raise ValueError('Relative bulk/reference mismatch '+str((label,force_error,block_error,work_error)))
   engine.invalid.zero_();engine.detect(u);engine.evaluate(u,1/2400);wp.synchronize();mapping_error=float(abs(engine.precise_position.numpy()-mapped_positions(physical,engine.embedding)).max());contact=engine.physical_force.numpy();contact_scale=float(np.linalg.norm(contact,axis=1).sum());balance=float(np.linalg.norm(contact.sum(0)));moment=float(np.linalg.norm(np.cross(physical,contact).sum(0)));peak=float(np.linalg.norm(contact,axis=1).max())
   if mapping_error>1e-14 or engine.invalid.numpy()[0] or balance>1e-8+1e-9*contact_scale or moment>1e-9+1e-10*contact_scale:raise ValueError('Relative contact embedding/reference mismatch')
   if label in ['rest','rotation'] and peak>1e-5:raise ValueError('Relative contact preload under rigid motion')
   if label=='rest' and scale>1e-8:raise ValueError('Reference rest has spring prestress')
   cases.append(dict(id=label,bulk_force_error_n=force_error,bulk_block_error_n_m=block_error,energy_directional_work_error_n=work_error,physical_reconstruction_error_m=reconstruction,proxy_mapping_error_m=mapping_error,contact_force_balance_n=balance,contact_moment_balance_nm=moment,contact_peak_n=peak,minimum_volume_ratio=expected['minimum_volume_ratio']));write(out,'relative_operator_partial.json',dict(cases=cases))
  # Simultaneous predictor contraction: prove the whole line remains admissible.
  baseline=wp.zeros(len(reference),dtype=wp.vec3);target=wp.array(reference*np.array([-.99,0.,0.]),dtype=wp.vec3);output=wp.zeros(len(reference),dtype=wp.vec3);s.volume_invalid.zero_();s.volume_step_fraction.fill_(1.);s.candidate_active.fill_(1)
  for _ in range(40):
   s.candidate_bad.zero_();wp.launch(relative_predictor_check,dim=s.cells.size,inputs=[s.spatial_reference,baseline,target,s.cells,s.volumes64,s.volume_step_fraction,s.candidate_active],outputs=[s.candidate_bad,s.volume_invalid],block_dim=64);wp.launch(finish_predictor,dim=1,inputs=[s.volume_step_fraction,s.candidate_active,s.candidate_bad])
  wp.launch(reject_unverified_predictor,dim=1,inputs=[s.volume_step_fraction,s.candidate_active,s.volume_invalid]);wp.launch(apply_predictor,dim=len(reference),inputs=[output,baseline,target,s.volume_step_fraction]);wp.synchronize();accepted=reference+output.numpy().astype(float);minimum=bulk_reference(accepted,data)['minimum_volume_ratio'];fraction=float(s.volume_step_fraction.numpy()[0])
  if s.volume_invalid.numpy()[0] or minimum<=.1 or not 0<fraction<1:raise ValueError('Relative predictor admitted unsafe contraction')
  cases.append(dict(id='predictor_contraction',accepted_fraction=fraction,minimum_volume_ratio=minimum))
  # One vertex would collapse a real tiny cell: colored checked update must stop it.
  u.zero_();delta=np.zeros_like(reference);cell=int(np.argmin(data['volumes']));tet=data['cells'][cell];node=int(tet[1]);delta[node]=-.99*(reference[node]-reference[tet[0]]);proposal=wp.array(delta,dtype=wp.vec3);s.volume_invalid.zero_();s.volume_clip_count.zero_();wp.launch(relative_colored_step,dim=len(reference),inputs=[int(color_ids[node]),model.particle_colors,s.spatial_reference,u,baseline,proposal,s.cell_offsets,s.cell_ids,s.cells,s.volumes64],outputs=[s.volume_invalid,s.volume_clip_count],block_dim=64);wp.synchronize();minimum=bulk_reference(reference+u.numpy().astype(float),data)['minimum_volume_ratio']
  if s.volume_invalid.numpy()[0] or minimum<=.1 or s.volume_clip_count.numpy()[0]==0:raise ValueError('Relative colored update admitted unsafe cell')
  cases.append(dict(id='colored_tiny_cell',cell=cell,node=node,minimum_volume_ratio=minimum,clipped_trials=int(s.volume_clip_count.numpy()[0])))
  if not sources_unchanged(pins):raise ValueError('Relative operator sources changed')
  write(out,'relative_operator_measurements.json',dict(cases=cases,source_unchanged=True,mechanical_triangle_count=model.tri_count,collision_triangle_count=engine.model.tri_count,scope='Rest-relative storage and float64 geometry: original bulk energy/gradient, declared diagonal solver blocks, complete contact mapping and safe-volume updates. Zero mechanical steps; no dynamic, cutting or experimental qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,relative_operator_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
