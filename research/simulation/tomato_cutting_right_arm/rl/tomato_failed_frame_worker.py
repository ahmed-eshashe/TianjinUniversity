"""Full-registry fully failed/rotating-frame safeguard operators; no cut."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Failed-frame operator stopped')
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
  from tomato_native_objective_reference import objective_force as old_force,incremental_objective_energy as old_energy,validate_frames as old_validate
  from tomato_failed_safe_objective import objective_force,incremental_objective_energy,validate_active_frames,commit_objective_history
  from tomato_cohesive_color_blocks import cohesive_color_blocks as old_blocks
  from tomato_failed_safe_blocks import failed_safe_cohesive_blocks
  from tomato_failed_safe_coupled import failed_safe_coupled_blocks
  from tomato_objective_cohesion_reference import make_patch
  from tomato_failed_cohesion_reference import released_safe_response,fracture_dissipation
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];rest=data['x'];model=build_relative_model(data);s=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data);e=RelativeSurfaceContact(data,s.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;zero=wp.zeros(len(rest),dtype=wp.vec3);left=np.unique(data['cells'][rest[data['cells']].mean(1)[:,0]<data['design']['cut_x_m']]);right=np.setdiff1d(np.arange(len(rest)),left);center=np.array([data['design']['cut_x_m'],0,.0295]);rot=np.diag([1.,-1.,-1.]);common=Rotation.from_rotvec([.2,.3,-.1]).as_matrix();patches=data['cohesion'].patches;law=s.objective_law.numpy();references=[]
  for p in patches:
   l=p['law'];references.append(make_patch(rest[data['pairs'][p['indices']]],p['weights'],p['stiffness'],(l.onset_m,l.failure_m,l.stiffness_n_m)))
  force=wp.zeros(len(rest),dtype=wp.vec3d);other_force=wp.zeros(len(rest),dtype=wp.vec3d);H=wp.zeros(len(rest),dtype=wp.mat33d);other_H=wp.zeros(len(rest),dtype=wp.mat33d);energy=wp.zeros(len(patches),dtype=wp.float64);other_energy=wp.zeros(len(patches),dtype=wp.float64);invalid=wp.zeros(1,dtype=int);write(out,'input_manifest.json',dict(cases=6,newton_steps=0,controlled_steps=0,force_reference_budget_n=1e-8,energy_reference_budget_j=1e-12,active_block_equivalence_budget_n_m=1e-8,full_failure_force_energy_blocks='exact zero without constructing a vanished material frame',scope='Prescribed geometry/history operators only. No performed fracture, physical free separation, robot or support qualification.'))
  full_history=None;closure=None
  for label in ['intact','partial_rotated','mixed_committed','failed_relative_rotation','failed_reclosure','reset']:
   if (out/'stop.request').exists():raise InterruptedError('Failed-frame stop')
   pos=rest.copy();history=np.zeros((len(patches),2));eligible=False
   if label in ['intact','partial_rotated','mixed_committed']:
    pos[right]+=[.0005,.0002,.0001]
    if label!='intact':history[:,0]=.0015;history[:,1]=law[:,2]*(.0015-law[:,1])/(.0015*(law[:,2]-law[:,1]))
    if label=='partial_rotated':pos=(pos-center)@common.T+center
    if label=='mixed_committed':history[::2,0]=.0045;history[::2,1]=1.
   if label=='failed_relative_rotation':
    s.reset_material();s.eligible.fill_(1);pre=rest.copy();pre[left,0]-=.0045;xpre=wp.array(pre,dtype=wp.vec3d);wp.launch(commit_objective_history,dim=len(patches),inputs=[xpre,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.eligible],outputs=[s.objective_history,s.history]);full_history=s.objective_history.numpy().copy()
    if not np.all(full_history[:,1]==1):raise ValueError('Prescribed native full failure did not commit')
   if label.startswith('failed_'):
    history=full_history.copy();pos[left]=(rest[left]-center)@rot.T+center;pos[left,0]+=(-.0045 if label=='failed_relative_rotation'else .00001);eligible=True
   if label=='reset':s.reset_material();pos=rest.copy()
   s.objective_history.assign(history);s.history.assign(history.astype(np.float32));s.eligible.fill_(int(eligible));x=wp.array(pos,dtype=wp.vec3d,requires_grad=True);invalid.zero_();wp.launch(validate_active_frames,dim=len(patches),inputs=[x,s.pairs,s.objective_anchors,s.objective_law,s.objective_history],outputs=[invalid]);force.zero_();other_force.zero_();H.zero_();other_H.zero_();common_inputs=[x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible];wp.launch(objective_force,dim=len(patches),inputs=common_inputs,outputs=[force]);wp.launch(incremental_objective_energy,dim=len(patches),inputs=common_inputs,outputs=[energy]);wp.launch(failed_safe_cohesive_blocks,dim=(len(patches),16),inputs=[-1,model.particle_colors,*common_inputs],outputs=[other_force,H]);reference_force=np.zeros_like(pos);reference_energy=[]
   for j,patch in enumerate(patches):
    ids=data['pairs'][patch['indices']];reference=released_safe_response(pos[ids],references[j],history=history[j],eligible=eligible);np.add.at(reference_force,ids.ravel(),reference['force_n'].reshape(-1,3));reference_energy.append(reference['incremental_potential_j'])
   fe=float(abs(force.numpy()-reference_force).max());ee=float(abs(energy.numpy()-reference_energy).max());fused=float(abs(force.numpy()-other_force.numpy()).max());ratios=np.linalg.det(pos[data['cells'][:,1:]]-pos[data['cells'][:,:1]])/(6*data['volumes']);row=dict(case=label,minimum_bulk_volume_ratio=float(ratios.min()),force_reference_error_n=fe,energy_reference_error_j=ee,fused_force_error_n=fused,active_frame_invalid=int(invalid.numpy()[0]))
   if ratios.min()<=.1 or fe>1e-8 or ee>1e-12 or fused>1e-8 or invalid.numpy()[0]:raise ValueError(('Failure-safe law mismatch',row))
   if label.startswith('failed_'):
    old_bad=wp.zeros(1,dtype=int);wp.launch(old_validate,dim=len(patches),inputs=[x,s.pairs,s.objective_anchors],outputs=[old_bad]);before=s.objective_history.numpy().copy();wp.launch(commit_objective_history,dim=len(patches),inputs=common_inputs[:8]+[s.eligible],outputs=[s.objective_history,s.history]);unchanged=bool(np.array_equal(before,s.objective_history.numpy()));count=len(patches)*256;rows=wp.empty(count,dtype=int);cols=wp.empty(count,dtype=int);values=wp.empty(count,dtype=wp.mat33d);wp.launch(failed_safe_coupled_blocks,dim=(len(patches),16,16),inputs=[0,*common_inputs,wp.ones(len(rest),dtype=int)],outputs=[rows,cols,values]);blockmax=float(abs(values.numpy()).max());e.reference=x;e.invalid.zero_();e.detect(zero);e.evaluate(zero,1/2400);contact=e.physical_force.numpy();net=float(contact[left,0].sum());row.update(old_frame_invalid=int(old_bad.numpy()[0]),history_preserved=unchanged,failed_diagonal_block_max=float(abs(H.numpy()).max()),failed_coupled_block_max=blockmax,closure_left_force_n=net,closure_invalid=int(e.invalid.numpy()[0]))
    if not unchanged or np.any(force.numpy())or np.any(energy.numpy())or np.any(H.numpy())or blockmax or e.invalid.numpy()[0]:raise ValueError('Failed interface retained traction or lost contact validity')
    if label=='failed_reclosure':
     if net>=-1e-4:raise ValueError('Failed interface lost normal reclosure contact')
     s.objective_history.zero_();e.evaluate(zero,1/2400);independence=float(abs(e.physical_force.numpy()-contact).max());s.objective_history.assign(history);row['closure_damage_independence_n']=independence
     if independence>1e-12:raise ValueError('Contact depends on vanished material damage')
   else:
    other_force.zero_();wp.launch(old_force,dim=len(patches),inputs=common_inputs,outputs=[other_force]);wp.launch(old_energy,dim=len(patches),inputs=common_inputs,outputs=[other_energy]);temp_force=wp.zeros(len(rest),dtype=wp.vec3d);wp.launch(old_blocks,dim=(len(patches),16),inputs=[-1,model.particle_colors,*common_inputs],outputs=[temp_force,other_H]);de=float(abs(H.numpy()-other_H.numpy()).max());row['old_active_block_error_n_m']=de
    if de>1e-8 or abs(force.numpy()-other_force.numpy()).max()>1e-8 or abs(energy.numpy()-other_energy.numpy()).max()>1e-12:raise ValueError('Active law changed under full-failure safeguard')
   cases.append(row);write(out,'failed_frame_partial.json',dict(cases=cases))
  # An active/partial interface with collapsed anchors is still unsupported.
  partial=full_history.copy();partial[:,0]=.0015;partial[:,1]=law[:,2]*(.0015-law[:,1])/(.0015*(law[:,2]-law[:,1]));s.objective_history.assign(partial);collapsed=rest.copy();collapsed[left]=(rest[left]-center)@rot.T+center;bad=wp.zeros(1,dtype=int);wp.launch(validate_active_frames,dim=len(patches),inputs=[wp.array(collapsed,dtype=wp.vec3d),s.pairs,s.objective_anchors,s.objective_law,s.objective_history],outputs=[bad])
  if not bad.numpy()[0]:raise ValueError('Partially attached collapsed frame was silently accepted')
  full_diss=float(fracture_dissipation(full_history,law).sum());budget=float(sum(p['law'].area_m2*p['law'].fracture_energy_j_m2 for p in patches))
  if abs(full_diss-budget)>1e-12 or not sources_unchanged(pins):raise ValueError('Fracture budget/source preservation failed')
  write(out,'failed_frame_measurements.json',dict(cases=cases,partial_collapsed_frame_rejected=True,full_fracture_dissipation_j=full_diss,unchanged_source_fracture_budget_j=budget,scope='Six full-registry prescribed interface operators, including proper independent 180-degree cap rotation and collapsed paired-midpoint frames after full failure. Active law/budget preserved; compression remains contact. Zero mechanical steps; no performed cut or free-release/support qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,failed_frame_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
